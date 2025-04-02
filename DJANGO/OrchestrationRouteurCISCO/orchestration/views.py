from django.shortcuts import render
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
import sys
import os
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Router, User, Interface, Log
from .serializersArti import RouterSerializer, UserSerializer, InterfaceSerializer, LogSerializer
import logging

#@csrf_exempt  # ATTENTION : Désactive temporairement la protection CSRF
#def json_view(request):
#   if request.method == "POST":
#       return JsonResponse({"message": "Requête POST reçue avec succès !"})
#   return JsonResponse({"error": "Méthode non autorisée"}, status=405)

# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer ssh_tool.py depuis le répertoire parent
import ssh_tool


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
    
        try:
            # **Enregistrer les données en base**
            config = Interface.objects.create(
                name=interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                sub_interface=sub_interface,
                status=action,
                mode=mode
            )
            
            return JsonResponse({'message': 'Configuration enregistrée', 'id': config.id}, status=201)
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

        except Exception as e:
            return JsonResponse({'error': f'Erreur lors de l’enregistrement: {str(e)}'}, status=500)
        
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
        
@csrf_exempt

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