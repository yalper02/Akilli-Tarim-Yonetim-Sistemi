"""
Kural motoru Celery görevi.
Sensör okuması geldiğinde koşulları değerlendirir,
hava durumu kısıtlamasını kontrol eder ve MQTT komutu yayınlar.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

logger = logging.getLogger(__name__)


def _apply_operator(operator: str, value: float, threshold: float) -> bool:
    """Karşılaştırma operatörünü uygular."""
    ops = {
        "lt": lambda v, t: v < t,
        "lte": lambda v, t: v <= t,
        "gt": lambda v, t: v > t,
        "gte": lambda v, t: v >= t,
        "eq": lambda v, t: v == t,
        "ne": lambda v, t: v != t,
    }
    fn = ops.get(operator)
    return fn(value, threshold) if fn else False


def _get_latest_value(farm_id: int, capability_type: str, current_reading=None) -> float | None:
    """
    Çiftlik için belirtilen capability'nin en son değerini döner.
    Tetikleyici okuma için mevcut değeri kullanır (DB sorgusu yapmaz).
    """
    from apps.sensor_data.models import SensorReading

    if current_reading and current_reading.capability_type == capability_type:
        return current_reading.value

    reading = (
        SensorReading.objects.filter(device__farm_id=farm_id, capability_type=capability_type)
        .order_by("-time")
        .first()
    )
    return reading.value if reading else None


def _evaluate_conditions(rule, current_reading) -> bool:
    """
    Kural koşullarını AND mantığıyla değerlendirir.
    Herhangi bir koşul için güncel değer bulunamazsa False döner.
    """
    for condition in rule.conditions.all():
        value = _get_latest_value(rule.farm_id, condition.capability_type, current_reading)
        if value is None:
            logger.debug(
                "Koşul için değer yok — kural pas geçildi: rule=%s capability=%s",
                rule.pk,
                condition.capability_type,
            )
            return False
        if not _apply_operator(condition.operator, value, condition.threshold_value):
            return False
    return True


def _rain_would_cancel(rule, farm) -> bool:
    """
    Hava durumu kısıtlaması varsa yağmur olasılığını kontrol eder.
    Kısıtlama yoksa veya hava durumu alınamazsa False döner (sulama iptal edilmez).
    """
    from apps.weather.services import get_max_rain_probability

    try:
        wc = rule.weather_constraint
    except ObjectDoesNotExist:
        return False

    max_prob = get_max_rain_probability(farm, wc.check_hours_ahead)
    if max_prob is None:
        # Hava durumu alınamadı — güvenli taraf: iptal etme, sula
        logger.warning("Hava durumu alınamadı, kısıtlama uygulanmıyor: rule=%s", rule.pk)
        return False

    if max_prob > wc.max_rain_probability_pct:
        logger.info(
            "Yağmur kısıtlaması tetiklendi: rule=%s max_rain_prob=%s threshold=%s",
            rule.pk,
            max_prob,
            wc.max_rain_probability_pct,
        )
        return True
    return False


def _already_fired_recently(rule, action_device, minutes: int = 5) -> bool:
    """
    Son N dakika içinde aynı kural + cihaz için aktif komut var mı?
    Aynı kuralın kısa sürede birden fazla kez tetiklenmesini önler.
    """
    from apps.commands.models import Command

    cutoff = timezone.now() - timedelta(minutes=minutes)
    return Command.objects.filter(
        rule=rule,
        device=action_device,
        status__in=[Command.PENDING, Command.RECEIVED, Command.EXECUTED],
        issued_at__gte=cutoff,
    ).exists()


@shared_task(bind=True, max_retries=3, default_retry_delay=10, ignore_result=True)
def evaluate_rules_task(self, reading_id: int) -> None:
    """
    Yeni bir sensör okuması için aktif kuralları değerlendirir.
    Koşullar sağlanıyorsa hava durumu kısıtlamasını kontrol eder,
    geçerse MQTT komutu yayınlar ve denetim günlüğüne yazar.
    """
    from apps.audit.services import write_audit_log
    from apps.commands.services import publish_command
    from apps.rules.models import Rule
    from apps.sensor_data.models import SensorReading

    try:
        reading = SensorReading.objects.select_related("device__farm").get(pk=reading_id)
    except SensorReading.DoesNotExist:
        logger.warning("Okuma bulunamadı, kural değerlendirmesi atlandı: reading_id=%s", reading_id)
        return

    device = reading.device
    farm = device.farm

    # Bu capability ile ilgili en az bir koşulu olan, aktif tüm çiftlik kuralları
    rules = (
        Rule.objects.filter(
            farm=farm,
            is_active=True,
            conditions__capability_type=reading.capability_type,
        )
        .select_related("weather_constraint")
        .prefetch_related("conditions", "actions", "actions__device")
        .distinct()
    )

    for rule in rules:
        # 1. Tüm koşulları AND olarak değerlendir
        if not _evaluate_conditions(rule, reading):
            continue

        logger.info(
            "Kural koşulları sağlandı: rule=%s farm=%s capability=%s value=%.2f",
            rule.pk,
            farm.pk,
            reading.capability_type,
            reading.value,
        )

        # 2. Hava durumu kısıtlaması — yağmur beklentisi varsa iptal et
        if _rain_would_cancel(rule, farm):
            write_audit_log(
                action_type="rule_cancelled_weather",
                resource_type="rule",
                resource_id=rule.pk,
                details={
                    "farm_id": farm.pk,
                    "reading_id": reading_id,
                    "capability_type": reading.capability_type,
                    "value": reading.value,
                },
            )
            continue

        # 3. Her aksiyon için komut yayınla
        for action in rule.actions.all():
            if _already_fired_recently(rule, action.device):
                logger.info(
                    "Son 5 dk içinde zaten tetiklendi, atlandı: rule=%s device=%s",
                    rule.pk,
                    action.device.device_uid,
                )
                continue

            cmd = publish_command(
                device=action.device,
                action_type=action.action_type,
                parameters=action.parameters,
                rule=rule,
            )
            logger.info(
                "Komut yayınlandı: rule=%s action=%s device=%s cmd_uid=%s",
                rule.pk,
                action.action_type,
                action.device.device_uid,
                cmd.command_uid,
            )
            write_audit_log(
                action_type="rule_command_issued",
                resource_type="command",
                resource_id=cmd.pk,
                details={
                    "rule_id": rule.pk,
                    "farm_id": farm.pk,
                    "device_uid": action.device.device_uid,
                    "action_type": action.action_type,
                    "reading_id": reading_id,
                    "capability_type": reading.capability_type,
                    "value": reading.value,
                    "command_status": cmd.status,
                },
            )
