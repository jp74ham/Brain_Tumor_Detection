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
