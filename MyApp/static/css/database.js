const queryInput = document.getElementById('query-input');
const executeBtn = document.getElementById('execute-btn');
const resultsContainer = document.getElementById('results-container');
const sampleQueryBtns = document.querySelectorAll('.sample-query-btn');

// Handle sample query buttons
sampleQueryBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    queryInput.value = this.dataset.query;
  });
});

// Execute query
executeBtn.addEventListener('click', async function() {
  const query = queryInput.value.trim();
  
  if (!query) {
    alert('Please enter a query');
    return;
  }
  
  executeBtn.disabled = true;
  executeBtn.textContent = 'Executing...';
  resultsContainer.innerHTML = '<p class="loading">Executing query...</p>';
  
  try {
    const response = await fetch('/execute_query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: query })
    });
    
    const result = await response.json();
    
    if (result.success) {
      displayResults(result);
    } else {
      displayError(result.error);
    }
  } catch (error) {
    displayError('Network error: ' + error.message);
  } finally {
    executeBtn.disabled = false;
    executeBtn.textContent = 'Execute Query';
  }
});

function displayResults(result) {
  if (result.count === 0) {
    resultsContainer.innerHTML = '<p class="no-results">Query executed successfully but returned no results.</p>';
    return;
  }
  
  let html = `
    <div class="results-info">
      Query executed successfully. Returned ${result.count} row${result.count !== 1 ? 's' : ''}.
    </div>
    <div style="overflow-x: auto;">
      <table class="results-table">
        <thead>
          <tr>
            ${result.columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
  `;
  
  result.data.forEach(row => {
    html += '<tr>';
    result.columns.forEach(col => {
      const value = row[col];
      html += `<td>${value !== null && value !== undefined ? escapeHtml(String(value)) : '<em>NULL</em>'}</td>`;
    });
    html += '</tr>';
  });
  
  html += `
        </tbody>
      </table>
    </div>
  `;
  
  resultsContainer.innerHTML = html;
}

function displayError(errorMessage) {
  resultsContainer.innerHTML = `
    <div class="error-message">
      <strong>Error:</strong> ${escapeHtml(errorMessage)}
    </div>
  `;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Allow Ctrl+Enter to execute query
queryInput.addEventListener('keydown', function(e) {
  if (e.ctrlKey && e.key === 'Enter') {
    executeBtn.click();
  }
});

// --- Patient form handling ---
const patientForm = document.getElementById('patient-form');
const submitPatientBtn = document.getElementById('submit-patient-btn');
const patientResponse = document.getElementById('patient-response');

if (submitPatientBtn) {
  submitPatientBtn.addEventListener('click', async function() {
    patientResponse.innerHTML = '';

    const fileInput = document.getElementById('mri-file');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      patientResponse.innerHTML = '<div class="error-message">Please select an MRI image to upload.</div>';
      return;
    }

    submitPatientBtn.disabled = true;
    submitPatientBtn.textContent = 'Saving...';

    const formData = new FormData(patientForm);

    try {
      const resp = await fetch('/submit_patient_scan', {
        method: 'POST',
        body: formData
      });

      const data = await resp.json();
      if (resp.ok && data.success) {
        let html = `<div class="results-info">Patient saved. Patient ID: <strong>${data.patient_id}</strong>. Scan ID: <strong>${data.scan_id}</strong>.</div>`;
        html += `<div style="margin-top:8px;"><button id="predict-btn" class="secondary-button">Run Model Prediction</button></div>`;
        patientResponse.innerHTML = html;

        // Attach prediction handler
        document.getElementById('predict-btn').addEventListener('click', async function() {
          this.disabled = true;
          this.textContent = 'Predicting...';
          try {
            const presp = await fetch('/predict_scan', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ scan_id: data.scan_id })
            });
            const pres = await presp.json();
            if (pres.success) {
              patientResponse.innerHTML += `<div class="results-info" style="margin-top:8px;">Prediction: <strong>${pres.predicted_label}</strong> (confidence: ${pres.confidence})</div>`;
            } else {
              patientResponse.innerHTML += `<div class="error-message">Prediction failed: ${pres.error}</div>`;
            }
          } catch (err) {
            patientResponse.innerHTML += `<div class="error-message">Network error during prediction: ${err.message}</div>`;
          } finally {
            this.disabled = false;
            this.textContent = 'Run Model Prediction';
          }
        });

      } else {
        patientResponse.innerHTML = `<div class="error-message">Error saving patient: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (err) {
      patientResponse.innerHTML = `<div class="error-message">Network error: ${err.message}</div>`;
    } finally {
      submitPatientBtn.disabled = false;
      submitPatientBtn.textContent = 'Save Patient + Upload Scan';
    }
  });
}
