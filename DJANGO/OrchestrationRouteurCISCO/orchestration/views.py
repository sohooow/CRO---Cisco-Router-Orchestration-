import json
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets

import cisco_config_tool

from .forms import CustomAuthenticationForm, InterfaceForm
from .models import Interface, Log, Router, User
from .serializersArti import (
    InterfaceSerializer,
    LogSerializer,
    RouterSerializer,
    UserSerializer,
)

# Add parent directory of 'orchestration' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


ROUTER_HOST = os.getenv("ROUTER_HOST")
INTERFACES_LIST = os.getenv("INTERFACES_LIST")


# Decorator to check if the user is an admin
def is_admin(user):
    return user.role == "admin"


def user_is_readwrite(user):
    return user.groups.filter(name="Read-write").exists()


@login_required
def config(request):
    return render(
        request, "config.html", {"is_readwrite": user_is_readwrite(request.user)}
    )


# User authentication
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/config")
            else:
                form.add_error(None, "Incorrect credentials.")
    else:
        form = CustomAuthenticationForm()

    return render(request, "login.html", {"form": form})


# Dynamically fetch interface details via SSH
def get_dynamic_output(request):
    try:
        # Get data from SSH
        output = cisco_config_tool.get_interfaces_details()

        # Check if output is a list
        if isinstance(output, list):

            filtered_output = [
                item
                for item in output
                if item["status"] != "deleted"
                and item["interface"] != "GigabitEthernet1"
            ]

            html_rows = "".join(
                f"""
                <tr>
                    <td>{item['interface']}</td>
                    <td>{item['ip_address']}</td>
                    <td>{item['status']}</td>
                    <td>{item['proto']}</td>
                    <td>
                        {(
                            f"<button hx-get='/add-subinterface/{item['interface']}/{item['ip_address']}' "
                            f"hx-target='#dataSection' hx-swap='innerHTML' "
                            f"class='btn btn-success btn-sm me-1 add'>"
                            f"Add <i class='fa fa-plus ms-1'></i></button>"
                            if re.match(r'^GigabitEthernet[1-4]$', item['interface']) else ""
                        )}
                        {(
                            f"<button hx-get='/update-subinterface/{item['interface']}/{item['ip_address']}' "
                            f"hx-target='#dataSection' hx-swap='innerHTML' "
                            f"class='btn btn-primary btn-sm me-1 update'>"
                            f"Edit <i class='fa fa-pencil-alt ms-1'></i></button>"
                            if '.' in item['interface'] else ""
                        )}
                        {(
                            f"<button hx-get='/delete-subinterface/{item['interface']}/{item['ip_address']}' "
                            f"hx-target='#dataSection' hx-swap='innerHTML' "
                            f"class='btn btn-danger btn-sm delete'>"
                            f"Delete <i class='fa fa-trash ms-1'></i></button>"
                            if '.' in item['interface'] else ""
                        )}
                    </td>
                </tr>
                """
                for item in filtered_output
            )
            return HttpResponse(html_rows)

        else:  # Error case if output is not a list
            return HttpResponse(
                '<tr><td colspan="4" class="text-danger">Error retrieving data</td></tr>',
                status=500,
            )

    except Exception as e:
        return HttpResponse(
            f'<tr><td colspan="4" class="text-danger">Erreur: {str(e)}</td></tr>',
            status=500,
        )


# Function to parse CLI command output and extract interface info
def parse_cli_output(output):
    """
    This function takes the output of a CLI command and extracts
    relevant information about the router's network interfaces.
    It returns a list of dictionaries with interface name, IP address, etc.
    """
    # Regex pattern to extract information
    pattern = r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)"

    # Find all matches
    matches = re.findall(pattern, output)

    # Convert each line into a dictionary
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


# Fetch router data via SSH and save it to the database
def get_router_data_and_save(request):
    """
    Connects to a router via SSH to retrieve interface details,
    then saves that data to the database.
    """
    if request.method == "POST":
        try:
            router_ip = request.POST.get("router_ip")

            if not router_ip:
                return JsonResponse({"error": "Router IP is required"}, status=400)

            router = Router.objects.filter(ip=router_ip).first()
            if not router:
                return JsonResponse(
                    {"error": "Router not found in database"}, status=404
                )

            ssh_client = cisco_config_tool.SSHClient(
                router.ip, router.username, router.password
            )
            output = ssh_client.execute_command("show ip interface brief")

            if not output:
                return JsonResponse({"error": "No interface data found"}, status=500)

            interfaces = parse_cli_output(output)

            if not interfaces:
                return JsonResponse(
                    {"error": "No interfaces found in CLI output"}, status=500
                )

            for interface in interfaces:
                interface_name = interface.get("name")
                ip_address = interface.get("ip_address")
                subnet_mask = interface.get(
                    "subnet_mask", "255.255.255.0"
                )  # Default value if not provided
                status = interface.get("status", "active")

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
                    "message": "Interfaces retrieved and saved",
                }
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"Internal server error: {str(e)}"}, status=500
            )

    return JsonResponse({"error": "Method not allowed"}, status=405)


