import uuid

from django.conf import settings
from django.db import models


class Command(models.Model):
    PENDING = "pending"
    RECEIVED = "received"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (RECEIVED, "Received"),
        (EXECUTED, "Executed"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled"),
    ]
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    TRIGGERED_BY_CHOICES = [
        (AUTOMATIC, "Automatic"),
        (MANUAL, "Manual"),
    ]
    OPEN_VALVE = "open_valve"
    CLOSE_VALVE = "close_valve"
    DISPENSE_FERTILIZER = "dispense_fertilizer"
    ACTION_TYPE_CHOICES = [
        (OPEN_VALVE, "Open Valve"),
        (CLOSE_VALVE, "Close Valve"),
        (DISPENSE_FERTILIZER, "Dispense Fertilizer"),
    ]

    command_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="commands")
    rule = models.ForeignKey(
        "rules.Rule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commands",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commands",
    )
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    triggered_by = models.CharField(max_length=15, choices=TRIGGERED_BY_CHOICES)
    issued_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.action_type} → {self.device} ({self.status})"

    class Meta:
        db_table = "commands"
        constraints = [
            # XOR: either rule-triggered OR user-triggered, never both or neither
            models.CheckConstraint(
                check=(
                    models.Q(rule__isnull=False, user__isnull=True)
                    | models.Q(rule__isnull=True, user__isnull=False)
                ),
                name="commands_either_rule_or_user",
            )
        ]
