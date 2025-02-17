from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException


host = "172.16.10.11"                   #importer la data depuis la bdd
username = "admin"
password = "c79e97SGVg7dc"
enable = "Admin123INT"  

# Définir les paramètres de connexion pour Netmiko
device = {
    "device_type": "cisco_ios",
    "host": host,
    "username": username,
    "password": password,
    "secret": enable,
}

def ssh_configure_netmiko(config_commands):
    """
    Se connecte en SSH à un routeur Cisco IOS-XE avec Netmiko et exécute une commande.
    
    :param host: Adresse IP du routeur
    :param username: Nom d'utilisateur pour l'authentification
    :param password: Mot de passe pour l'authentification
    :param command: Commande à exécuter sur le routeur
    :return: La sortie de la commande ou une erreur
    """


    try:
        print(f"Connexion à {host} avec Netmiko...")
        # Connexion au routeur
        connection = ConnectHandler(**device)

        # Passer en mode enable
        print("Passage en mode enable...")
        connection.enable()
        
        # Exécution de la commande
        print("Passage en mode configuration...")
        output = connection.send_config_set(
            config_commands,
            delay_factor = 2,
        )
        
        # Déconnexion propre
        connection.disconnect()

        return output
    
    except NetMikoAuthenticationException:
        return "Erreur : Échec de l'authentification."
    except NetMikoTimeoutException:
        return "Erreur : Délai de connexion dépassé."
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"

<<<<<<< Updated upstream
def exec():
    host = "172.16.10.11"                   #importer la data depuis la bdd
    username = "admin"
    password = "c79e97SGVg7dc"
    enable = "Admin123INT"
    interface_name = ""
    command = "telnet" # Exemple de commande Cisco à exécuter
    config_commands = [
        f"",
    ]
=======

def orchestration(given_interface_name, given_ip_address, given_subnet_mask, given_sub_interface, given_action, send_mode):

    match given_action:
            case "1":
                print("cas numero 1 : créer/modifier")
                config_commands = [
                    f"interface {given_interface_name}.{given_sub_interface}",
                    f"ip address {given_ip_address} {given_subnet_mask}",
                    "write memory"
                ]
            case "0":
                print("cas numero 2 : supprimer")
                config_commands = [
                    f"no interface {given_interface_name}.{given_sub_interface}",
                    "write memory"
                ]
    if send_mode == "cli":
        try:
            # Connexion et exécution de la commande
            output = ssh_configure_netmiko(config_commands)
            print("Output de la commande SSH:", output)  # Affiche la sortie de la commande

            if output:
                return output
            
        except Exception as e:
            print(f"Erreur dans orchestration(): {str(e)}")  # Capture l'exception et l'affiche
            return {"error": f"Erreur dans orchestration(): {str(e)}"}
    elif send_mode == "netconf":
        return {"netconf": "Mode non paramétré"}
    else:
        return {"error": "Mode non valide"}

def refresh():

    config_commands = ["show ip interface brief"]  # Exemple de commande Cisco à exécuter
  
>>>>>>> Stashed changes
    try:
        # Connexion et exécution de la commande
        output = ssh_configure_netmiko(config_commands)
        print("Output de la commande SSH:", output)  # Affiche la sortie de la commande

        if isinstance(output, list):
            for interface in output:
                print(interface)  # Affiche chaque dictionnaire                
                print(f"Interface: {interface.get('interface', 'N/A')} | IP: {interface.get('ip_address', 'N/A')} | Status: {interface.get('status', 'N/A')} | Protocol: {interface.get('proto', 'N/A')}")
        else:
            print(f"Erreur lors de l'exécution de la commande : {output}")  # Affiche l'erreur si ce n'est pas une liste
        return output
    except Exception as e:
        print(f"Erreur dans refresh(): {str(e)}")  # Capture l'exception et l'affiche
        return {"error": f"Erreur dans refresh(): {str(e)}"}


if __name__ == "__main__":
    output = refresh()
    print("\n===== Résultat de la commande =====\n")
    print(output)


#le hostname par défaut est pod1-cat9kv