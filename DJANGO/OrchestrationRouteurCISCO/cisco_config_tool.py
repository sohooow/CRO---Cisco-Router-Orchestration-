import os

from lxml import etree
from ncclient import manager
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException

host = "172.16.10.11"
username = "admin"
password = "c79e97SGVg7dc"
enable = "Admin123INT"

device = {
    "device_type": "cisco_ios",
    "host": host,
    "username": username,
    "password": password,
    "secret": enable,
}


def ssh_configure_netmiko(config_commands):
    try:
        connection = ConnectHandler(**device)

        connection.enable()

        if isinstance(config_commands, str):
            output = connection.send_command(config_commands, use_textfsm=True)
        else:
            output = connection.send_config_set(
                config_commands,
                delay_factor=2,
            )

        output_write = connection.send_command("write memory")

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
            inner = etree.fromstring(xml_payload.encode())
            config_element = etree.Element(
                "config", xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
            )
            config_element.append(inner)

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
                "encapsulation dot1Q " + given_sub_interface,
                f"ip address {given_ip_address} {given_subnet_mask}",
                "no shutdown",
                "end",
            ]

        case "Update":
            config_commands = [
                f"interface {given_interface_name}.{given_sub_interface}",
                "encapsulation dot1Q " + given_sub_interface,
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
            output = ssh_configure_netmiko(config_commands)

            refresh_output = get_interfaces_details()

            if output:
                return output

        except Exception as e:
            return {"error": f"Erreur dans orchestration(): {str(e)}"}

    elif send_mode == "netconf":
        try:
            cropped_given_interface_name = given_interface_name[-1]
            interface_name = (
                f"{cropped_given_interface_name}.{given_sub_interface}"
                if given_sub_interface
                else given_interface_name
            )
            

            if given_action == "Create" or given_action == "Update":
                xml_payload = load_netconf_template(
                    "templates_netconf/create_update_interface_native.xml",
                    {
                        "interface_name": interface_name,
                        "vlan_id": given_sub_interface,
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

            edit_result = ssh_configure_netconf(xml_payload)

            commit_result = send_commit_rpc()

            return {"edit-config": edit_result, "commit": commit_result}

        except Exception as e:
            return {"error": f"Erreur NETCONF : {str(e)}"}


def get_interfaces_details():
    command = "show ip interface brief"
    config_commands = ["show netconf-yang capabilities"]
    try:
        output = ssh_configure_netmiko(command)

        if isinstance(output, str):
            pass

        if isinstance(output, list):
            for interface in output:
                pass
        else:
            pass

        return output
    except Exception as e:
        return {"error": f"Erreur dans refresh(): {str(e)}"}


if __name__ == "__main__":
    output = get_interfaces_details()
    print(output)
    output = sendConfig(
        given_interface_name="GigabitEthernet2",
        given_ip_address="192.168.27.2",
        given_subnet_mask="255.255.255.0",
        given_sub_interface="7",
        given_action="Update",
        send_mode="netconf",
    )
    print("\n===== Résultat NETCONF =====\n")
    print(output)
