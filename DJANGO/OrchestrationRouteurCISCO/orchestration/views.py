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

# Vue simple pour tester les méthodes GET et POST
@api_view(['GET', 'POST']) 
def my_view(request):
    if request.method == 'GET':
        return Response({"message": "GET method is allowed now."})
    elif request.method == 'POST':
        return Response({"message": "Data received"}, status=201)


# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#Fonction d'authentification
def auth(request):
    template = loader.get_template("auth.html")
    return HttpResponse(template.render())

#Décorateur pour vérifier si l'utilisateur est un admin
def is_admin(user):
    return user.role == 'admin'

#Vue protégée par un décorateur, accessible uniquement aux administrateurs   
@user_passes_test(is_admin)
def add_router(request):
    if request.method == "POST":
        # Code pour ajouter un routeur : 
        #1. Récupère les informations du routeur via POST
        hostname = request.POST.get('hostname')
        device_type = request.POST.get('device_type')
        ip_address = request.POST.get('ip_address')

        #2. Crée un nouvel objet routeur dans la base de données
        Router.objects.create(hostname=hostname, device_type=device_type, ip_address=ip_address)
        return redirect('router_list')  
    
    return render(request, 'add_router.html')

# Fonction pour valider l'adresse IP et le masque de sous-réseau
def validate_ip_and_mask(ip, mask):
    """Valide l'adresse IP et le masque de sous-réseau."""
    try:
        ipaddress.IPv4Address(ip)  # Vérifie si l'IP est valide
        ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)  # Vérifie si le masque et l'IP sont valides ensemble
    except ValueError:
        return False
    return True

# Vue de configuration, accessible après authentification
#@login_required                #décommenter @login_required pour sécuriser la page avec l'authentification 
def config(request):
    return render(request, "config.html")


# Récupération dynamique des informations des interfaces via SSH
def get_dynamic_output(request):
    try:
        # Récupération des données depuis SSH
        output = ssh_tool.get_interfaces_details()

        # Vérification si output est une liste
        if isinstance(output, list):

            filtered_output = [item for item in output if item["status"] != "deleted"]

            html_rows = "".join(
                f"""
                <tr>
                    <td>{item['interface']}</td>
                    <td>{item['ip_address']}</td>
                    <td>{item['status']}</td>
                    <td>{item['proto']}</td>
                </tr>
                """ for item in filtered_output
            )
            return HttpResponse(html_rows)

        else:  # Cas d'erreur si output n'est pas une liste
            return HttpResponse(
                '<tr><td colspan="4" class="text-danger">Erreur lors de la récupération des données</td></tr>', 
                status=500
            )

    except Exception as e:
        return HttpResponse(
            f'<tr><td colspan="4" class="text-danger">Erreur: {str(e)}</td></tr>', 
            status=500
        )
    

# API NETCONF - Création, modification, suppression d'une interface

