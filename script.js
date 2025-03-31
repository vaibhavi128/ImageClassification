document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');
    const identifyBtn = document.getElementById('identifyBtn');
    const resultName = document.getElementById('resultName');
    const resultAge = document.getElementById('resultAge');
    const resultImage = document.getElementById('resultImage');
    const resultConfidence = document.getElementById('resultConfidence');

    let selectedFile = null;

    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('active');
    }

    function unhighlight() {
        dropZone.classList.remove('active');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length) {
            handleFiles(e.target.files);
        }
    });

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFiles(files);
        }
    }

    function handleFiles(files) {
        const file = files[0];
        if (!file.type.match('image.*')) {
            showError('Please upload an image file (JPG, PNG)');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            showError('File size should be less than 5MB');
            return;
        }

        selectedFile = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            previewContainer.classList.remove('hidden');
            identifyBtn.classList.remove('hidden');
            resultContainer.classList.add('hidden');
            errorContainer.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        identifyBtn.classList.add('hidden');
        resultContainer.classList.add('hidden');
    }

    identifyBtn.addEventListener('click', function() {
        if (!selectedFile) {
            showError('No file selected');
            return;
        }

        // Show loading state
        identifyBtn.disabled = true;
        identifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';

        const formData = new FormData();
        formData.append('file', selectedFile);

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }

            // Display results
            resultName.textContent = data.name;
            resultAge.textContent = `${data.age} years old`;
            resultImage.src = data.image_url;
            resultConfidence.textContent = `Confidence: ${data.confidence}`;
            
            resultContainer.classList.remove('hidden');
        })
        .catch(error => {
            showError('Identification failed. Please try again.');
        })
        .finally(() => {
            identifyBtn.disabled = false;
            identifyBtn.innerHTML = '<i class="fas fa-search mr-2"></i> Identify Person';
        });
    });
});