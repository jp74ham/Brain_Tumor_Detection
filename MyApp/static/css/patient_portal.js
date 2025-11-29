const recordsContainer = document.getElementById('records-container');

// Load patient records on page load
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const response = await fetch('/patient_records');
    const result = await response.json();
    
    if (result.success) {
      displayRecords(result.records);
    } else {
      displayError(result.error || 'Failed to load records');
    }
  } catch (error) {
    displayError('Network error: ' + error.message);
  }
});

function displayRecords(records) {
  if (records.length === 0) {
    recordsContainer.innerHTML = '<p class="no-records">No MRI scan records found for your patient ID.</p>';
    return;
  }
  
  recordsContainer.innerHTML = '';
  
  records.forEach(record => {
    const card = document.createElement('div');
    card.className = 'record-card';
    
    const labelClass = record.label || 'unknown';
    const displayLabel = record.label ? record.label.replace(/_/g, ' ') : 'Unknown';
    
    card.innerHTML = `
      <div class="record-header">
        <span class="record-label ${labelClass}">${escapeHtml(displayLabel)}</span>
        <span class="scan-date">${escapeHtml(record.scan_date || 'N/A')}</span>
      </div>
      <div class="record-details">
        <div class="detail-row">
          <span class="detail-label">Age:</span>
          <span class="detail-value">${escapeHtml(String(record.age || 'N/A'))}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Gender:</span>
          <span class="detail-value">${escapeHtml(record.gender || 'N/A')}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Hospital Unit:</span>
          <span class="detail-value">${escapeHtml(record.hospital_unit || 'N/A')}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Image Size:</span>
          <span class="detail-value">${escapeHtml(String(record.orig_width || 'N/A'))} × ${escapeHtml(String(record.orig_height || 'N/A'))}</span>
        </div>
      </div>
      <div class="record-stats">
        Processed: ${escapeHtml(String(record.proc_width || 'N/A'))} × ${escapeHtml(String(record.proc_height || 'N/A'))} | 
        Mean Pixel: ${record.mean_pixel ? Number(record.mean_pixel).toFixed(4) : 'N/A'} | 
        Std: ${record.std_pixel ? Number(record.std_pixel).toFixed(4) : 'N/A'}
      </div>
    `;
    
    recordsContainer.appendChild(card);
  });
}

function displayError(errorMessage) {
  recordsContainer.innerHTML = `
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
