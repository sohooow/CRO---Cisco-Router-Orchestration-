from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException

def ssh_configure_netmiko(host, username, password, enable, config_commands, command):
    """
    Se connecte en SSH à un routeur Cisco IOS-XE avec Netmiko et exécute une commande.
    
    :param host: Adresse IP du routeur
    :param username: Nom d'utilisateur pour l'authentification
    :param password: Mot de passe pour l'authentification
    :param command: Commande à exécuter sur le routeur
    :return: La sortie de la commande ou une erreur
    """
    # Définir les paramètres de connexion pour Netmiko
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "secret": enable,
    }

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
        
        output = connection.send_command(command)


        # Déconnexion propre
        connection.disconnect()
        
        return output
    
    except NetMikoAuthenticationException:
        return "Erreur : Échec de l'authentification."
    except NetMikoTimeoutException:
        return "Erreur : Délai de connexion dépassé."
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"

if __name__ == "__main__":
    # Informations pour la connexion
    host = "172.16.10.11"
    username = "admin"
    password = "c79e97SGVg7dc"
    enable = "Admin123INT"
    interface_name = "GigabitEthernet1"
    command = "show ip interface brief"  # Exemple de commande Cisco à exécuter
    config_commands = [
        f"interface {interface_name}",
        "shutdown"
    ]
    
    # Connexion et exécution de la commande
    output = ssh_configure_netmiko(host, username, password, enable, config_commands, command)
    if output:
        print("Sortie des commandes de configuration")
        print(output)



#le hostname par défaut est pod1-cat9kv