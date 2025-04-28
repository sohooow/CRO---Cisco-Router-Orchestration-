import os
import dotenv
import uuid
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

            # Générer un message ID unique
            message_id = str(uuid.uuid4())

            # Remplacement des placeholders dans le fichier XML
            rpc = rpc.format(message_id=message_id, **kwargs)
            
            # Vérifier si le remplacement a réussi
            print(f"RPC après remplacement : {rpc}")
            
            return rpc
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

    def commit_changes(self):
        """Effectue un commit des modifications pour les rendre effectives."""
        try:
            commit_rpc = """<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{message_id}">
                              <commit/>
                            </rpc>"""
            commit_rpc = commit_rpc.format(message_id=str(uuid.uuid4()))
            rpc_element = to_ele(commit_rpc)
            response = self.mgr.dispatch(rpc_element)
            print("Commit effectué.")
            return response.xml
        except Exception as e:
            print(f"Erreur lors du commit des modifications : {e}")
        return None

    def create_or_update_interface(self, interface_name, vlan_id, ip, mask, operation="merge"):
        """Crée ou met à jour une interface avec une adresse IP (modèle Cisco IOS-XE)."""
        response = self.send_rpc("create_update_interface_native.xml", interface_name=interface_name, vlan_id=vlan_id, ip=ip, mask=mask, operation=operation)
        if response:
            # Après la création ou mise à jour, effectuer un commit
            self.commit_changes()
        return response

    def delete_interface(self, interface_name):
        """Supprime une interface (modèle Cisco IOS-XE)."""
        response = self.send_rpc("delete_interface_native.xml", interface_name=interface_name)
        if response:
            # Après la suppression, effectuer un commit
            self.commit_changes()
        return response

if __name__ == "__main__":
    client = NetconfClient()
    
    if client.connect():
        # Exemple de création ou mise à jour d'interface
        response = client.create_or_update_interface(interface_name="GigabitEthernet1.5", vlan_id=5, ip="172.16.10.11", mask="255.255.255.0", operation="create")
        print("Réponse RPC création ou mise à jour :", response)

        # Exemple de suppression d'interface
        response_delete = client.delete_interface(interface_name="GigabitEthernet1.5")
        print("Réponse RPC suppression :", response_delete)

        client.disconnect()
