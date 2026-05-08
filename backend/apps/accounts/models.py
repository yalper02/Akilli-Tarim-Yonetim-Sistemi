from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "users"


class Role(models.Model):
    FARMER = "farmer"
    FARM_MANAGER = "farm_manager"
    SYSTEM_ADMIN = "system_admin"
    ROLE_CHOICES = [
        (FARMER, "Çiftçi"),
        (FARM_MANAGER, "Tarım Yöneticisi"),
        (SYSTEM_ADMIN, "Sistem Yöneticisi"),
    ]

    name = models.CharField(max_length=30, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        db_table = "roles"


class FarmMembership(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="memberships")
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "farm_memberships"
        unique_together = [("user", "farm")]
