import os
import dotenv
from ncclient import manager
from ncclient.xml_ import to_ele

class NetconfClient:
    """Client NETCONF sécurisé pour gérer les interfaces d'un routeur Cisco IOS-XE."""
    
    def __init__(self):
        dotenv.load_dotenv()
        self.host = os.getenv("NETCONF_HOST")
        self.username = os.getenv("NETCONF_USER")
        self.password = os.getenv("NETCONF_PASS")
        self.mgr = None  

    def connect(self):
        """Établit la connexion NETCONF."""
        try:
            self.mgr = manager.connect(
                host=self.host,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name': 'iosxe'},
                allow_agent=False,
                look_for_keys=False
            )
            print("Connexion NETCONF établie avec", self.host)
            return self.mgr
        except Exception as e:
            print(f"Erreur de connexion NETCONF: {e}")
            return None

    def disconnect(self):
        """Ferme la connexion NETCONF."""
        if self.mgr:
            self.mgr.close_session()
            print("Connexion NETCONF fermée.")
    
    def load_rpc(self, file_path, **kwargs):
        """Charge une requête XML depuis un fichier et remplace les valeurs dynamiques."""
        try:
            with open(file_path, "r") as file:
                rpc = file.read()
            return rpc.format(**kwargs)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier RPC: {e}")
            return None

    def send_rpc(self, file_path, **kwargs):
        """Envoie une requête NETCONF chargée depuis un fichier."""
        rpc = self.load_rpc(file_path, **kwargs)
        if rpc:
            try:
                rpc_element = to_ele(rpc)
                response = self.mgr.dispatch(rpc_element)
                return response.xml
            except Exception as e:
                print(f"Erreur lors de l'envoi RPC: {e}")
        return None

    def create_or_update_interface(self, interface_name, ip, mask, operation="merge"):
        """Crée ou met à jour une interface avec une adresse IP."""
        return self.send_rpc("create_update_interface.xml", interface_name=interface_name, ip=ip, mask=mask, operation=operation)

    def delete_interface(self, interface_name):
        """Supprime une interface."""
        return self.send_rpc("delete_interface.xml", interface_name=interface_name)
    
if __name__ == "__main__":
    client = NetconfClient()
    
    if client.connect():
        response = client.create_or_update_interface("GigabitEthernet5", "172.16.10.11", "255.255.255.0", "merge")
        print("Réponse RPC:", response)
        client.disconnect()
