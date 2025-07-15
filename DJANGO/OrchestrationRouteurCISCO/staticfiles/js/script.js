// Send data to the backend when the execute button is clicked
const executeBtn = document.getElementById('executeBtn');
if (executeBtn) {
  executeBtn.addEventListener('click', async function () {
    await sendJsonData();
    loadDynamicData();
  });
}

// Send the form data as JSON to the backend API endpoint
async function sendJsonData() {
  const data = getData();
  if (!data) {
    console.error("Invalid data, request not sent");
    return;
  }

  console.log(data);

  // Retrieve CSRF token from cookies
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  if (!csrfToken) {
    console.error("CSRF token not found!");
    return;
  }

  const output_body = document.querySelector('#Output p');

  try {
    // Send POST request to backend
    const response = await fetch('http://localhost:8000/orchestration/send-subinterface/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(getData()),
    });

    if (response.status === 500) {
      window.location.href = "/500/";
      return;
    }

    const result = await response.json();
    console.log('Server response:', result);

    // Display result or error in the output area
    if (result.error) {
      if (output_body) output_body.textContent = result.error || "Execution error.";
    } else {
      if (output_body) output_body.textContent = result.message || "Action successful.";
    }

  } catch (error) {
    console.error('Error:', error);
    if (output_body) output_body.textContent = "Execution error.";
  }
}

// Print the last executed command and action in the CLI output area
function printOutput() {
  const output = `Executed command: ${command} (${action})`;
  const cliOutput = document.getElementById('cliOutput');
  if (cliOutput) cliOutput.textContent = output;
}

// Collect form data and return it as a JSON object
function getData() {
  const interfaceName = document.getElementById('interfaceName')?.value;
  const ipAddress = document.getElementById('ipAddress')?.value;
  const subnetMask = document.getElementById('SubnetMask')?.value;
  const subInterface = document.getElementById('SubInterface')?.value;
  const action = document.getElementById('Action')?.value;
  let mode = "cli";

  // Determine the selected mode (CLI or NETCONF)
  const selectedRadio = document.querySelector('input[name="flexRadioDefault"]:checked');
  if (selectedRadio) {
    if (selectedRadio.id === "flexRadioDefault1") {
      mode = "cli";
    } else if (selectedRadio.id === "flexRadioDefault2") {
      mode = "netconf";
    }
  }

  // Log error if any required field is missing
  if (!interfaceName || !ipAddress || !subnetMask || !subInterface || !action || !mode) {
    console.error("Invalid data:", { interfaceName, ipAddress, subnetMask, subInterface, action, mode });
  }

  // Return the collected data as a JSON object
  return {
    interfaceName: interfaceName,
    ipAddress: ipAddress,
    subnetMask: subnetMask,
    subInterface: subInterface,
    action: action,
    mode: mode,
  };
}

// Fetch and display the list of interfaces in the table
function loadDynamicData() {
  const tbody = document.querySelector('#interfaceTable tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  const loadingRow = document.getElementById('loadingRow');
  if (loadingRow) loadingRow.style.display = 'table-row';

  fetch('http://localhost:8000/orchestration/dynamic-output/')
    .then(response => {
      if (!response.ok) {
        if (response.status === 500) {
          window.location.href = "/500/";
          return;
        }
        throw new Error(`HTTP error: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (!data) return;
      if (loadingRow) loadingRow.style.display = 'none';

      // Populate the table with interface data, skipping deleted interfaces
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
        // Show a message if no data is available
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.setAttribute('colspan', '4');
        cell.textContent = 'No data available (check VPN or internet connection)';
        row.appendChild(cell);
        tbody.appendChild(row);
      }
    })
    .catch(error => {
      // Handle fetch errors and display a message
      console.error('Error fetching data:', error);
      if (loadingRow) loadingRow.style.display = 'none';

      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.setAttribute('colspan', '4');
      cell.textContent = 'Error fetching data. Please try again.';
      row.appendChild(cell);
      tbody.appendChild(row);
    });
}

// Refresh the interface table when the refresh button is clicked
const refreshBtn = document.getElementById('refresh');
if (refreshBtn) {
  refreshBtn.addEventListener('click', loadDynamicData);
}

// Initialize the interface table and Lottie animation on page load
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