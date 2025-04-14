from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException


host = "172.16.10.11"                   #importer la data depuis la bdd
username = "admin"
password = "c79e97SGVg7dc"
enable = "Admin123INT"  

# Définir les paramètres de connexion pour Netmiko
device = {                              #importer depuis la bdd
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
                delay_factor = 2,
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


def sendConfig(given_interface_name, given_ip_address, given_subnet_mask, given_sub_interface, given_action, send_mode):
    
    match given_action:
            case "1":
                config_commands = [
                    f"interface {given_interface_name}.{given_sub_interface}",
                    "encapsulation dot1Q 1",
                    f"ip address {given_ip_address} {given_subnet_mask}",
                    "no shutdown",
                    "end",
                ]

            case "0":
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
            print(f"Erreur dans orchestration(): {str(e)}")  # Capture l'exception et l'affiche
            return {"error": f"Erreur dans orchestration(): {str(e)}"}
        

    elif send_mode == "netconf":
        return {"netconf": "Mode non paramétré"}
    else:
        return {"error": "Mode non valide"}

def get_interfaces_details():

    command = "show ip interface brief"
  
    try:
        # Connexion et exécution de la commande
        output = ssh_configure_netmiko(command)
        print("Output de la commande SSH:\n", output)  # Affiche la sortie de la commande

        if isinstance(output, str):
            print("string2")

        if isinstance(output, list):
            print("l'output est une liste")
            for interface in output:
                print(interface)  # Affiche chaque dictionnaire                
                print(f"Interface: {interface.get('interface', 'N/A')} | IP: {interface.get('ip_address', 'N/A')} | Status: {interface.get('status', 'N/A')} | Protocol: {interface.get('proto', 'N/A')}")
        else:
            print(f"Erreur lors de l'exécution de la commande : {command}")  # Affiche l'erreur si ce n'est pas une liste
            print(f"Erreur : \n{output}")  # Affiche l'erreur si ce n'est pas une liste

        return output
    except Exception as e:
        print(f"Erreur dans refresh(): {str(e)}")  # Capture l'exception et l'affiche
        return {"error": f"Erreur dans refresh(): {str(e)}"}


if __name__ == "__main__":
    output = get_interfaces_details()
    print("\n===== Résultat de la commande =====\n")
    print(output)


#le hostname par défaut est pod1-cat9kv