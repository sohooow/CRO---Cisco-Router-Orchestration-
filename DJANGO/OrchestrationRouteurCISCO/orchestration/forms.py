from django import forms
from .models import Router, Interface, User
from django.contrib.auth.forms import AuthenticationForm



class SubInterfaceForm(forms.Form):
    interfaceName = forms.CharField()
    ipAddress = forms.GenericIPAddressField()
    subnetMask = forms.CharField()
    subInterface = forms.IntegerField()
    action = forms.ChoiceField(choices=[("1", "Create"), ("1", "Update"), ("0", "Delete")])
    mode = forms.ChoiceField(choices=[("cli", "CLI"), ("netconf", "NETCONF")])

class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = ['hostname', 'device_type', 'ip_address']  

class InterfaceForm(forms.ModelForm):
    class Meta:
        model = Interface
        fields = ['router','name', 'ip_address', 'subnet_mask', 'status']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=100)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)