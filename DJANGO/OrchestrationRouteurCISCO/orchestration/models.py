from django.db import models
<<<<<<< Updated upstream
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
=======
from django.contrib.auth.models import AbstractUser
>>>>>>> Stashed changes

# Modèle Routeur et Interfaces

class Router(models.Model) : 
    hostname = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()

class User(AbstractUser) : 
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100)


class Interface(models.Model) : 
    router = models.ForeignKey(max_length=100, null=False)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=15)
    status  = models.CharField(max_length=100)

class Configuration(models.Model) : 
    router_id = models.ForeignKey(max_length=100, null = False)
    interface_id = models.ForeignKey(max_length=100, null = False)
    config_type = models.CharField(max_length=100 )

class Log(models.Model) : 
    router = models.ForeignKey(max_length=100, null = False)
    action = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.interface_name} - {self.ip_address}"


