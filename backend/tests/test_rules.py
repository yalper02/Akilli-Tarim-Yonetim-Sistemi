"""
Kural motoru testleri — evaluate_rules_task, koşul değerlendirme, hava durumu kısıtlaması.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.commands.models import Command
from apps.devices.models import Device
from apps.farms.models import Crop, Farm
from apps.rules.models import Rule, RuleAction, RuleCondition, RuleWeatherConstraint
from apps.rules.tasks import _apply_operator, _evaluate_conditions, evaluate_rules_task
from apps.sensor_data.models import SensorReading

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db):
    return User.objects.create_superuser(username="rule_tester", password="pass")


@pytest.fixture
def crop(db):
    return Crop.objects.create(
        name="Domates",
        optimal_soil_moisture_min=40.0,
        optimal_soil_moisture_max=70.0,
        optimal_temperature_min=15.0,
        optimal_temperature_max=35.0,
        irrigation_water_need_mm_per_day=5.0,
        optimal_ph_min=6.0,
        optimal_ph_max=7.0,
        nitrogen_need_ppm=150.0,
        phosphorus_need_ppm=30.0,
        potassium_need_ppm=200.0,
    )


@pytest.fixture
def farm(db, user, crop):
    return Farm.objects.create(
        name="Test Çiftliği",
        latitude=37.0,
        longitude=35.0,
        owner=user,
        crop=crop,
    )


@pytest.fixture
def sensor(db, farm):
    return Device.objects.create(
        farm=farm,
        name="Toprak Sensörü",
        device_uid="sensor-test-001",
        device_type=Device.SENSOR,
        status=Device.ONLINE,
    )


@pytest.fixture
def valve(db, farm):
    return Device.objects.create(
        farm=farm,
        name="Sulama Vanası",
        device_uid="valve-test-001",
        device_type=Device.ACTUATOR,
        status=Device.ONLINE,
    )


@pytest.fixture
def rule(db, farm, user, valve):
    """soil_moisture < 30.0 → open_valve kuralı."""
    r = Rule.objects.create(farm=farm, name="Düşük Nem Sulama", is_active=True, created_by=user)
    RuleCondition.objects.create(
        rule=r, capability_type="soil_moisture", operator="lt", threshold_value=30.0
    )
    RuleAction.objects.create(
        rule=r,
        action_type=RuleAction.OPEN_VALVE,
        device=valve,
        parameters={"duration_seconds": 1800},
    )
    return r


def _reading(sensor, value=25.0, capability="soil_moisture"):
    return SensorReading.objects.create(
        time=timezone.now(), device=sensor, capability_type=capability, value=value
    )


# ---------------------------------------------------------------------------
# _apply_operator birimleri
# ---------------------------------------------------------------------------


class TestApplyOperator:
    def test_lt_true(self):
        assert _apply_operator("lt", 25.0, 30.0) is True

    def test_lt_false(self):
        assert _apply_operator("lt", 35.0, 30.0) is False

    def test_lte_equal(self):
        assert _apply_operator("lte", 30.0, 30.0) is True

    def test_gt_true(self):
        assert _apply_operator("gt", 35.0, 30.0) is True

    def test_gte_equal(self):
        assert _apply_operator("gte", 30.0, 30.0) is True

    def test_eq_true(self):
        assert _apply_operator("eq", 30.0, 30.0) is True

    def test_ne_true(self):
        assert _apply_operator("ne", 25.0, 30.0) is True

    def test_unknown_operator_returns_false(self):
        assert _apply_operator("xx", 1.0, 2.0) is False


# ---------------------------------------------------------------------------
# _evaluate_conditions birimleri
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEvaluateConditions:
    def test_single_condition_met(self, rule, sensor):
        reading = _reading(sensor, value=25.0)  # 25 < 30 → True
        assert _evaluate_conditions(rule, reading) is True

    def test_single_condition_not_met(self, rule, sensor):
        reading = _reading(sensor, value=40.0)  # 40 < 30 → False
        assert _evaluate_conditions(rule, reading) is False

    def test_missing_value_returns_false(self, rule, sensor):
        # temperature koşulu ekliyoruz ama sensörden hiç temperature okuma yok
        RuleCondition.objects.create(
            rule=rule, capability_type="temperature", operator="gt", threshold_value=10.0
        )
        reading = _reading(sensor, value=25.0, capability="soil_moisture")
        assert _evaluate_conditions(rule, reading) is False

    def test_multi_condition_all_met(self, rule, sensor, farm, user, valve):
        """İki koşulun ikisi de sağlandığında True döner."""
        RuleCondition.objects.create(
            rule=rule, capability_type="temperature", operator="gt", threshold_value=10.0
        )
        # Temperature okuma ekle (20 > 10 → True)
        SensorReading.objects.create(
            time=timezone.now(), device=sensor, capability_type="temperature", value=20.0
        )
        reading = _reading(sensor, value=25.0)  # soil_moisture 25 < 30 → True
        assert _evaluate_conditions(rule, reading) is True

    def test_multi_condition_one_fails(self, rule, sensor):
        """Koşullardan biri başarısız olursa False döner."""
        RuleCondition.objects.create(
            rule=rule, capability_type="temperature", operator="gt", threshold_value=10.0
        )
        # Temperature okuma: 5 > 10 → False
        SensorReading.objects.create(
            time=timezone.now(), device=sensor, capability_type="temperature", value=5.0
        )
        reading = _reading(sensor, value=25.0)
        assert _evaluate_conditions(rule, reading) is False


# ---------------------------------------------------------------------------
# evaluate_rules_task — tam entegrasyon testleri
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEvaluateRulesTask:
    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_rule_fires_when_condition_met(self, mock_pub, rule, sensor):
        """Koşul sağlandığında komut oluşturulur ve MQTT'ye gönderilir."""
        reading = _reading(sensor, value=25.0)
        evaluate_rules_task(reading.pk)

        cmd = Command.objects.filter(rule=rule).first()
        assert cmd is not None
        assert cmd.action_type == Command.OPEN_VALVE
        assert cmd.triggered_by == Command.AUTOMATIC
        mock_pub.assert_called_once()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_rule_skips_when_condition_not_met(self, mock_pub, rule, sensor):
        """Koşul sağlanmadığında komut oluşturulmaz."""
        reading = _reading(sensor, value=45.0)  # 45 < 30 → False
        evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 0
        mock_pub.assert_not_called()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_inactive_rule_is_skipped(self, mock_pub, rule, sensor):
        """is_active=False olan kural tetiklenmez."""
        rule.is_active = False
        rule.save()
        reading = _reading(sensor, value=25.0)
        evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 0
        mock_pub.assert_not_called()

    def test_nonexistent_reading_does_not_raise(self):
        """Var olmayan reading_id için görev sessizce sonlanır."""
        evaluate_rules_task(999999)  # exception olmamalı

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_weather_constraint_cancels_when_rain_high(self, mock_pub, rule, farm, sensor):
        """Yağış olasılığı eşiği aştığında kural iptal edilir, komut oluşturulmaz."""
        RuleWeatherConstraint.objects.create(
            rule=rule, max_rain_probability_pct=70, check_hours_ahead=24
        )
        reading = _reading(sensor, value=25.0)

        # Yağış %80 → iptal
        with patch("apps.weather.services.get_max_rain_probability", return_value=80):
            evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 0
        mock_pub.assert_not_called()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_weather_constraint_allows_when_rain_low(self, mock_pub, rule, farm, sensor):
        """Yağış olasılığı eşiğin altındaysa kural tetiklenir."""
        RuleWeatherConstraint.objects.create(
            rule=rule, max_rain_probability_pct=70, check_hours_ahead=24
        )
        reading = _reading(sensor, value=25.0)

        # Yağış %30 → devam et
        with patch("apps.weather.services.get_max_rain_probability", return_value=30):
            evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 1
        mock_pub.assert_called_once()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_weather_unavailable_does_not_cancel(self, mock_pub, rule, farm, sensor):
        """Hava durumu alınamazsa (None) kural iptal edilmez — güvenli taraf sulamak."""
        RuleWeatherConstraint.objects.create(
            rule=rule, max_rain_probability_pct=70, check_hours_ahead=24
        )
        reading = _reading(sensor, value=25.0)

        with patch("apps.weather.services.get_max_rain_probability", return_value=None):
            evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 1

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_recently_fired_guard_prevents_double(self, mock_pub, rule, sensor, valve):
        """Son 5 dakika içinde aynı kural+cihaz için komut varsa tekrar tetiklenmez."""
        # Önceden gönderilmiş bir komut oluştur
        Command.objects.create(
            device=valve,
            rule=rule,
            action_type=Command.OPEN_VALVE,
            triggered_by=Command.AUTOMATIC,
            status=Command.EXECUTED,
            issued_at=timezone.now() - timedelta(minutes=2),
        )
        reading = _reading(sensor, value=25.0)
        evaluate_rules_task(reading.pk)

        # Yeni komut oluşturulmamalı
        assert Command.objects.filter(rule=rule).count() == 1
        mock_pub.assert_not_called()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_recently_fired_guard_allows_after_cooldown(self, mock_pub, rule, sensor, valve):
        """5 dakika geçmişse kural tekrar tetiklenebilir."""
        Command.objects.create(
            device=valve,
            rule=rule,
            action_type=Command.OPEN_VALVE,
            triggered_by=Command.AUTOMATIC,
            status=Command.EXECUTED,
            issued_at=timezone.now() - timedelta(minutes=10),
        )
        reading = _reading(sensor, value=25.0)
        evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=rule).count() == 2
        mock_pub.assert_called_once()

    @patch("apps.commands.services._publish_mqtt", return_value=True)
    def test_multi_action_rule_publishes_all_commands(self, mock_pub, farm, user, sensor, valve):
        """Birden fazla aksiyonu olan kural hepsini yayınlar."""
        valve2 = Device.objects.create(
            farm=farm, name="Vana 2", device_uid="valve-test-002", device_type=Device.ACTUATOR
        )
        r = Rule.objects.create(
            farm=farm, name="Çok Aksiyonlu Kural", is_active=True, created_by=user
        )
        RuleCondition.objects.create(
            rule=r, capability_type="soil_moisture", operator="lt", threshold_value=30.0
        )
        # İki farklı vanaya aksiyon
        RuleAction.objects.create(
            rule=r, action_type=RuleAction.OPEN_VALVE, device=valve, priority=0
        )
        RuleAction.objects.create(
            rule=r, action_type=RuleAction.OPEN_VALVE, device=valve2, priority=1
        )

        reading = _reading(sensor, value=25.0)
        evaluate_rules_task(reading.pk)

        assert Command.objects.filter(rule=r).count() == 2
        assert mock_pub.call_count == 2
