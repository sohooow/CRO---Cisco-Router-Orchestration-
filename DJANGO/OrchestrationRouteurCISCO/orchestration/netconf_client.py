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

            message_id = str(uuid.uuid4())
            rpc = rpc.format(message_id=message_id, **kwargs)
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
        response = self.send_rpc(
            "create_update_interface_native.xml",
            interface_name=interface_name,
            vlan_id=vlan_id,
            ip=ip,
            mask=mask,
            operation=operation
        )
        if response:
            self.commit_changes()
        return response

    def delete_interface(self, interface_name):
        """Supprime une interface (modèle Cisco IOS-XE)."""
        response = self.send_rpc(
            "delete_interface_native.xml",
            interface_name=interface_name
        )
        if response:
            self.commit_changes()
        return response

    def generate_modify_interface_rpc(self, interface_name, new_interface_name=None, ip_address=None, subnet_mask=None, description=None):
        """Génère dynamiquement un RPC XML pour modifier une interface existante."""
        config_parts = []

        if new_interface_name:
            config_parts.append(f"<name>{new_interface_name}</name>")
        else:
            config_parts.append(f"<name>{interface_name}</name>")

        if description:
            config_parts.append(f"<description>{description}</description>")

        if ip_address and subnet_mask:
            config_parts.append(f"""
            <ip>
              <address>
                <primary>
                  <address>{ip_address}</address>
                  <mask>{subnet_mask}</mask>
                </primary>
              </address>
            </ip>""")

        if not config_parts:
            raise ValueError("Aucune information fournie pour modifier l'interface.")

        config_body = "\n".join(config_parts)
        message_id = str(uuid.uuid4())

        rpc = f"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{message_id}">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            {config_body}
          </GigabitEthernet>
        </interface>
      </native>
    </config>
  </edit-config>
</rpc>"""
        return rpc

    def modify_interface(self, interface_name, new_interface_name=None, ip_address=None, subnet_mask=None, description=None):
        """Modifie dynamiquement les attributs d'une interface."""
        try:
            rpc = self.generate_modify_interface_rpc(
                interface_name=interface_name,
                new_interface_name=new_interface_name,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                description=description
            )
            rpc_element = to_ele(rpc)
            response = self.mgr.dispatch(rpc_element)
            self.commit_changes()
            return response.xml
        except Exception as e:
            print(f"Erreur lors de la modification de l'interface : {e}")
            return None
