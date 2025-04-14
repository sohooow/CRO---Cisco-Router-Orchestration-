from django.db import models
from django.contrib.auth.models import AbstractUser

# Modèle Routeur et Interfaces

class Router(models.Model) : 
    hostname = models.CharField(max_length=100, default='Unknown')
    device_type = models.CharField(max_length=100, default='Unknown')
    ip_address = models.GenericIPAddressField(unique='True')

class User(AbstractUser) : 
    #username = models.CharField(max_length=100, unique=True)
    #password = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='Unknown')


class Interface(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=39)
    status  = models.CharField(max_length=100, choices=[('active','Active'),('inactive', 'Inactive')])


class Log(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.ip_address}"


# Configuration model
class Configuration(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE, null=False)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, null=False)
    config_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.config_type} for {self.router.hostname}"


# Log model
class Log(models.Model):
    router = models.ForeignKey(Router, on_delete=models.CASCADE, null=False)
    action = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.router.hostname} - {self.action}"