#@login_required  # Ajouter ce décorateur pour limiter l'accès aux utilisateurs authentifiés
def manage_interface(request):
    """API pour créer, modifier ou supprimer une interface via NETCONF."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

#formulaire django : extraction des champs
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
        if action == "Create":
            response = client.create_or_update_interface(interface_name, ip, mask, operation="merge")
            new_interface = Interface.objects.create(
                router=router,
                name=interface_name,
                ip_address=ip,
                subnet_mask=mask,
                status="active"  # Ajoute le statut par défaut "active"
            )
            new_interface.save()
        elif action == "Update":
            response = client.create_or_update_interface(interface_name, ip, mask, operation="replace")
            try:
                interface = Interface.objects.get(router=router, name=interface_name)
                interface.ip_address = ip
                interface.subnet_mask = mask
                interface.save()
                response = client.create_or_update_interface(interface_name, ip, mask, operation="replace")
            except Interface.DoesNotExist:
                return JsonResponse({"error": "Interface non trouvée"}, status=404)
        elif action == "Delete":
            response = client.delete_interface(interface_name)
            try:
                interface = Interface.objects.get(router=router, name=interface_name)
                interface.delete()
                response = client.delete_interface(interface_name)
            except Interface.DoesNotExist:
                return JsonResponse({"error": "Interface non trouvée"}, status=404)

        else:
            return JsonResponse({"error": "Action non valide"}, status=400)
        
        # Enregistrer l'action dans les logs
        Log.objects.create(
            router=router,
            action=action,
            user=request.user  # Enregistre l'utilisateur connecté qui a effectué l'action
        )

        return JsonResponse({"status": "success", "response": response})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Vue pour gérer l'enregistrement de la configuration des interfaces réseau via JSON
def orchestration_json(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Charger les données JSON envoyées

            # Extraire les informations
            interface_name = data.get('interfaceName')
            ip_address = data.get('ipAddress')
            subnet_mask = data.get('subnetMask')
            sub_interface = data.get('subInterface')
            action = data.get('action')
            mode = data.get('mode')

            # Vérifier si toutes les données nécessaires sont présentes
            if not all([interface_name, ip_address, subnet_mask, sub_interface, action, mode]):
                return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

            # Enregistrer l'interface dans la base de données
            config = Interface.objects.create(
                name=interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                sub_interface=sub_interface,
                status=action,
                mode=mode
            )

            return JsonResponse({'message': 'Configuration enregistrée', 'id': config.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# Vue basée sur la classe View pour modifier la sous-interface

@method_decorator(csrf_exempt, name='dispatch')
class ModifySubInterface(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            interface_name = data.get('interfaceName')
            ip_address = data.get('ipAddress')
            subnet_mask = data.get('subnetMask')
            sub_interface = data.get('subInterface')
            action = data.get('action')

            if not all([interface_name, ip_address, subnet_mask, sub_interface, action]):
                return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

            # Envoie la config au routeur via SSH
            output = ssh_tool.sendConfig(interface_name, ip_address, subnet_mask, sub_interface, action)

            # Enregistrement dans la BDD
            Interface.objects.create(
                name=interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                status='active' if action == "Create" else 'updated',
                router_ip='172.16.10.11',  #attacher au routeur
            )

            return JsonResponse({"data": output})

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

        
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de la requête GET
        interface_name = request.GET.get('interfaceName', None)
        ip_address = request.GET.get('ipAddress', None)
        subnet_mask = request.GET.get('subnetMask', None)
        sub_interface = request.GET.get('subInterface', None)
        action = request.GET.get('action', None)
        mode = request.GET.get('mode', None)
        

        # Vérification des paramètres (exemple : champs obligatoires)
        if not all([interface_name, ip_address, subnet_mask, sub_interface, action, mode]):
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

        # Effectuer des traitements sur les données (exemple : validation IP)
        try:
            # Appel de la fonction orchestration() pour envoyer les données
            output = ssh_tool.orchestration(interface_name, ip_address, subnet_mask, sub_interface, action, mode)            
            if output:
                return JsonResponse({"data": output})
        except Exception as e:
            # Capture l'exception et renvoie les détails
            return JsonResponse({"error": f"Erreur inattendue: {str(e)}"}, status=500)

        # Optionnel : Tu peux récupérer les données et les afficher ou les manipuler
        # par exemple ici l'enregistrement en base de données comme dans la version POST
        try:
            config = Interface.objects.create(
                name=interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                sub_interface=sub_interface,
                status=action,
                mode=mode
            )
            return JsonResponse({'message': 'Configuration enregistrée', 'id': config.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de l’enregistrement: {str(e)}'}, status=500)



#Gestion de la base de donnnées
def delete_router(request, router_ip):
    """Supprimer un router par son adresse IP"""
    if request.method == 'DELETE':
        # Essayer de récupérer le router avec l'adresse IP
        try:
            router = Router.objects.get(ip=router_ip)
        except Router.DoesNotExist:
            return JsonResponse({"error": f"Router avec l'IP {router_ip} non trouvé."}, status=404)

        try:
            # Supprimer le router
            router.delete()
            return JsonResponse({"status": "success", "message": f"Router avec IP {router.ip} supprimé avec succès."})
        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)


def parse_interfaces_and_masks(output):
    """
    Parse le résultat de la commande 'show running-config' pour extraire les interfaces et leurs masques.
    Retourne une liste de dictionnaires contenant 'name', 'ip', 'subnet_mask' et 'status'.
    """
    interfaces = []
    lines = output.splitlines()
    
    iface_name = None
    ip_address = None
    subnet_mask = None

    for line in lines:
        # Extraction du nom de l'interface
        if line.strip().startswith('interface'):
            if iface_name:
                interfaces.append({'name': iface_name, 'ip': ip_address, 'subnet_mask': subnet_mask, 'status': 'up'})  # Statut par défaut
            iface_name = line.split()[-1]  # Nom de l'interface, ex: GigabitEthernet0/1

        # Extraction de l'adresse IP et du masque de sous-réseau
        if 'ip address' in line:
            parts = line.strip().split()
            ip_address = parts[2]  # IP de l'interface, ex: 10.0.0.1
            subnet_mask = parts[3]  # Masque de sous-réseau, ex: 255.255.255.0

    # Ajouter la dernière interface trouvée
    if iface_name:
        interfaces.append({'name': iface_name, 'ip': ip_address, 'subnet_mask': subnet_mask, 'status': 'up'})

    return interfaces


def get_interfaces_and_save(request):
    """Se connecter au routeur via SSH, récupérer les interfaces et les stocker en BDD."""
    if request.method == 'POST':
        try:
            # IP Management du routeur 
            router_ip = "172.16.10.11"
            
            # Cherche le routeur en BDD
            try:
                router = Router.objects.get(ip=router_ip)
            except Router.DoesNotExist:
                return JsonResponse({"error": "Routeur introuvable"}, status=404)

            # Connexion SSH
            ssh_client = ssh_tool.connect(router.ip, router.username, router.password)

            # Récupération des interfaces et masques via la commande 'show running-config'
            output = ssh_tool.execute_command(ssh_client, "show running-config")
            ssh_tool.disconnect(ssh_client)

            # Parser les interfaces et les masques
            interfaces = parse_interfaces_and_masks(output)

            if not interfaces:
                return JsonResponse({"error": "Aucune interface trouvée"}, status=500)

            # Supprimer les anciennes interfaces existantes
            Interface.objects.filter(router=router).delete()

            # Enregistrement des interfaces dans la base de données
            for iface in interfaces:
                Interface.objects.create(
                    router=router,
                    name=iface['name'],
                    ip_address=iface['ip'],
                    subnet_mask=iface['subnet_mask'],  # Masque de sous-réseau récupéré
                    status=iface['status']
                )

            return JsonResponse({"status": "success", "message": f"{len(interfaces)} interfaces sauvegardées"})

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Ajout des vues pour manipuler les modèles dans la base de données via l'API REST

# Vue personnalisée de login héritée de LoginView pour rediriger les utilisateurs authentifiés
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
