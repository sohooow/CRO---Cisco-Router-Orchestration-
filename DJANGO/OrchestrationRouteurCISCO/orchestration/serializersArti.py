from rest_framework import serializers

from .models import Interface, Log, Router, User


class RouterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Router
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class InterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interface
        fields = "__all__"


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = "__all__"
