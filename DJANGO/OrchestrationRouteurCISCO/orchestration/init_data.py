import os
import sys

#  Add the root folder (with manage.py) to sys.path
racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(racine)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OrchestrationRouteurCISCO.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

from orchestration.models import Interface, Log, Router, User

# Retrieve environment variables to avoid hardcoding passwords
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD", "")
ROUTER_ENABLE_PASSWORD = os.getenv("ROUTER_ENABLE_PASSWORD", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")
USER_PASSWORD = os.getenv("USER_PASSWORD", "")


User = get_user_model()

#  Create permission groups
read_only_group, created = Group.objects.get_or_create(name="read-only")
read_write_group, created = Group.objects.get_or_create(name="read-write")


def add_all_perms(model, group):
    ct = ContentType.objects.get_for_model(model)
    perms = Permission.objects.filter(content_type=ct)
    for perm in perms:
        group.permissions.add(perm)


def add_view_perms(model, group):
    ct = ContentType.objects.get_for_model(model)
    view_perms = Permission.objects.filter(content_type=ct, codename__startswith="view")
    for perm in view_perms:
        group.permissions.add(perm)


for model in [Router, Interface, User, Log]:
    add_all_perms(model, read_write_group)

for model in [Router, Interface, User, Log]:
    add_view_perms(model, read_only_group)


# Function to create users with error handling if user already exists
def create_user_if_not_exists(username, password, role, is_superuser=False, group=None):
    try:
        if not User.objects.filter(username=username).exists():
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username, password=password, role=role
                )
            else:
                user = User.objects.create_user(
                    username=username, password=password, role=role
                )
            if group:
                user.groups.add(group)
            print(f"User '{username}' created.")
        else:
            print(f"User '{username}' already exists, creation skipped.")
    except IntegrityError:
        print(f"Error: user '{username}' already exists (IntegrityError captured).")


#  Create users
create_user_if_not_exists(
    "admin",
    ADMIN_PASSWORD,
    "admin",
    is_superuser=True,
    group=read_write_group,
)

create_user_if_not_exists("default", DEFAULT_PASSWORD, "normal", read_only_group)
create_user_if_not_exists("user", USER_PASSWORD, "normal" )

# Create router
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
        print("Router 172.16.10.11 created.")
    else:
        print("Router 172.16.10.11 already exists, creation skipped.")
except IntegrityError:
    print("Error: router 172.16.10.11 already exists (IntegrityError captured).")
