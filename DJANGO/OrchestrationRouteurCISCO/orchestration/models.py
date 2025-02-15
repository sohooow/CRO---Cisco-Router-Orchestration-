from django.db import models
from django.contrib.auth.models import AbstractUser
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



