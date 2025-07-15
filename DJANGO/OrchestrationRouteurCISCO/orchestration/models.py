from django.contrib.auth.models import AbstractUser
from django.db import models


# Router model representing a network device
class Router(models.Model):
    hostname = models.CharField(max_length=100, default="Unknown")
    device_type = models.CharField(max_length=100, default="Unknown")
    ip_address = models.GenericIPAddressField(unique=True)
    username = models.CharField(max_length=100, default="Unknown")
    password = models.CharField(max_length=100, default="Unknown")
    enable_password = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


# Custom user model with role support
class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("normal", "Normal"),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default="normal")


# Interface model representing a router interface
class Interface(models.Model):
    router = models.ForeignKey("Router", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=39)
    status = models.CharField(
        max_length=100,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("up", "Up"),
            ("down", "Down"),
            ("deleted", "Deleted"),
        ],
        default="active",
    )

    def __str__(self):
        return f"{self.name} ({self.ip_address} / {self.subnet_mask})"


# Log model for tracking user actions on routers
class Log(models.Model):
    router = models.ForeignKey("Router", on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.router.hostname} - {self.action} - {self.user.username if self.user else 'System'}"
