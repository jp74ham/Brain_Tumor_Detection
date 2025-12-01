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
      <div class="record-image">
        <img src="${record.image_url}" alt="${escapeHtml(displayLabel)}" class="mri-thumbnail" />
      </div>
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
        
      </div>
      
    `;
    
    recordsContainer.appendChild(card);
  });

    // Attach click handlers to thumbnails (delegation alternative)
    const thumbnails = recordsContainer.querySelectorAll('.mri-thumbnail');
    thumbnails.forEach(img => {
      img.addEventListener('click', function(e) {
        showImageModal(this.src, this.alt);
      });
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

// Image modal helpers
function showImageModal(src, alt) {
  // create modal if it doesn't exist
  let modal = document.getElementById('image-modal-overlay');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'image-modal-overlay';
    modal.innerHTML = `
      <div class="image-modal-backdrop" id="image-modal-backdrop">
        <button class="image-modal-close" id="image-modal-close" aria-label="Close image">×</button>
        <img class="image-modal-img" id="image-modal-img" src="" alt="" />
      </div>
    `;
    document.body.appendChild(modal);

    // events
    modal.addEventListener('click', function(e) {
      if (e.target.id === 'image-modal-overlay' || e.target.id === 'image-modal-backdrop') {
        hideImageModal();
      }
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') hideImageModal();
    });
    const closeBtn = modal.querySelector('#image-modal-close');
    closeBtn.addEventListener('click', hideImageModal);
  }

  const modalImg = document.getElementById('image-modal-img');
  modalImg.src = src;
  modalImg.alt = alt || '';
  modal.classList.add('active');
}

function hideImageModal() {
  const modal = document.getElementById('image-modal-overlay');
  if (modal) modal.classList.remove('active');
}
