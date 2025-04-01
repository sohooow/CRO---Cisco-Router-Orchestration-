from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
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
from .serializersArti import RouterSerializer, UserSerializer, InterfaceSerializer, LogSerializer
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


@method_decorator(csrf_exempt, name='dispatch')
class modifySubInterface(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"Erreur JSON: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

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
            output = ssh_tool.orchestration(interface_name, ip_address, subnet_mask, sub_interface, action, mode)            
            return JsonResponse({"data": output})
        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)


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