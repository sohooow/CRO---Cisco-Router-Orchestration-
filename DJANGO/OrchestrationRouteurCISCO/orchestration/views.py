from django.shortcuts import render, redirect 
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.test import Client
from django.http import JsonResponse
import json
from .netconf_client import NetconfClient  # le script NETCONF
import ipaddress
import json
import re
import sys
import os
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Router, User, Interface, Log
from .serializersArti import RouterSerializer, UserSerializer, InterfaceSerializer, LogSerializer
import logging
import ssh_tool # Importer ssh_tool.py depuis le répertoire parent

#@csrf_exempt  # ATTENTION : Désactive temporairement la protection CSRF

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Créez un logger
logger = logging.getLogger(__name__)

#Fonction d'authentification
def auth(request):
    template = loader.get_template("auth.html")
    return HttpResponse(template.render())

#Décorateur pour vérifier si l'utilisateur est un admin
def is_admin(user):
    return user.role == 'admin'

# Vue de configuration
@login_required
def config(request):
    """Page de configuration pour les utilisateurs authentifiés."""
    return render(request, "config.html")

# Fonction pour valider l'adresse IP et le masque de sous-réseau
def validate_ip_and_mask(ip, mask):
    """Valide l'adresse IP et le masque de sous-réseau."""
    try:
        ipaddress.IPv4Address(ip)  # Vérifie si l'IP est valide
        ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)  # Vérifie si le masque et l'IP sont valides ensemble
    except ValueError:
        return False
    return True

# Fonction pour récupérer le routeur depuis la base de données
def get_router_by_ip(router_ip):
    """Récupère un routeur depuis la base de données par son adresse IP."""
    try:
        return Router.objects.get(ip=router_ip)
    except Router.DoesNotExist:
        return None


# Exemple de vue simple avec DRF pour tester GET et POST
@api_view(['GET', 'POST'])
def my_view(request):
    if request.method == 'GET':
        return Response({"message": "GET method is allowed now."})
    elif request.method == 'POST':
        return Response({"message": "Data received"}, status=201)


# Fonction pour gérer l'ajout d'un routeur
@user_passes_test(lambda user: user.role == 'admin')
def add_router(request):
    """Vue pour ajouter un routeur à la base de données."""
    if request.method == "POST":
        hostname = request.POST.get('hostname')
        device_type = request.POST.get('device_type')
        ip_address = request.POST.get('ip_address')

        # Création du routeur dans la base de données
        Router.objects.create(hostname=hostname, device_type=device_type, ip_address=ip_address)
        return redirect('router_list')
    
    return render(request, 'add_router.html')


# Récupération dynamique des interfaces via SSH
def get_dynamic_output(request):
    """Récupère les informations des interfaces réseau via SSH et les retourne au format HTML."""
    try:
        output = ssh_tool.get_interfaces_details()

        # Filtrage des éléments supprimés et création des lignes HTML
        if isinstance(output, list):
            filtered_output = [item for item in output if item["status"] != "deleted"]
            html_rows = "".join(
                f"<tr><td>{item['interface']}</td><td>{item['ip_address']}</td><td>{item['status']}</td><td>{item['proto']}</td></tr>"
                for item in filtered_output
            )
            return HttpResponse(html_rows)

        return HttpResponse('<tr><td colspan="4" class="text-danger">Erreur lors de la récupération des données</td></tr>', status=500)
    
    except Exception as e:
        return HttpResponse(f'<tr><td colspan="4" class="text-danger">Erreur: {str(e)}</td></tr>', status=500)
    

