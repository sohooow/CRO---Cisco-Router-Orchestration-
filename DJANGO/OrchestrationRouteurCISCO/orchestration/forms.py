from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Interface, Router, User


# Form for sub-interface operations
class SubInterfaceForm(forms.Form):
    interfaceName = forms.CharField()
    ipAddress = forms.GenericIPAddressField()
    subnetMask = forms.CharField()
    subInterface = forms.IntegerField()
    action = forms.ChoiceField(
        choices=[("1", "Create"), ("1", "Update"), ("0", "Delete")]
    )
    mode = forms.ChoiceField(choices=[("cli", "CLI"), ("netconf", "NETCONF")])


# Form for Router model
class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = ["hostname", "device_type", "ip_address"]


# Form for Interface model
class InterfaceForm(forms.ModelForm):
    class Meta:
        model = Interface
        fields = ["name", "ip_address", "subnet_mask", "status"]


# Custom authentication form with English labels
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
