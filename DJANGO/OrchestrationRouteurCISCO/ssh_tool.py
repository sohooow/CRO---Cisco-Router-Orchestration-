import os

from lxml import etree
from ncclient import manager
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException

host = "172.16.10.11"  # importer la data depuis la bdd
username = "admin"
password = "c79e97SGVg7dc"
enable = "Admin123INT"

# Définir les paramètres de connexion pour Netmiko
device = {  # importer depuis la bdd
    "device_type": "cisco_ios",
    "host": host,
    "username": username,
    "password": password,
    "secret": enable,
}


def ssh_configure_netmiko(config_commands):

    try:
        # Connexion au routeur
        connection = ConnectHandler(**device)

        # Passer en mode enable
        connection.enable()

        # Exécution de la commande
        if isinstance(config_commands, str):
            output = connection.send_command(config_commands, use_textfsm=True)
        else:
            output = connection.send_config_set(
                config_commands,
                delay_factor=2,
            )

        # Exécution de "write memory" séparément après la configuration
        output_write = connection.send_command("write memory")

        # Déconnexion propre
        connection.disconnect()

        return output

    except NetMikoAuthenticationException:
        return "Erreur : Échec de l'authentification."
    except NetMikoTimeoutException:
        return "Erreur : Délai de connexion dépassé."
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"


def send_commit_rpc():
    try:
        with manager.connect(
            host=device["host"],
            port=830,
            username=device["username"],
            password=device["password"],
            hostkey_verify=False,
            device_params={"name": "csr"},
            allow_agent=False,
            look_for_keys=False,
            timeout=30,
        ) as m:
            print("\n===== Envoi du COMMIT NETCONF =====")
            response = m.commit()
            return response.xml
    except Exception as e:
        return f"Erreur lors du commit : {str(e)}"


def load_netconf_template(template_path, variables: dict):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, template_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Template introuvable : {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(**variables)


def ssh_configure_netconf(xml_payload):
    try:
        with manager.connect(
            host=device["host"],
            port=830,
            username=device["username"],
            password=device["password"],
            hostkey_verify=False,
            device_params={"name": "csr"},
            allow_agent=False,
            look_for_keys=False,
            timeout=30,
        ) as m:
            print("Connexion NETCONF établie")

            # Parser correctement le XML inner payload
            inner = etree.fromstring(xml_payload.encode())

            # Créer l'élément <config> parent
            config_element = etree.Element(
                "config", xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
            )
            config_element.append(inner)

            print("\n===== XML FINAL ENVOYÉ À edit-config =====\n")
            print(etree.tostring(config_element, pretty_print=True).decode())

            response = m.edit_config(target="candidate", config=config_element)
            return response.xml
    except Exception as e:
        return f"Erreur NETCONF : {str(e)}"


def sendConfig(
    given_interface_name,
    given_ip_address,
    given_subnet_mask,
    given_sub_interface,
    given_action,
    send_mode,
):

    match given_action:
        case "Create":
            config_commands = [
                f"interface {given_interface_name}.{given_sub_interface}",
                "encapsulation dot1Q 1",
                f"ip address {given_ip_address} {given_subnet_mask}",
                "no shutdown",
                "end",
            ]

        case "Update":
            config_commands = [
                f"interface {given_interface_name}.{given_sub_interface}",
                "encapsulation dot1Q 1",
                f"ip address {given_ip_address} {given_subnet_mask}",
                "no shutdown",
                "end",
            ]

        case "Delete":
            config_commands = [
                f"no interface {given_interface_name}.{given_sub_interface}",
                "end",
            ]

    if send_mode == "cli":
        try:
            # Connexion et exécution de la commande
            output = ssh_configure_netmiko(config_commands)

            refresh_output = get_interfaces_details()

            if output:
                return output

        except Exception as e:
            print(
                f"Erreur dans orchestration(): {str(e)}"
            )  # Capture l'exception et l'affiche
            return {"error": f"Erreur dans orchestration(): {str(e)}"}

    elif send_mode == "netconf":
        try:
            # Construction du nom d'interface (ex: GigabitEthernet4.7)
            interface_name = (
                f"{given_interface_name}.{given_sub_interface}"
                if given_sub_interface
                else given_interface_name
            )
            vlan_id = "4"

            # Chargement du template XML en fonction de l'action
            if given_action == "Create" or given_action == "Update":
                xml_payload = load_netconf_template(
                    "templates_netconf/create_update_interface_native.xml",
                    {
                        "interface_name": interface_name,
                        "vlan_id": vlan_id,
                        "ip": given_ip_address,
                        "mask": given_subnet_mask,
                    },
                )
            elif given_action == "Delete":
                xml_payload = load_netconf_template(
                    "templates_netconf/delete_interface_native.xml",
                    {"interface_name": interface_name},
                )
            else:
                return {"error": "Action non valide pour netconf"}

            # Affichage du XML généré
            print("\n===== XML NETCONF généré (sans <rpc>) =====\n")
            print(xml_payload)

            # Envoi du XML avec edit-config vers le datastore candidate
            edit_result = ssh_configure_netconf(xml_payload)

            # Commit pour valider les modifications
            commit_result = send_commit_rpc()

            return {"edit-config": edit_result, "commit": commit_result}

        except Exception as e:
            return {"error": f"Erreur NETCONF : {str(e)}"}


def get_interfaces_details():

    command = "show ip interface brief"
    config_commands = [
        "show netconf-yang capabilities"
    ]  # Exemple de commande Cisco à exécuter

    try:
        # Connexion et exécution de la commande
        output = ssh_configure_netmiko(command)
        print(
            "Output de la commande SSH:\n", output
        )  # Affiche la sortie de la commande

        if isinstance(output, str):
            print("string2")

        if isinstance(output, list):
            print("l'output est une liste")
            for interface in output:
                print(interface)  # Affiche chaque dictionnaire
                print(
                    f"Interface: {interface.get('interface', 'N/A')} | IP: {interface.get('ip_address', 'N/A')} | Status: {interface.get('status', 'N/A')} | Protocol: {interface.get('proto', 'N/A')}"
                )
        else:
            print(
                f"Erreur lors de l'exécution de la commande : {command}"
            )  # Affiche l'erreur si ce n'est pas une liste
            print(f"Erreur : \n{output}")  # Affiche l'erreur si ce n'est pas une liste

        return output
    except Exception as e:
        print(f"Erreur dans refresh(): {str(e)}")  # Capture l'exception et l'affiche
        return {"error": f"Erreur dans refresh(): {str(e)}"}


if __name__ == "__main__":
    output = get_interfaces_details()
    print("\n===== Résultat de la commande =====\n")
    print(output)

    output = sendConfig(
        given_interface_name="2",
        given_ip_address="192.168.27.2",
        given_subnet_mask="255.255.255.0",
        given_sub_interface="7",
        given_action="Delete",
        send_mode="netconf",
    )
    print("\n===== Résultat NETCONF =====\n")
    print(output)


# le hostname par défaut est pod1-cat9kv
