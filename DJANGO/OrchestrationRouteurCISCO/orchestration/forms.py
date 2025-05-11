from django import forms
from .models import Router, Interface 

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
        fields = ['name', 'ip_address', 'subnet_mask', 'status']
