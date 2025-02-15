from django.db import models
from django.contrib.auth.models import AbstractUser

class Router(models.Model) : 
    hostname = models.CharField(max_length=100, default='Unknown')
    device_type = models.CharField(max_length=100, default='Unknown')
    ip_address = models.GenericIPAddressField()

class User(AbstractUser) : 
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='Unknown')


class Interface(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=15)
    status  = models.CharField(max_length=100)

class Configuration(models.Model) : 
    router_id = models.ForeignKey('Router',on_delete=models.CASCADE)
    interface_id = models.ForeignKey('Interface', on_delete=models.CASCADE)
    config_type = models.CharField(max_length=100 )

class Log(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.interface_name} - {self.ip_address}"



