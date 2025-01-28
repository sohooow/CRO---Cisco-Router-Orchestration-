const interfaces = ['GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet1/1', 'BundleEther0/1', 'BundleEther1/1', 'HundredGigE0/0/0', 'HundredGigE1/1/1', 'FastEthernet0/1', 'FastEthernet1/1'];
const interfaceNameField = document.getElementById('interfaceName');

//<!-- Finir de coder le menu déroulant filtré en fonction de la saisie du user -->

//Envoi de la data au back-end
document.getElementById('executeBtn').addEventListener('click', sendJsonData()); 

function sendJsonData(){

    // Send JSON data to the backend
    fetch('http://localhost:8000/orchestration/config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(getData())
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function printOutput() {

    const output = `Commande exécutée : ${command} (${action})`;
    document.getElementById('cliOutput').textContent = output;

}

//Récupérer la data
function getData() {
 
    const interfaceName = document.getElementById('interfaceName').value;
    const ipAddress = document.getElementById('ipAddress').value;
    const subnetMask = document.getElementById('SubnetMask').value;
    const subInterface = document.getElementById('SubInterface').value;
    const action = document.getElementById('Action').value;

    
    const JsonData = {
        interfaceName: interfaceName,
        ipAddress: ipAddress,
        subnetMask: subnetMask,
        subInterface: subInterface,
        action: action,
    };

    return JsonData;

}

// Fonction pour récupérer les interfaces dynamiquement
function loadDynamicData() {
// Effectuer une requête AJAX pour obtenir les données
fetch('/orchestration/dynamic-output/')
    .then(response => response.json())  // Convertir la réponse en JSON
    .then(data => {
        // Si l'API renvoie un champ "data"
        if (data && data.data) {
            // Trouver le corps du tableau
            const tbody = document.querySelector('#interfaceTable tbody');

            // Parcourir les données et ajouter des lignes au tableau
            data.data.forEach(interface => {
                const row = document.createElement('tr');  // Créer une nouvelle ligne

                // Créer et ajouter les cellules (td) pour chaque champ
                const cell1 = document.createElement('td');
                cell1.textContent = interface.interface || 'N/A';
                row.appendChild(cell1);

                const cell2 = document.createElement('td');
                cell2.textContent = interface.ip_address || 'N/A';
                row.appendChild(cell2);

                const cell3 = document.createElement('td');
                cell3.textContent = interface.status || 'N/A';
                row.appendChild(cell3);

                const cell4 = document.createElement('td');
                cell4.textContent = interface.proto || 'N/A';
                row.appendChild(cell4);

                // Ajouter la ligne au tableau
                tbody.appendChild(row);
            });
        } else {
            // Si aucune donnée n'est disponible, afficher un message
            const tbody = document.querySelector('#interfaceTable tbody');
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.setAttribute('colspan', '4');
            cell.textContent = 'Aucune donnée disponible (vérifiiez le VPN)';
            row.appendChild(cell);
            tbody.appendChild(row);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données:', error);
    });
}

// Charger les données dynamiques lorsque la page est prête
document.addEventListener('DOMContentLoaded', loadDynamicData);