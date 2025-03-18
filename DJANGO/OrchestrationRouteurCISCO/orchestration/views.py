from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.test import Client
import json
from .netconf_client import NetconfClient  # le script NETCONF
import ipaddress
import json
import sys
import os

from rest_framework import viewsets
from .models import Router, User, Interface, Log
from serializers import RouterSerializer, UserSerializer, InterfaceSerializer, LogSerializer

import logging

# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer ssh_tool.py depuis le répertoire parent
import ssh_tool


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


def auth(request):
    template = loader.get_template("auth.html")
    return HttpResponse(template.render())

def validate_ip_and_mask(ip, mask):
    """Valide l'adresse IP et le masque de sous-réseau."""
    try:
        ipaddress.IPv4Address(ip)  # Vérifie si l'IP est valide
        ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)  # Vérifie si le masque et l'IP sont valides ensemble
    except ValueError:
        return False
    return True

#@login_required                #décommenter @login_required pour sécuriser la page avec l'authentification 
def config(request):
    template = loader.get_template("config.html")           #peut être fait en une ligne avec django de base
    return HttpResponse(template.render())



def get_dynamic_output(request):
    try:
        # Appel de la fonction refresh() pour récupérer les données
        output = ssh_tool.refresh()
        
        # Vérifiez si output est une liste
        if isinstance(output, list):
            return JsonResponse({"data": output})
        else:           #remplacer par une exception
            return JsonResponse({"error": output}, status=500)  # Retourne un message d'erreur si output n'est pas une liste
    except Exception as e:
        # Capture l'exception et renvoie les détails
        return JsonResponse({"error": f"Erreur inattendue: {str(e)}"}, status=500)
    


# API NETCONF - Création, modification, suppression d'une interface
@csrf_exempt
#@login_required  # Ajouter ce décorateur pour limiter l'accès aux utilisateurs authentifiés
def manage_interface(request):
    """API pour créer, modifier ou supprimer une interface via NETCONF."""
    if request.method == "POST":
        data = json.loads(request.body)


#formulaire django
        interface_name = data.get("interface")
        ip = data.get("ip")
        mask = data.get("mask")
        action = data.get("action")  # "create", "update" ou "delete"
        router_ip = data.get("router_ip")  # L'IP du routeur (nécessite d'être fourni dans la requête)

        # Valider l'IP et le masque
        if ip and mask:
            if not validate_ip_and_mask(ip, mask):
                return JsonResponse({"error": "Adresse IP ou masque non valide"}, status=400)
            



        # Récupérer le routeur à partir de la base de données
        try:
            router = Router.objects.get(ip=router_ip)  # Récupérer le routeur correspondant à l'IP
        except Router.DoesNotExist:
            return JsonResponse({"error": "Routeur non trouvé"}, status=404)

        # Connexion NETCONF avec les informations récupérées de la base de données
        client = NetconfClient(router.ip, router.username, router.password)
        client.connect()

        #mettre en anglais les actions (gérer le select)
        if action == "Ajouter":
            response = client.create_or_update_interface(interface_name, ip, mask, operation="merge")
        elif action == "Modifier":
            response = client.create_or_update_interface(interface_name, ip, mask, operation="replace")
        elif action == "Supprimer":
            response = client.delete_interface(interface_name)
        else:
            return JsonResponse({"error": "Action non valide"}, status=400)

        return JsonResponse({"status": "success", "response": response})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


class ConfigAPIView(View):
    def post(self, request, *args, **kwargs):
        # Récupérer les données JSON envoyées dans le body de la requête
        print("Requête reçue !")  # Vérifie si la vue est bien appelée

        try:
            data = json.loads(request.body)  # Utilise json.loads pour parser la requête JSON
        except json.JSONDecodeError as e:  # Capturer l'erreur correctement
            print(f"Erreur lors du traitement du JSON : {str(e)}")  # Afficher l'erreur
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Extraire les données
        interface_name = data.get('interfaceName', None)
        ip_address = data.get('ipAddress', None)
        subnet_mask = data.get('subnetMask', None)
        sub_interface = data.get('subInterface', None)
        action = data.get('action', None)
        mode = data.get('mode', None)
        
        print(f"Interface Name: {interface_name}")
        print(f"IP Address: {ip_address}")
        print(f"Subnet Mask: {subnet_mask}")
        print(f"Sub-Interface: {sub_interface}")
        print(f"Action: {action}")
        print(f"Mode: {mode}")

        # Vérification des données (exemple : champs obligatoires)
        if not all([interface_name, ip_address, subnet_mask, sub_interface, action, mode]):
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

        # Effectuer des traitements sur les données (exemple : validation IP)
        try:
            # Appel de la fonction orchestration() pour envoyer les données
            #modifier le nom de la fonction
            output = ssh_tool.orchestration(interface_name, ip_address, subnet_mask, sub_interface, action, mode)            
            if output:
                return JsonResponse({"data": output})
        except Exception as e:
            # Capture l'exception et renvoie les détails
            return JsonResponse({"error": f"Erreur inattendue: {str(e)}"}, status=500)


#Ajout des vues pour la base de données 

class RouterViewSet(viewsets.ModelViewSet):
    queryset = Router.objects.all()
    serializer_class = RouterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LogViewSet(viewsets.ModelViewSet) :
    queryset = Log.objects.all()
    serializer_class =LogSerializer

class InterfaceViewSet(viewsets.ModelViewSet) :
    queryset = Interface.objects.all()
    serializer_class = InterfaceSerializer