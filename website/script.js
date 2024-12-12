// Initialize camera feed
const cameraFeed = document.getElementById('cameraFeed');
const cameraStatus = document.getElementById('cameraStatus');

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    cameraFeed.srcObject = stream;
    cameraStatus.textContent = 'CONNECTED';
    cameraStatus.classList.replace('text-warning', 'text-success');
  })
  .catch((error) => {
    console.error('Camera access error:', error);
    cameraStatus.textContent = 'NOT CONNECTED';
    cameraStatus.classList.replace('text-warning', 'text-danger');
  });

// File upload functionality
const fileInput = document.getElementById('fileInput');
const uploadedImage = document.getElementById('uploadedImage');
const sourceStatus = document.getElementById('sourceStatus');

fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedImage.src = e.target.result;
      uploadedImage.classList.remove('d-none');
      sourceStatus.textContent = 'FOUND';
      sourceStatus.classList.replace('text-warning', 'text-success');
    };
    reader.readAsDataURL(file);
  } else {
    sourceStatus.textContent = 'NOT FOUND';
    sourceStatus.classList.replace('text-warning', 'text-danger');
  }
});

// Robot control
document.querySelectorAll('.btn').forEach((button) => {
  button.addEventListener('click', () => {
    console.log(`Button ID clicked: ${button.id}`);
  });
});
