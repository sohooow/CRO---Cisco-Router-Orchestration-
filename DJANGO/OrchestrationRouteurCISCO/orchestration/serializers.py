from rest_framework import serializers 
from .models import Router, User, Interface, Log



class RouterSerializer(serializers.ModelSerializer) : 
    class Meta : 
        model = Router
        fields ="_all_"


class UserSerializer(serializers.ModelSerializer) : 
    class Meta : 
        model = User
        fields ="_all_"

class InterfaceSerializer(serializers.ModelSerializer) : 
    class Meta : 
        model = Interface
        fields ="_all_"

class LogSerializer(serializers.ModelSerializer) : 
    class Meta : 
        model = Log
        fields ="_all_"
