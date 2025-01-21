const interfaces = ['GigabitEthernet0/1', 'GigabitEthernet0/2', 'GigabitEthernet1/1', 'BundleEther0/1', 'BundleEther1/1', 'HundredGigE0/0/0', 'HundredGigE1/1/1', 'FastEthernet0/1', 'FastEthernet1/1'];
const interfaceNameField = document.getElementById('interfaceName');

//<!-- Finir de coder le menu déroulant filtré en fonction de la saisie du user -->
//<!-- Basculement dynamique du mode -->

document.getElementById('cliModeBtn').addEventListener('click', function() {
    document.getElementById('cliSection').style.display = 'block';
    document.getElementById('netconfSection').style.display = 'none';
});

document.getElementById('netconfModeBtn').addEventListener('click', function() {
    document.getElementById('cliSection').style.display = 'none';
    document.getElementById('netconfSection').style.display = 'block';
});

// Exécution de la partie CLI
document.getElementById('cliExecuteBtn').addEventListener('click', function() {
    const command = document.getElementById('cliCommand').value;
    const action = document.getElementById('cliAction').value;
    const output = `Commande exécutée : ${command} (${action})`;
    document.getElementById('cliOutput').textContent = output;
});

// Exécution de la partie NETCONF
document.getElementById('netconfExecuteBtn').addEventListener('click', function() {
    const interfaceName = document.getElementById('interfaceName').value;
    const action = document.getElementById('netconfAction').value;
    const output = `Action ${action} exécutée sur l'interface ${interfaceName}`;
    document.getElementById('netconfOutput').textContent = output;
});



// Fonction pour récupérer les données dynamiques
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
            cell.textContent = 'Aucune donnée disponible';
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