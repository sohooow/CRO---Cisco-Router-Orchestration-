from django.contrib.auth.models import AbstractUser
from django.db import models

# Modèle Routeur et Interfaces


class Router(models.Model):
    hostname = models.CharField(max_length=100, default="Unknown")
    device_type = models.CharField(max_length=100, default="Unknown")
    ip_address = models.GenericIPAddressField(unique="True")
    username = models.CharField(max_length=100, default="Unknown")
    password = models.CharField(max_length=100, default="Unknown")
    enable_password = models.CharField(max_length=100, default="Unknown")


class User(AbstractUser):
    # username = models.CharField(max_length=100, unique=True)
    # password = models.CharField(max_length=100)
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("normal", "Normal"),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default="normal")


class Interface(models.Model):
    router = models.ForeignKey("Router", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=39)
    status = models.CharField(
        max_length=100, choices=[("active", "Active"), ("inactive", "Inactive")]
    )

    def __str__(self):
        return f"{self.name} ({self.ip_address} / {self.subnet_mask})"


class Log(models.Model):
    router = models.ForeignKey("Router", on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.interface_name} - {self.ip_address}"
