from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Modèle Utilisateur avec authentification
class User(AbstractUser):
    """Modèle utilisateur pour l'identification."""
    groups = models.ManyToManyField(
        Group,
        related_name="orchestration_users",  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="orchestration_user_permissions",
        blank=True
    )
    def __str__(self):
        return self.username

# Modèle Routeur et Interfaces
class Router(models.Model):
    """Table pour stocker les interfaces configurées sur les routeurs."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Associer un routeur à un utilisateur
    interface_name = models.CharField(max_length=50, unique=True)  # Nom de l'interface
    ip_address = models.GenericIPAddressField()  # Adresse IP de l'interface
    subnet_mask = models.CharField(max_length=15)  # Masque de sous-réseau
    sub_interface = models.CharField(max_length=50, null=True, blank=True)  # Nom de la sous-interface (optionnel)

    def __str__(self):
        return f"{self.interface_name} - {self.ip_address}"
