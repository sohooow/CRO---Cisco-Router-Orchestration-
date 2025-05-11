import ipaddress, json, logging, os, re, sys, ssh_tool


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.test import Client
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

from .netconf_client import NetconfClient  # Adapte selon où est ton fichier

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Router, User, Interface, Log
from .serializersArti import RouterSerializer, UserSerializer, InterfaceSerializer, LogSerializer
from .forms import SubInterfaceForm, RouterForm, InterfaceForm, CustomAuthenticationForm




#@csrf_exempt  # ATTENTION : Désactive temporairement la protection CSRF

# Vue simple pour tester les méthodes GET et POST
@api_view(["GET", "POST"])
def my_view(request):
    if request.method == "GET":
        return Response({"message": "GET method is allowed now."})
    elif request.method == "POST":
        return Response({"message": "Data received"}, status=201)


# Créez un logger
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent de 'orchestration' au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Fonction d'authentification
def auth(request):
    template = loader.get_template("auth.html")
    return HttpResponse(template.render())


# Décorateur pour vérifier si l'utilisateur est un admin
def is_admin(user):
    return user.role == "admin"

#authentification des users
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('')  # Rediriger vers une page d'accueil ou une page protégée
            else:
                form.add_error(None, "Identifiants incorrects.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



# Vue protégée par un décorateur, accessible uniquement aux administrateurs
@user_passes_test(is_admin)
def add_router(request):
    if request.method == "POST":
        form = RouterForm(request.post)
        if form.is_valid():
            form.save()
            return redirect('router_list')
        else : 
            form = RouterForm()
    
    return render(request, 'add_router.html', {'form': form})

# Fonction pour valider l'adresse IP et le masque de sous-réseau
def validate_ip_and_mask(ip, mask):
    """Valide l'adresse IP et le masque de sous-réseau."""
    try:
        ipaddress.IPv4Address(ip)  # Vérifie si l'IP est valide
        ipaddress.IPv4Network(
            f"{ip}/{mask}", strict=False
        )  # Vérifie si le masque et l'IP sont valides ensemble
    except ValueError:
        return False
    return True


# Vue de configuration, accessible après authentification
@login_required                #décommenter @login_required pour sécuriser la page avec l'authentification
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
                """
                for item in filtered_output
            )
            return HttpResponse(html_rows)

        else:  # Cas d'erreur si output n'est pas une liste
            return HttpResponse(
                '<tr><td colspan="4" class="text-danger">Erreur lors de la récupération des données</td></tr>',
                status=500,
            )

    except Exception as e:
        return HttpResponse(
            f'<tr><td colspan="4" class="text-danger">Erreur: {str(e)}</td></tr>',
            status=500,
        )

def netconf_action(request):
    if request.method == "POST":
        # 1. Récupérer les données du formulaire
        interface_name = request.POST.get("interface_name")
        ip_address = request.POST.get("ip_address")
        subnet_mask = request.POST.get("subnet_mask")
        sub_interface = request.POST.get("sub_interface")
        action = request.POST.get("action")

        # 2. Connexion NETCONF
        client = NetconfClient()
        mgr = client.connect()

        if not mgr:
            return render(
                request, "error.html", {"error": "Connexion NETCONF impossible"}
            )

        response = None
        try:
            # 3. Effectuer l'action demandée
            if action in ["Create", "Update"]:
                full_interface_name = (
                    f"{interface_name}.{sub_interface}"
                    if sub_interface
                    else interface_name
                )
                response = client.create_or_update_interface(
                    interface_name=full_interface_name,
                    vlan_id=sub_interface or "1",  # par défaut 1 si vide
                    ip=ip_address,
                    mask=subnet_mask,
                )
            elif action == "Delete":
                full_interface_name = (
                    f"{interface_name}.{sub_interface}"
                    if sub_interface
                    else interface_name
                )
                response = client.delete_interface(interface_name=full_interface_name)
            else:
                return render(request, "error.html", {"error": "Action inconnue"})

        finally:
            client.disconnect()

        return render(request, "success.html", {"response": response})

    return redirect("home")


# Récupère et enregistre les données d'un routeur via NETCONF
def get_router_data_and_save_netconf(request):
    """Récupère les données d'un routeur (exemple d'interface) et les sauvegarde dans la base de données."""
    if request.method == "POST":
        try:
            router_ip = request.POST.get("router_ip")

            if not router_ip:
                return JsonResponse(
                    {"error": "L'IP du routeur est requise"}, status=400
                )
            router = Router.objects.filter(ip=router_ip).first()

            if not router:
                return JsonResponse(
                    {"error": "Routeur introuvable dans la base de données"}, status=404
                )
            client = NetconfClient(router.ip, router.username, router.password)
            client.connect()
            interfaces = client.get_interfaces_details()
            if not interfaces:
                return JsonResponse(
                    {"error": "Aucune donnée d'interface trouvée"}, status=500
                )

            for interface in interfaces:
                interface_name = interface.get("interface")
                ip_address = interface.get("ip_address")
                subnet_mask = interface.get("subnet_mask")
                status = interface.get("status", "inactive")

                Interface.objects.create(
                    router=router,
                    name=interface_name,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    status=status,
                )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Interfaces récupérées et sauvegardées",
                }
            )

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des données du routeur: {str(e)}"
            )
            return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Fonction pour analyser la sortie d'une commande CLI et extraire les informations des interfaces
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


# Récupère les données d'un routeur via SSH et les sauvegarde dans la base de données
def get_router_data_and_save(request):
    """
    Se connecte à un routeur via SSH pour récupérer les informations des interfaces réseau,
    puis enregistre ces données dans la base de données.
    """
    if request.method == "POST":
        try:
            router_ip = request.POST.get("router_ip")

            if not router_ip:
                return JsonResponse(
                    {"error": "L'IP du routeur est requise"}, status=400
                )

            router = Router.objects.filter(ip=router_ip).first()
            if not router:
                return JsonResponse(
                    {"error": "Routeur introuvable dans la base de données"}, status=404
                )

            ssh_client = ssh_tool.SSHClient(router.ip, router.username, router.password)
            output = ssh_client.execute_command("show ip interface brief")

            if not output:
                return JsonResponse(
                    {"error": "Aucune donnée d'interface trouvée"}, status=500
                )

            interfaces = parse_cli_output(
                output
            )  # Tu devras créer cette fonction pour parser la sortie CLI

            if not interfaces:
                return JsonResponse(
                    {"error": "Aucune interface trouvée dans la sortie CLI"}, status=500
                )

            for interface in interfaces:
                interface_name = interface.get("name")
                ip_address = interface.get("ip_address")
                subnet_mask = interface.get(
                    "subnet_mask", "255.255.255.0"
                )  # Valeur par défaut si non fournie
                status = interface.get("status", "inactive")

                Interface.objects.create(
                    router=router,
                    name=interface_name,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    status=status,
                )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Interfaces récupérées et sauvegardées",
                }
            )

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des données du routeur: {str(e)}"
            )
            return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Vue pour gérer l'enregistrement de la configuration des interfaces réseau via JSON
def orchestration_json(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Charger les données JSON envoyées

            # Extraire les informations
            interface_name = data.get("interfaceName")
            ip_address = data.get("ipAddress")
            subnet_mask = data.get("subnetMask")
            sub_interface = data.get("subInterface")
            action = data.get("action")
            mode = data.get("mode")

            # Vérifier si toutes les données nécessaires sont présentes
            if not all(
                [interface_name, ip_address, subnet_mask, sub_interface, action, mode]
            ):
                return JsonResponse(
                    {"error": "Tous les champs sont requis"}, status=400
                )

            # Enregistrer l'interface dans la base de données
            config = Interface.objects.create(
                name=interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                sub_interface=sub_interface,
                status=action,
                mode=mode,
            )

            return JsonResponse(
                {"message": "Configuration enregistrée", "id": config.id}, status=201
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Vue basée sur la classe View pour modifier la sous-interface
@method_decorator(csrf_exempt, name="dispatch")
class modifySubInterface(View):
    def post(self, request, *args, **kwargs):
        # Récupérer les paramètres de la requête GET
        interface_name = request.GET.get('interfaceName')
        ip_address = request.GET.get('ipAddress')
        subnet_mask = request.GET.get('subnetMask')
        sub_interface = request.GET.get('subInterface')
        action = request.GET.get('action')
        mode = request.GET.get('mode')

        if not all([interface_name, ip_address, subnet_mask, sub_interface, action, mode]):
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)
        
         # 1. Enregistrer en base via formulaire
        form_data = {
            'name': interface_name,
            'ip_address': ip_address,
            'subnet_mask': subnet_mask,
            'status': 'active' if action == "Create" else 'updated',
        }

        form = InterfaceForm(form_data)

        if form.is_valid():
            interface = form.save(commit=False)

            try:
                router = Router.objects.get(ip_address="172.16.10.11")
                interface.router = router
                interface.save()
            except Router.DoesNotExist:
                return JsonResponse({'error': 'Routeur non trouvé'}, status=404)
        else:
            return JsonResponse({'error': form.errors}, status=400)

        # 2. Envoyer la config au routeur via SSH
        try:
            output = ssh_tool.orchestration(interface_name, ip_address, subnet_mask, sub_interface, action, mode)
            return JsonResponse({
                "message": "Interface enregistrée et configuration envoyée au routeur.",
                "data": output
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': f"Erreur SSH : {str(e)}"}, status=500)

# Gestion de la base de donnnées
def delete_router(request, router_ip):
    """Supprimer un router par son adresse IP"""
    if request.method == "DELETE":
        # Essayer de récupérer le router avec l'adresse IP
        try:
            router = Router.objects.get(ip=router_ip)
        except Router.DoesNotExist:
            return JsonResponse(
                {"error": f"Router avec l'IP {router_ip} non trouvé."}, status=404
            )

        try:
            # Supprimer le router
            router.delete()
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Router avec IP {router.ip} supprimé avec succès.",
                }
            )
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
        if line.strip().startswith("interface"):
            if iface_name:
                interfaces.append(
                    {
                        "name": iface_name,
                        "ip": ip_address,
                        "subnet_mask": subnet_mask,
                        "status": "up",
                    }
                )  # Statut par défaut
            iface_name = line.split()[-1]  # Nom de l'interface, ex: GigabitEthernet0/1

        # Extraction de l'adresse IP et du masque de sous-réseau
        if "ip address" in line:
            parts = line.strip().split()
            ip_address = parts[2]  # IP de l'interface, ex: 10.0.0.1
            subnet_mask = parts[3]  # Masque de sous-réseau, ex: 255.255.255.0

    # Ajouter la dernière interface trouvée
    if iface_name:
        interfaces.append(
            {
                "name": iface_name,
                "ip": ip_address,
                "subnet_mask": subnet_mask,
                "status": "up",
            }
        )

    return interfaces


def get_interfaces_and_save(request):
    """Se connecter au routeur via SSH, récupérer les interfaces et les stocker en BDD."""
    if request.method == "POST":
        try:
            # IP Management du routeur 
            router_ip =settings.DEFAULT_ROUTER_IP
            
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
                    name=iface["name"],
                    ip_address=iface["ip"],
                    subnet_mask=iface["subnet_mask"],  # Masque de sous-réseau récupéré
                    status=iface["status"],
                )

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"{len(interfaces)} interfaces sauvegardées",
                }
            )

        except Exception as e:
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


# Ajout des vues pour manipuler les modèles dans la base de données via l'API REST


# Vue personnalisée de login héritée de LoginView pour rediriger les utilisateurs authentifiés
class MyLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class RouterViewSet(viewsets.ModelViewSet):
    queryset = Router.objects.all()
    serializer_class = RouterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer


class InterfaceViewSet(viewsets.ModelViewSet):
    queryset = Interface.objects.all()
    serializer_class = InterfaceSerializer
