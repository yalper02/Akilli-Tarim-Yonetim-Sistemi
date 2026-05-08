from django.conf import settings
from django.db import models


class Rule(models.Model):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_rules",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "rules"


class RuleCondition(models.Model):
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    EQ = "eq"
    NE = "ne"
    OPERATOR_CHOICES = [
        (LT, "<"),
        (LTE, "<="),
        (GT, ">"),
        (GTE, ">="),
        (EQ, "="),
        (NE, "!="),
    ]

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="conditions")
    capability_type = models.CharField(max_length=30)
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES)
    threshold_value = models.FloatField()

    class Meta:
        db_table = "rule_conditions"


class RuleAction(models.Model):
    OPEN_VALVE = "open_valve"
    CLOSE_VALVE = "close_valve"
    DISPENSE_FERTILIZER = "dispense_fertilizer"
    ACTION_TYPE_CHOICES = [
        (OPEN_VALVE, "Open Valve"),
        (CLOSE_VALVE, "Close Valve"),
        (DISPENSE_FERTILIZER, "Dispense Fertilizer"),
    ]

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    device = models.ForeignKey(
        "devices.Device", on_delete=models.CASCADE, related_name="rule_actions"
    )
    parameters = models.JSONField(default=dict, blank=True)
    priority = models.IntegerField(default=0)

    class Meta:
        db_table = "rule_actions"
        ordering = ["priority"]


class RuleWeatherConstraint(models.Model):
    # 1:0..1 with Rule — cancels irrigation when rain probability exceeds threshold
    rule = models.OneToOneField(Rule, on_delete=models.CASCADE, related_name="weather_constraint")
    max_rain_probability_pct = models.IntegerField(default=70)
    check_hours_ahead = models.IntegerField(default=24)

    class Meta:
        db_table = "rule_weather_constraints"
