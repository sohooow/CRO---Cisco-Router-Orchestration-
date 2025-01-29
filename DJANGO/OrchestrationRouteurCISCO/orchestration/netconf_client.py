from ncclient import manager
from ncclient.xml_ import to_ele

class NetconfClient:
    """Client NETCONF pour gérer les interfaces d'un routeur Cisco IOS-XE."""
    
    def __init__(self, host, username, password, port=830):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.mgr = None  

    def connect(self):
        """Établit la connexion NETCONF."""
        try:
            self.mgr = manager.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name': 'iosxe'},
                allow_agent=False,
                look_for_keys=False
            )
            print("[✅] Connexion NETCONF établie avec", self.host)
            return self.mgr
        except Exception as e:
            print(f"[❌] Erreur de connexion NETCONF: {e}")
            return None

    def send_rpc(self, xml_rpc):
        """Envoie une requête XML NETCONF."""
        try:
            rpc_element = to_ele(xml_rpc)
            response = self.mgr.dispatch(rpc_element)
            return response.xml
        except Exception as e:
            print(f"[❌] Erreur lors de l'envoi RPC: {e}")
            return None

    # ======= 📌 GESTION DES INTERFACES ======= #

    def create_or_update_interface(self, interface_name, ip, mask, operation="merge"):
        """Crée ou modifie une interface avec une adresse IP."""
        rpc = f"""
        <rpc message-id="102" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <edit-config>
            <target>
              <running/>
            </target>
            <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
              <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                  <GigabitEthernet xc:operation="{operation}">
                    <name>{interface_name}</name>
                    <ip>
                      <address>
                        <primary>
                          <address>{ip}</address>
                          <mask>{mask}</mask>
                        </primary>
                      </address>
                    </ip>
                  </GigabitEthernet>
                </interface>
              </native>
            </config>
          </edit-config>
        </rpc>
        """
        return self.send_rpc(rpc)

    def delete_interface(self, interface_name):
        """Supprime une interface."""
        rpc = f"""
        <rpc message-id="103" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <edit-config>
            <target>
              <running/>
            </target>
            <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
              <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <interface>
                  <GigabitEthernet xc:operation="delete">
                    <name>{interface_name}</name>
                  </GigabitEthernet>
                </interface>
              </native>
            </config>
          </edit-config>
        </rpc>
        """
        return self.send_rpc(rpc)
