from django.db import models
from django.contrib.auth.models import AbstractUser

class Router(models.Model) : 
    hostname = models.CharField(max_length=100, default='Unknown')
    device_type = models.CharField(max_length=100, default='Unknown')
    ip_address = models.GenericIPAddressField(unique='True')

    def __str__(self):
        return self.hostname

class User(AbstractUser) : 
    role = models.CharField(max_length=100, default='Unknown')

    def __str__(self):
        return self.username
    
class Interface(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    subnet_mask = models.CharField(max_length=39)
    status  = models.CharField(max_length=100, choices=[('active','Active'),('inactive', 'Inactive')])

    def __str__(self):
        return f"{self.router.hostname} - {self.name}"

class Log(models.Model) : 
    router = models.ForeignKey('Router', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    #ajouter la date et l'interface et on est bon

    def __str__(self):
        return f"Action: {self.action} on {self.router.hostname}"





