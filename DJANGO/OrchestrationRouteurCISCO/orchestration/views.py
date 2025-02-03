from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
<<<<<<< Updated upstream
from django.views.decorators.csrf import csrf_exempt
import json
from .netconf_client import NetconfClient  # le script NETCONF

import ipaddress
=======
from django.views import View
import json
>>>>>>> Stashed changes
import sys
import os

import logging

# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer ssh_tool.py depuis le répertoire parent
import ssh_tool


class MyLoginView(LoginView):
    template_name = 'resgistration/login.html'
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
    template = loader.get_template("config.html")
    return HttpResponse(template.render())

def get_dynamic_output(request):
    try:
        # Appel de la fonction exec() pour récupérer les données
        output = ssh_tool.exec()
        
        # Vérifiez si output est une liste
        if isinstance(output, list):
            return JsonResponse({"data": output})
        else:
            return JsonResponse({"error": output}, status=500)  # Retourne un message d'erreur si output n'est pas une liste
    except Exception as e:
        # Capture l'exception et renvoie les détails
        return JsonResponse({"error": f"Erreur inattendue: {str(e)}"}, status=500)
<<<<<<< Updated upstream
    

# API NETCONF - Création, modification, suppression d'une interface
@csrf_exempt
@login_required  # Ajouter ce décorateur pour limiter l'accès aux utilisateurs authentifiés
def manage_interface(request):
    """API pour créer, modifier ou supprimer une interface via NETCONF."""
    if request.method == "POST":
        data = json.loads(request.body)

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

=======


class ConfigAPIView(View):
    def post(self, request, *args, **kwargs):

        # Récupérer les données JSON envoyées dans le body de la requête
        try:
            data = json.loads(request.body)  # Utilise json.loads pour parser la requête JSON
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Extraire les données
        interface_name = data.get('interfaceName', None)
        ip_address = data.get('ipAddress', None)
        subnet_mask = data.get('subnetMask', None)
        sub_interface = data.get('subInterface', None)
        action = data.get('action', None)
        
        # Effectuer des traitements sur les données (par exemple, une configuration réseau)
        
        # Vous pouvez envoyer une réponse au client ici
        response_data = {
            'status': 'success',
            'message': 'Configuration traitée avec succès!'
        }
        
        return JsonResponse(response_data)  # Retourne un JSON au frontend
>>>>>>> Stashed changes
