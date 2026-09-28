// =====================================================
// StudySnap - Client-Side JavaScript
// Simple & clear code for file selection handling
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const processBtn = document.getElementById('processBtn');
    const uploadForm = document.getElementById('uploadForm');
    const statusMessage = document.getElementById('statusMessage');

    // Helper: Format bytes to human readable format (KB, MB)
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Update UI when a file is selected
    function handleFileSelected(file) {
        if (!file) return;

        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        fileInfo.classList.remove('hidden');
        processBtn.disabled = false;
        statusMessage.classList.add('hidden');
    }

    // Reset UI when file is removed
    function resetFileSelection() {
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        processBtn.disabled = true;
        statusMessage.classList.add('hidden');
    }

    // 1. File input change event
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
        }
    });

    // 2. Remove file button event
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileSelection();
    });

    // 3. Drag and Drop styling events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    // Handle dropped file
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt.files && dt.files.length > 0) {
            fileInput.files = dt.files;
            handleFileSelected(dt.files[0]);
        }
    });

    // 4. Form Submit Preview (No AI yet - placeholder for upcoming step)
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const selectedFile = fileInput.files[0];

        if (!selectedFile) {
            alert('Please select a file first!');
            return;
        }

        // Show friendly confirmation message
        statusMessage.className = 'status-message success';
        statusMessage.textContent = `✅ "${selectedFile.name}" selected! Your Flask setup is ready for AI & PDF extraction in the next step.`;
        statusMessage.classList.remove('hidden');
    });
});
