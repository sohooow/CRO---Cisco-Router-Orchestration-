import sys
import os

# Ajouter le dossier racine (avec manage.py) dans sys.path
racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(racine)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OrchestrationRouteurCISCO.settings')

import django
django.setup()

from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orchestration.models import Router, Interface, User, Log  



#Récupération des variables d'environnement pour ne pas stocker en dur les mots de passe
ROUTER_PASSWORD = os.getenv('ROUTER_PASSWORD', '')
ROUTER_ENABLE_PASSWORD = os.getenv('ROUTER_ENABLE_PASSWORD', '')
SUPERADMIN_PASSWORD = os.getenv('SUPERADMIN_PASSWORD', '')
READWRITE_PASSWORD = os.getenv('READWRITE_PASSWORD', '')
READONLY_PASSWORD = os.getenv('READONLY_PASSWORD', '')
USER_PASSWORD = os.getenv('USER_PASSWORD', '')


User = get_user_model()

# Création des groupes de permissions
read_only_group, created = Group.objects.get_or_create(name="read-only")
read_write_group, created = Group.objects.get_or_create(name="read-write")

def add_all_perms(model, group):
    ct = ContentType.objects.get_for_model(model)
    perms = Permission.objects.filter(content_type=ct)
    for perm in perms:
        group.permissions.add(perm)

def add_view_perms(model, group):
    ct = ContentType.objects.get_for_model(model)
    view_perms = Permission.objects.filter(content_type=ct, codename__startswith='view')
    for perm in view_perms:
        group.permissions.add(perm)

for model in [Router, Interface, User, Log]:
    add_all_perms(model, read_write_group)

for model in [Router, Interface, User, Log]:
    add_view_perms(model, read_only_group)

# Fonction pour création des users avec gestion des erreurs si user déjà existant 
def create_user_if_not_exists(username, password, role, is_superuser=False, group=None):
    try:
        if not User.objects.filter(username=username).exists():
            if is_superuser:
                user = User.objects.create_superuser(username=username, password=password, role=role)
            else:
                user = User.objects.create_user(username=username, password=password, role=role)
            if group:
                user.groups.add(group)
            print(f"Utilisateur '{username}' créé.")
        else:
            print(f"Utilisateur '{username}' existe déjà, création ignorée.")
    except IntegrityError:
        print(f"Erreur : l'utilisateur '{username}' existe déjà (IntegrityError capturée).")

# Création des utilisateurs
create_user_if_not_exists("superadmin", SUPERADMIN_PASSWORD, "admin", is_superuser=True, group=read_write_group)
create_user_if_not_exists("readwrite", READWRITE_PASSWORD, "normal", group=read_write_group)
create_user_if_not_exists("readonly", READONLY_PASSWORD, "normal", group=read_only_group)
create_user_if_not_exists("user", USER_PASSWORD, "normal")

# Création du routeur
try:
    if not Router.objects.filter(ip_address="172.16.10.11").exists():
        Router.objects.create(
            hostname="IOS_XE",
            device_type="Cisco",
            ip_address="172.16.10.11",
            username="admin",
            password=ROUTER_PASSWORD,
            enable_password=ROUTER_ENABLE_PASSWORD,
        )
        print("Routeur 172.16.10.11 créé.")
    else:
        print("Routeur 172.16.10.11 existe déjà, création ignorée.")
except IntegrityError:
    print("Erreur : le routeur 172.16.10.11 existe déjà (IntegrityError capturée).")
