let selectedFile = null;
let uploadedFilePath = null;

const fileInput = document.getElementById('mri-upload');
const fileChosen = document.getElementById('file-chosen');
const previewImage = document.getElementById('preview-image');
const saveBtn = document.getElementById('save-btn');
const submitBtn = document.getElementById('submit-btn');
const cancelBtn = document.getElementById('cancel-btn');
const resultImage = document.getElementById('result-image');
const tumorResult = document.getElementById('tumor-result');
const typeResult = document.getElementById('type-result');

fileInput.addEventListener('change', function(e) {
  const file = e.target.files[0];
  if (file) {
    selectedFile = file;
    fileChosen.textContent = file.name;
    
    const reader = new FileReader();
    reader.onload = function(e) {
      previewImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    saveBtn.disabled = false;
  }
});

saveBtn.addEventListener('click', async function() {
  if (!selectedFile) {
    alert('Please select a file first');
    return;
  }
  
  const formData = new FormData();
  formData.append('mri-upload', selectedFile);
  
  try {
    saveBtn.disabled = true;
    saveBtn.querySelector('.choose-file').textContent = 'Saving...';
    
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
      uploadedFilePath = result.filepath;
      submitBtn.disabled = false;
      alert('File saved successfully!');
    } else {
      alert('Error: ' + result.error);
      saveBtn.disabled = false;
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while uploading the file');
    saveBtn.disabled = false;
  } finally {
    saveBtn.querySelector('.choose-file').textContent = 'Save';
  }
});

submitBtn.addEventListener('click', async function() {
  if (!uploadedFilePath) {
    alert('Please save the file first');
    return;
  }
  
  try {
    submitBtn.disabled = true;
    submitBtn.querySelector('.label-2').textContent = 'Processing...';
    
    // Simulate classification (replace with actual API call)
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Display results
    resultImage.style.backgroundImage = `url(${uploadedFilePath})`;
    tumorResult.textContent = 'Yes';
    typeResult.textContent = 'Glioma';
    
    alert('Classification complete!');
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred during classification');
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector('.label-2').textContent = 'Submit';
  }
});

cancelBtn.addEventListener('click', function() {
  selectedFile = null;
  uploadedFilePath = null;
  fileInput.value = '';
  fileChosen.textContent = 'No File Chosen';
  previewImage.src = 'https://c.animaapp.com/DnqGvymX/img/component-placeholder-image-2@2x.png';
  resultImage.style.backgroundImage = 'url(https://c.animaapp.com/DnqGvymX/img/image-4.svg)';
  tumorResult.textContent = '-';
  typeResult.textContent = '-';
  saveBtn.disabled = true;
  submitBtn.disabled = true;
});

// Image modal functionality for query results
document.addEventListener('DOMContentLoaded', function() {
  // Create image modal element
  const modal = document.createElement('div');
  modal.className = 'image-modal';
  modal.innerHTML = `
    <span class="image-modal-close">&times;</span>
    <img src="" alt="Enlarged view">
  `;
  document.body.appendChild(modal);
  
  const modalImg = modal.querySelector('img');
  const closeBtn = modal.querySelector('.image-modal-close');
  
  // Add click handlers to all query images
  document.querySelectorAll('.query-image').forEach(img => {
    img.addEventListener('click', function() {
      modal.classList.add('active');
      modalImg.src = this.src;
      modalImg.alt = this.alt;
    });
  });
  
  // Close modal on click
  closeBtn.addEventListener('click', function() {
    modal.classList.remove('active');
  });
  
  // Close modal on background click
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      modal.classList.remove('active');
    }
  });
  
  // Close modal on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      modal.classList.remove('active');
    }
  });

  // Create login modal
  const loginModal = document.createElement('div');
  loginModal.className = 'login-modal';
  loginModal.innerHTML = `
    <div class="login-modal-content">
      <div class="login-modal-header">
        <h2>Database Login</h2>
        <p>Enter your credentials to access the database query interface</p>
      </div>
      <form class="login-form" id="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input type="text" id="username" name="username" required autocomplete="username">
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" name="password" required autocomplete="current-password">
        </div>
        <div class="login-error" id="login-error"></div>
        <div class="login-actions">
          <button type="button" class="login-cancel" id="login-cancel">Cancel</button>
          <button type="submit" class="login-submit" id="login-submit">Login</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(loginModal);

  // Create patient login modal
  const patientLoginModal = document.createElement('div');
  patientLoginModal.className = 'login-modal';
  patientLoginModal.innerHTML = `
    <div class="login-modal-content">
      <div class="login-modal-header">
        <h2>Patient Login</h2>
        <p>Enter your Patient ID to view your medical records</p>
      </div>
      <form class="login-form" id="patient-login-form">
        <div class="form-group">
          <label for="patient-id">Patient ID</label>
          <input type="text" id="patient-id" name="patient_id" required placeholder="Enter your patient ID">
        </div>
        <div class="login-error" id="patient-login-error"></div>
        <div class="login-actions">
          <button type="button" class="login-cancel" id="patient-login-cancel">Cancel</button>
          <button type="submit" class="login-submit" id="patient-login-submit">Access Records</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(patientLoginModal);

  const loginBtn = document.getElementById('admin-login-btn');
  const loginForm = document.getElementById('login-form');
  const loginCancelBtn = document.getElementById('login-cancel');
  const loginSubmitBtn = document.getElementById('login-submit');
  const loginError = document.getElementById('login-error');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  const patientLoginBtn = document.getElementById('patient-login-btn');
  const patientLoginForm = document.getElementById('patient-login-form');
  const patientLoginCancelBtn = document.getElementById('patient-login-cancel');
  const patientLoginSubmitBtn = document.getElementById('patient-login-submit');
  const patientLoginError = document.getElementById('patient-login-error');
  const patientIdInput = document.getElementById('patient-id');

  // Open admin login modal
  if (loginBtn) {
    loginBtn.addEventListener('click', function() {
      loginModal.classList.add('active');
      usernameInput.focus();
      loginError.classList.remove('active');
    });
  }

  // Open patient login modal
  if (patientLoginBtn) {
    patientLoginBtn.addEventListener('click', function() {
      patientLoginModal.classList.add('active');
      patientIdInput.focus();
      patientLoginError.classList.remove('active');
    });
  }

  // Close admin login modal
  loginCancelBtn.addEventListener('click', function() {
    loginModal.classList.remove('active');
    loginForm.reset();
    loginError.classList.remove('active');
  });

  // Close patient login modal
  patientLoginCancelBtn.addEventListener('click', function() {
    patientLoginModal.classList.remove('active');
    patientLoginForm.reset();
    patientLoginError.classList.remove('active');
  });

  // Close on background click - admin
  loginModal.addEventListener('click', function(e) {
    if (e.target === loginModal) {
      loginModal.classList.remove('active');
      loginForm.reset();
      loginError.classList.remove('active');
    }
  });

  // Close on background click - patient
  patientLoginModal.addEventListener('click', function(e) {
    if (e.target === patientLoginModal) {
      patientLoginModal.classList.remove('active');
      patientLoginForm.reset();
      patientLoginError.classList.remove('active');
    }
  });

  // Handle admin login form submission
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = usernameInput.value;
    const password = passwordInput.value;
    
    loginSubmitBtn.disabled = true;
    loginSubmitBtn.textContent = 'Logging in...';
    loginError.classList.remove('active');
    
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      const result = await response.json();
      
      if (result.success) {
        window.location.href = result.redirect;
      } else {
        loginError.textContent = result.error || 'Invalid credentials';
        loginError.classList.add('active');
      }
    } catch (error) {
      loginError.textContent = 'Network error: ' + error.message;
      loginError.classList.add('active');
    } finally {
      loginSubmitBtn.disabled = false;
      loginSubmitBtn.textContent = 'Login';
    }
  });

  // Handle patient login form submission
  patientLoginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const patientId = patientIdInput.value.trim();
    
    patientLoginSubmitBtn.disabled = true;
    patientLoginSubmitBtn.textContent = 'Accessing...';
    patientLoginError.classList.remove('active');
    
    try {
      const response = await fetch('/patient_login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ patient_id: patientId })
      });
      
      const result = await response.json();
      
      if (result.success) {
        window.location.href = result.redirect;
      } else {
        patientLoginError.textContent = result.error || 'Invalid Patient ID';
        patientLoginError.classList.add('active');
      }
    } catch (error) {
      patientLoginError.textContent = 'Network error: ' + error.message;
      patientLoginError.classList.add('active');
    } finally {
      patientLoginSubmitBtn.disabled = false;
      patientLoginSubmitBtn.textContent = 'Access Records';
    }
  });
});
