from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView


import sys
import os

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