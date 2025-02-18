# from celery import shared_task
# import json
# from django.test import Client

# @shared_task
# def execute_config_api(data):
#     client = Client()
#     response = client.post("/config-api/", json.dumps(data), content_type="application/json")
#     return response.json()  # Retourne les données JSON de la vue
