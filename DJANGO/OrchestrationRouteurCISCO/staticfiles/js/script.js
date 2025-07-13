// Send data to the back-end
document.getElementById('executeBtn').addEventListener('click', async function () {
    await sendJsonData();  // Wait for sendJsonData() to finish
    loadDynamicData();  // Then execute loadDynamicData()
});

async function sendJsonData() {
    const data = getData();
    if (!data) {
        console.error("Invalid data, request not sent");
        return;
    }

    console.log(data);

    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    if (!csrfToken) {
        console.error("CSRF token not found!");
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
        console.log('Server response:', result);

        if (result.error) {
            output_body.textContent = result.error || "Error during execution.";
        } else {
            output_body.textContent = result.message || "Action successful.";
        }

    } catch (error) {
        console.error('Error:', error);
        output_body.textContent = "Error during execution.";
    }
}

function printOutput() {
    const output = `Command executed: ${command} (${action})`;
    document.getElementById('cliOutput').textContent = output;
}

// Retrieve the data
function getData() {
    const interfaceName = document.getElementById('interfaceName').value;
    const ipAddress = document.getElementById('ipAddress').value;
    const subnetMask = document.getElementById('SubnetMask').value;
    const subInterface = document.getElementById('SubInterface').value;
    const action = document.getElementById('Action').value;
    let mode = "cli";

    const selectedRadio = document.querySelector('input[name="flexRadioDefault"]:checked');

    // Check which radio is selected and update the mode accordingly
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
        mode: mode,
    };

    return JsonData;
}

// Function to fetch interfaces dynamically
function loadDynamicData() {

    // Find the table body
    const tbody = document.querySelector('#interfaceTable tbody');

    tbody.innerHTML = '';

    // Show the loading spinner (replace the content with the spinner)
    const loadingRow = document.getElementById('loadingRow');
    loadingRow.style.display = 'table-row'; // Show the spinner

    // Make an AJAX request to get the data
    fetch('/orchestration/dynamic-output/')
        .then(response => response.json())  // Convert the response to JSON
        .then(data => {
            // Hide the spinner once the data is loaded
            loadingRow.style.display = 'none';

            if (data && data.data && Array.isArray(data.data) && data.data.length > 0) {
                // If data is available and it's a non-empty array
                data.data.forEach(interface => {

                    if (interface.status.trim().toLowerCase() !== "deleted") {

                        const row = document.createElement('tr');

                        // Create the table cells
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

                        // Add the row to the table
                        tbody.appendChild(row);
                    }
                });
            } else {
                // If no data is available, show a message
                const row = document.createElement('tr');
                const cell = document.createElement('td');
                cell.setAttribute('colspan', '4');
                cell.textContent = 'No data available (check VPN or internet connection)';
                row.appendChild(cell);
                tbody.appendChild(row);
            }
        })
        .catch(error => {
            console.error('Error while retrieving data:', error);

            // Hide spinner in case of error
            loadingRow.style.display = 'none';

            // On network error, show error message
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.setAttribute('colspan', '4');
            cell.textContent = 'Error while retrieving data. Please try again.';
            row.appendChild(cell);
            tbody.appendChild(row);
        });
}

// Attach the function to the "Refresh" button
document.getElementById('refresh').addEventListener('click', loadDynamicData);

// Load dynamic data when the page is ready
document.addEventListener('DOMContentLoaded', loadDynamicData);



// Either a client-side framework that communicates with the back-end using JSON (no HTML), the framework handles the requests
// Or use HTMX, only using HTTP and HTML. Send form data to the back-end, and the back-end returns HTML
// Reorganize the front (file structure) and server communication

// HTMX: Django returns the table in the view

// Avoid uppercase letters in element IDs

// Connect the back-end with the front-end