# Vue pour gérer les interfaces via NETCONF (création, modification, suppression)
def manage_interface(request):
    """API pour gérer les interfaces via NETCONF."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            interface_name = data.get("interface")
            ip = data.get("ip")
            mask = data.get("mask")
            action = data.get("action")
            router_ip = data.get("router_ip")

            # Validation de l'IP et du masque
            if ip and mask and not validate_ip_and_mask(ip, mask):
                return JsonResponse({"error": "Adresse IP ou masque non valide"}, status=400)

            router = get_router_by_ip(router_ip)
            if not router:
                return JsonResponse({"error": "Routeur non trouvé"}, status=404)

            # Connexion à NETCONF et gestion des interfaces
            client = NetconfClient(router.ip, router.username, router.password)
            client.connect()

            if action == "Create":
                response = client.create_or_update_interface(interface_name, ip, mask, operation="merge")
                Interface.objects.create(router=router, name=interface_name, ip_address=ip, subnet_mask=mask, status="active")
            elif action == "Update":
                response = client.create_or_update_interface(interface_name, ip, mask, operation="replace")
                interface = Interface.objects.get(router=router, name=interface_name)
                interface.ip_address = ip
                interface.subnet_mask = mask
                interface.save()
            elif action == "Delete":
                response = client.delete_interface(interface_name)
                interface = Interface.objects.get(router=router, name=interface_name)
                interface.delete()
            else:
                return JsonResponse({"error": "Action non valide"}, status=400)

            # Enregistrement de l'action dans les logs
            Log.objects.create(router=router, action=action, user=request.user)

            return JsonResponse({"status": "success", "response": response})

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

# Vue pour récupérer les données d'un routeur via NETCONF et les enregistrer
def get_router_data_and_save_netconf(request):
    """Récupère les données d'un routeur via NETCONF et les sauvegarde dans la base de données."""
    if request.method == 'POST':
        try:
            router_ip = request.POST.get('router_ip')

            if not router_ip:
                return JsonResponse({"error": "L'IP du routeur est requise"}, status=400)

            router = get_router_by_ip(router_ip)
            if not router:
                return JsonResponse({"error": "Routeur introuvable"}, status=404)

            client = NetconfClient(router.ip, router.username, router.password)
            client.connect()
            interfaces = client.get_interfaces_details()

            if not interfaces:
                return JsonResponse({"error": "Aucune donnée d'interface trouvée"}, status=500)

            # Sauvegarde des interfaces dans la base de données
            for interface in interfaces:
                Interface.objects.create(router=router, name=interface.get('interface'), ip_address=interface.get('ip_address'), 
                                         subnet_mask=interface.get('subnet_mask'), status=interface.get('status', 'inactive'))

            return JsonResponse({"status": "success", "message": "Interfaces récupérées et sauvegardées"})

        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
            return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

# Vue pour modifier la sous-interface via POST ou GET (orchestration via JSON)
@method_decorator(csrf_exempt, name='dispatch')
class ModifySubInterface(View):
    def post(self, request, *args, **kwargs):
        """Modifie la sous-interface via une requête POST."""
        try:
            data = json.loads(request.body)
            interface_name = data.get('interfaceName')
            ip_address = data.get('ipAddress')
            subnet_mask = data.get('subnetMask')
            sub_interface = data.get('subInterface')
            action = data.get('action')

            # Vérification des champs requis
            if not all([interface_name, ip_address, subnet_mask, sub_interface, action]):
                return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

            output = ssh_tool.sendConfig(interface_name, ip_address, subnet_mask, sub_interface, action)
            return JsonResponse({"data": output})

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

    def get(self, request, *args, **kwargs):
        """Récupère les informations de la sous-interface via GET."""
        interface_name = request.GET.get('interfaceName')
        ip_address = request.GET.get('ipAddress')
        subnet_mask = request.GET.get('subnetMask')
        sub_interface = request.GET.get('subInterface')
        action = request.GET.get('action')

        if not all([interface_name, ip_address, subnet_mask, sub_interface, action]):
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

        try:
            output = ssh_tool.orchestration(interface_name, ip_address, subnet_mask, sub_interface, action)
            return JsonResponse({"data": output})

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

#________

# Ajout des vues pour manipuler les modèles dans la base de données via l'API REST

# Vue personnalisée de login héritée de `LoginView` pour rediriger les utilisateurs authentifiés
class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

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

   