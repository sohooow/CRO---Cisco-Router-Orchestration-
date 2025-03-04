// Envoi de la data au back-end
document.getElementById('executeBtn').addEventListener('click', async function () {
    await sendJsonData();  // Attendre la fin de sendJsonData()
    loadDynamicData();  // Puis exécuter loadDynamicData()
});

async function sendJsonData(){
    console.log(getData());
    
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];  
    if (!csrfToken) {
        console.error("Token CSRF introuvable !");
        return;
    }

    const output_body = document.querySelector('#Output p');

    try {
        const response = await fetch('http://localhost:8000/orchestration/json/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(getData()),
        });

        const data = await response.json();
        console.log('Réponse du serveur:', data);
        output_body.textContent = data.data || "Aucune réponse.";

    } catch (error) {
        console.error('Erreur:', error);
        output_body.textContent = "Erreur lors de l'exécution.";
    }
}

function printOutput() {
    const output = `Commande exécutée : ${command} (${action})`;
    document.getElementById('cliOutput').textContent = output;
}

// Récupérer la data
function getData() {
    const interfaceName = document.getElementById('interfaceName').value;
    const ipAddress = document.getElementById('ipAddress').value;
    const subnetMask = document.getElementById('SubnetMask').value;
    const subInterface = document.getElementById('SubInterface').value;
    const action = document.getElementById('Action').value;
    let mode = "cli";

    const selectedRadio = document.querySelector('input[name="flexRadioDefault"]:checked');

    // Vérifier quel radio est sélectionné et modifie le mode en fonction
    if (selectedRadio) {
        if (selectedRadio.id === "flexRadioDefault1") {
            mode = "cli";
        } else if (selectedRadio.id === "flexRadioDefault2") {
            mode = "netconf";
        }
    }

    const JsonData = {
        interfaceName: interfaceName,
        ipAddress: ipAddress,
        subnetMask: subnetMask,
        subInterface: subInterface,
        action: action,
        mode : mode,
    };
    
    if (!interfaceName || !ipAddress || !subnetMask || !subInterface || !action || !mode) {
        console.error("Invalid data:", { interfaceName, ipAddress, subnetMask, subInterface, action, mode });
    }
    
    return JsonData;
}

// Fonction pour récupérer les interfaces dynamiquement
function loadDynamicData() {
    
    // Trouver le corps du tableau
    const tbody = document.querySelector('#interfaceTable tbody');
    
    tbody.innerHTML = '';
    
    // Afficher le spinner de chargement (remplacer le contenu par le spinner)
    const loadingRow = document.getElementById('loadingRow');
    loadingRow.style.display = 'table-row'; // Afficher le spinner
    
    // Effectuer une requête AJAX pour obtenir les données
    fetch('/orchestration/dynamic-output/')
    .then(response => response.json())  // Convertir la réponse en JSON
    .then(data => {
        // Masquer le spinner une fois les données chargées
        loadingRow.style.display = 'none';
        
        if (data && data.data && Array.isArray(data.data) && data.data.length > 0) {
            // Si les données sont présentes et sous forme de tableau non vide
            data.data.forEach(interface => {
                const row = document.createElement('tr');
                
                // Création des cellules
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
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.setAttribute('colspan', '4');
            cell.textContent = 'Aucune donnée disponible (vérifiez le VPN ou la connexion internet)';
            row.appendChild(cell);
            tbody.appendChild(row);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données:', error);
        
        // Masquer le spinner en cas d'erreur
        loadingRow.style.display = 'none';
        
        // En cas d'erreur réseau, afficher un message d'erreur
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.setAttribute('colspan', '4');
        cell.textContent = 'Erreur lors de la récupération des données. Veuillez réessayer.';
        row.appendChild(cell);
        tbody.appendChild(row);
    });
}

// Associer la fonction au bouton "Rafraîchir"
document.getElementById('refresh').addEventListener('click', loadDynamicData);

// Charger les données dynamiques lorsque la page est prête
document.addEventListener('DOMContentLoaded', loadDynamicData);

