// Envoi de la data au back-end
const executeBtn = document.getElementById('executeBtn');
if (executeBtn) {
  executeBtn.addEventListener('click', async function () {
    await sendJsonData();
    loadDynamicData();
  });
}

async function sendJsonData(){
  const data = getData();
  if (!data) {
    console.error("Données invalides, requête non envoyée");
    return;
  }

  console.log(data);

  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  if (!csrfToken) {
    console.error("Token CSRF introuvable !");
    return;
  }

  const output_body = document.querySelector('#Output p');

  try {
    const response = await fetch('http://localhost:8000/orchestration/send-subinterface/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(getData()),
    });

    const result = await response.json();
    console.log('Réponse du serveur:', result);

    if (result.error) {
      if (output_body) output_body.textContent = result.error || "Erreur lors de l'exécution.";
    } else {
      if (output_body) output_body.textContent = result.message || "Action réussie.";
    }

  } catch (error) {
    console.error('Erreur:', error);
    if (output_body) output_body.textContent = "Erreur lors de l'exécution.";
  }
}

function printOutput() {
  const output = `Commande exécutée : ${command} (${action})`;
  const cliOutput = document.getElementById('cliOutput');
  if (cliOutput) cliOutput.textContent = output;
}

function getData() {
  const interfaceName = document.getElementById('interfaceName')?.value;
  const ipAddress = document.getElementById('ipAddress')?.value;
  const subnetMask = document.getElementById('SubnetMask')?.value;
  const subInterface = document.getElementById('SubInterface')?.value;
  const action = document.getElementById('Action')?.value;
  let mode = "cli";

  const selectedRadio = document.querySelector('input[name="flexRadioDefault"]:checked');

  if (selectedRadio) {
    if (selectedRadio.id === "flexRadioDefault1") {
      mode = "cli";
    } else if (selectedRadio.id === "flexRadioDefault2") {
      mode = "netconf";
    }
  }

  if (!interfaceName || !ipAddress || !subnetMask || !subInterface || !action || !mode) {
    console.error("Invalid data:", { interfaceName, ipAddress, subnetMask, subInterface, action, mode });
  }

  const JsonData = {
    interfaceName: interfaceName,
    ipAddress: ipAddress,
    subnetMask: subnetMask,
    subInterface: subInterface,
    action: action,
    mode : mode,
  };

  return JsonData;
}

function loadDynamicData() {
  const tbody = document.querySelector('#interfaceTable tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  const loadingRow = document.getElementById('loadingRow');
  if (loadingRow) loadingRow.style.display = 'table-row';

  fetch('/orchestration/dynamic-output/')
  .then(response => response.json())
  .then(data => {
    if (loadingRow) loadingRow.style.display = 'none';

    if (data && data.data && Array.isArray(data.data) && data.data.length > 0) {
      data.data.forEach(interface => {
        if (interface.status.trim().toLowerCase() !== "deleted") {
          const row = document.createElement('tr');
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
          tbody.appendChild(row);
        }
      });
    } else {
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
    if (loadingRow) loadingRow.style.display = 'none';

    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.setAttribute('colspan', '4');
    cell.textContent = 'Erreur lors de la récupération des données. Veuillez réessayer.';
    row.appendChild(cell);
    tbody.appendChild(row);
  });
}

const refreshBtn = document.getElementById('refresh');
if (refreshBtn) {
  refreshBtn.addEventListener('click', loadDynamicData);
}

document.addEventListener('DOMContentLoaded', () => {
  loadDynamicData();

  const animationContainer = document.querySelector('.lottie-animation');
  if (animationContainer) {
    lottie.loadAnimation({
      container: animationContainer,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: 'https://lottie.host/d987597c-7676-4424-8817-7fca6dc1a33e/BVrFXsaeui.json'
    });
  }
});