# Class-based view to modify a sub-interface
@method_decorator(csrf_exempt, name="dispatch")
class ModifySubInterface(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        interface_name = data.get("interfaceName")
        ip_address = data.get("ipAddress")
        subnet_mask = data.get("subnetMask")
        sub_interface = data.get("subInterface")
        action = data.get("action")
        mode = data.get("mode")

        if not all(
            [interface_name, ip_address, subnet_mask, sub_interface, action, mode]
        ):
            return JsonResponse({"error": "All fields are required"}, status=400)

        # 1. Save to database via form
        form_data = {
            "name": interface_name + "." + sub_interface,
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "status": "active" if action == "1" else "inactive",
        }

        form = InterfaceForm(form_data)

        if form.is_valid():
            interface = form.save(commit=False)

            try:
                router = Router.objects.get(ip_address=ROUTER_HOST)
                interface.router = router
                interface.save()
            except Router.DoesNotExist:
                return JsonResponse({"error": "Router not found"}, status=404)
        else:
            return JsonResponse({"error": form.errors}, status=400)

        # 2. Send config to router via SSH
        try:
            output = cisco_config_tool.sendConfig(
                interface_name, ip_address, subnet_mask, sub_interface, action, mode
            )
            return JsonResponse(
                {
                    "message": "Interface saved and configuration sent to router.",
                    "data": output,
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": f"Erreur SSH : {str(e)}"}, status=500)


def parse_interfaces_and_masks(output):
    """
    Parses the output of the 'show running-config' command to extract interfaces and masks.
    Returns a list of dictionaries containing 'name', 'ip', 'subnet_mask', and 'status'.
    """
    interfaces = []
    lines = output.splitlines()

    iface_name = None
    ip_address = None
    subnet_mask = None

    for line in lines:
        # Extract interface name
        if line.strip().startswith("interface"):
            if iface_name:
                interfaces.append(
                    {
                        "name": iface_name,
                        "ip": ip_address,
                        "subnet_mask": subnet_mask,
                        "status": "up",
                    }
                )
            iface_name = line.split()[-1]

        # Extract IP address and subnet mask
        if "ip address" in line:
            parts = line.strip().split()
            ip_address = parts[2]
            subnet_mask = parts[3]

    #  Add the last found interface
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
    """Connect to the router via SSH, retrieve interfaces, and store them in the database."""
    if request.method == "POST":
        try:
            #  Router management IP
            router_ip = settings.DEFAULT_ROUTER_IP

            # Look for router in database
            try:
                router = Router.objects.get(ip=router_ip)
            except Router.DoesNotExist:
                return JsonResponse({"error": "Router not found"}, status=404)

            # SSH connection
            ssh_client = cisco_config_tool.connect(
                router.ip, router.username, router.password
            )

            # Get interfaces and masks
            output = cisco_config_tool.execute_command(
                ssh_client, "show running-config"
            )
            cisco_config_tool.disconnect(ssh_client)

            # Parse interfaces and masks
            interfaces = parse_interfaces_and_masks(output)

            if not interfaces:
                return JsonResponse({"error": "No interfaces found"}, status=500)

            # Delete existing interfaces
            Interface.objects.filter(router=router).delete()

            # Save interfaces to the database
            for iface in interfaces:
                Interface.objects.create(
                    router=router,
                    name=iface["name"],
                    ip_address=iface["ip"],
                    subnet_mask=iface["subnet_mask"],
                    status=iface["status"],
                )

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"{len(interfaces)} interfaces saved",
                }
            )

        except Exception as e:
            return JsonResponse({"error": f"Error : {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def sync_router(request):
    if request.method == "POST":
        router_ip = request.POST.get("router_ip", ROUTER_HOST)
        router, created = Router.objects.get_or_create(ip_address=router_ip)

        response = request.get(INTERFACES_LIST)

        if response.status_code == 200:
            data = response.text.strip().split("\n")
            for line in data:
                parts = line.split()
                if len(parts) >= 4:
                    name = parts[0]
                    ip_address = parts[1]
                    subnet_mask = "255.255.255.0"  # Default value
                    status = "active" if parts[2].lower() == "up" else "inactive"

                    Interface.objects.update_or_create(
                        router=router,
                        name=name,
                        defaults={
                            "ip_address": ip_address,
                            "subnet_mask": subnet_mask,
                            "status": status,
                        },
                    )
            return JsonResponse(
                {"status": "success", "message": "Interfaces synchronized"}
            )
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to get data from router"},
                status=500,
            )

    return JsonResponse(
        {"status": "error", "message": "POST method required"}, status=405
    )


# Views to manipulate models in the database via the REST API


# Custom login view inherited from LoginView to redirect authenticated users
class MyLoginView(LoginView):
    template_name = "login.html"
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


@login_required
def add_subinterface(request, interface, ipaddress):
    interface_name = interface.split(".")[0]
    data = {
        "interfaceName": interface_name,
        "subInterface": "",
        "ipAddress": ipaddress,
        "action": "Create",
        "is_readwrite": user_is_readwrite(request.user),
    }
    return render(request, "subinterface_form_add_update.html", data)


@login_required
def update_subinterface(request, interface, ipaddress):
    if "." in interface:
        interface_name, sub_interface = interface.split(".", 1)
    else:
        interface_name = interface
        sub_interface = ""

    data = {
        "interfaceName": interface_name,
        "subInterface": sub_interface,
        "ipAddress": ipaddress,
        "action": "Update",
        "is_readwrite": user_is_readwrite(request.user),
    }
    return render(request, "subinterface_form_add_update.html", data)


@login_required
def delete_subinterface(request, interface, ipaddress):
    if "." in interface:
        interface_name, sub_interface = interface.split(".", 1)
    else:
        interface_name = interface
        sub_interface = ""

    data = {
        "interfaceName": interface_name,
        "subInterface": sub_interface,
        "ipAddress": ipaddress,
        "action": "Delete",
        "is_readwrite": user_is_readwrite(request.user),
    }
    return render(request, "subinterface_form_delete.html", data)


@require_POST
def logout_view(request):
    if request.headers.get("Hx-Request") != "true":
        return JsonResponse({"error": "Invalid HTMX request"}, status=400)
    logout(request)
    return JsonResponse({"redirect": "/"})
