from django.shortcuts import render, redirect 
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
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
#def json_view(request):
#   if request.method == "POST":
#       return JsonResponse({"message": "Requête POST reçue avec succès !"})
#   return JsonResponse({"error": "Méthode non autorisée"}, status=405)

# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
    return render(request, "config.html")

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

##A revoir : début 

def get_router_data_and_save_netconf(request):
    """Récupère les données d'un routeur (exemple d'interface) et les sauvegarde dans la base de données."""
    if request.method == 'POST':
        try:
            router_ip = request.POST.get('router_ip')

            if not router_ip:
                return JsonResponse({"error": "L'IP du routeur est requise"}, status=400)
            router = Router.objects.filter(ip=router_ip).first()

            if not router:
                return JsonResponse({"error": "Routeur introuvable dans la base de données"}, status=404)
            client = NetconfClient(router.ip, router.username, router.password)
            client.connect()
            interfaces = client.get_interfaces_details()
            if not interfaces:
                return JsonResponse({"error": "Aucune donnée d'interface trouvée"}, status=500)

            for interface in interfaces:
                interface_name = interface.get('interface')
                ip_address = interface.get('ip_address')
                subnet_mask = interface.get('subnet_mask')
                status = interface.get('status', 'inactive')

    
                Interface.objects.create(
                    router=router,
                    name=interface_name,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    status=status
                )

            return JsonResponse({"status": "success", "message": "Interfaces récupérées et sauvegardées"})
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du routeur: {str(e)}")
            return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def parse_cli_output(output):
    """
    Cette fonction prend en entrée la sortie d'une commande CLI et en extrait
    les informations pertinentes sur les interfaces réseau du routeur.
    Elle retourne une liste de dictionnaires avec le nom de l'interface, l'adresse IP, etc.
    """
    # Expression régulière pour extraire les informations
    pattern = r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)"
    
    # Trouver toutes les correspondances
    matches = re.findall(pattern, output)
    
    # Transformer chaque ligne en un dictionnaire
    interfaces = []
    for match in matches:
        interface = {
            "name": match[0],  
            "ip_address": match[1],  
            "subnet_mask": match[2],  
            "status": match[4],  
        }
        interfaces.append(interface)
    
    return interfaces



def get_router_data_and_save(request):
    """
    Se connecte à un routeur via SSH pour récupérer les informations des interfaces réseau,
    puis enregistre ces données dans la base de données.
    """
    if request.method == 'POST':
        try:
            router_ip = request.POST.get('router_ip')

            if not router_ip:
                return JsonResponse({"error": "L'IP du routeur est requise"}, status=400)

            router = Router.objects.filter(ip=router_ip).first()
            if not router:
                return JsonResponse({"error": "Routeur introuvable dans la base de données"}, status=404)

            ssh_client = ssh_tool.SSHClient(router.ip, router.username, router.password)
            output = ssh_client.execute_command("show ip interface brief")  

            if not output:
                return JsonResponse({"error": "Aucune donnée d'interface trouvée"}, status=500)

            interfaces = parse_cli_output(output)  # Tu devras créer cette fonction pour parser la sortie CLI

            if not interfaces:
                return JsonResponse({"error": "Aucune interface trouvée dans la sortie CLI"}, status=500)

            for interface in interfaces:
                interface_name = interface.get('name')
                ip_address = interface.get('ip_address')
                subnet_mask = interface.get('subnet_mask', '255.255.255.0')  # Valeur par défaut si non fournie
                status = interface.get('status', 'inactive')

                Interface.objects.create(
                    router=router,
                    name=interface_name,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    status=status
                )

            return JsonResponse({"status": "success", "message": "Interfaces récupérées et sauvegardées"})

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du routeur: {str(e)}")
            return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

##fin 


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

@method_decorator(csrf_exempt, name='dispatch')
class modifySubInterface(View):
    def post(self, request, *args, **kwargs):
        # Récupérer les données JSON envoyées dans le body de la requête
        print("Requête POST reçue !")  # Vérifie si la vue est bien appelée


        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"Erreur JSON: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Extraction des champs
        interface_name = data.get('interfaceName')
        ip_address = data.get('ipAddress')
        subnet_mask = data.get('subnetMask')
        sub_interface = data.get('subInterface')
        action = data.get('action')
        mode = data.get('mode', 'cli')

        # Vérification des champs
        if not all([interface_name, ip_address, subnet_mask, sub_interface, action]):
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

        try:
            output = ssh_tool.sendConfig(interface_name, ip_address, subnet_mask, sub_interface, action, mode)         
            return JsonResponse({"data": output})
        except Exception as e:
            # Capture l'exception et renvoie les détails
            return JsonResponse({"error": f"Erreur inattendue: {str(e)}"}, status=500)


        
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de la requête GET
        interface_name = request.GET.get('interfaceName', None)
        ip_address = request.GET.get('ipAddress', None)
        subnet_mask = request.GET.get('subnetMask', None)
        sub_interface = request.GET.get('subInterface', None)
        action = request.GET.get('action', None)
        mode = request.GET.get('mode', None)
        
        print(f"Interface Name: {interface_name}")
        print(f"IP Address: {ip_address}")
        print(f"Subnet Mask: {subnet_mask}")
        print(f"Sub-Interface: {sub_interface}")
        print(f"Action: {action}")
        print(f"Mode: {mode}")

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
        
@csrf_exempt # Désactive la protection CSRF (à utiliser avec précaution, surtout si tu ne passes pas de token CSRF)

@api_view(['GET', 'POST']) 
def my_view(request):
    if request.method == 'GET':
        return Response({"message": "GET method is allowed now."})
    elif request.method == 'POST':
        return Response({"message": "Data received"}, status=201)
    

class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

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