// =====================================================
// StudySnap - Client-Side JavaScript
// Handles file upload interactions and theme toggling
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

    // Theme Switcher Elements
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeToggleIcon = document.getElementById('themeToggleIcon');
    const themeToggleLabel = document.getElementById('themeToggleLabel');

    // =========================================
    // Theme Management (Industrial vs Swiss Poster)
    // =========================================
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('studysnap-theme', theme);
        
        if (theme === 'poster') {
            if (themeToggleIcon) themeToggleIcon.textContent = '🔴';
            if (themeToggleLabel) themeToggleLabel.textContent = 'POSTER RED';
        } else {
            if (themeToggleIcon) themeToggleIcon.textContent = '⚡';
            if (themeToggleLabel) themeToggleLabel.textContent = 'INDUSTRIAL';
        }
    }

    // Load saved theme or default to 'industrial'
    const savedTheme = localStorage.getItem('studysnap-theme') || 'industrial';
    setTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'industrial';
            const nextTheme = currentTheme === 'industrial' ? 'poster' : 'industrial';
            setTheme(nextTheme);
        });
    }

    // =========================================
    // File Handling
    // =========================================
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

    // 4. Form Submit Handler
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const selectedFile = fileInput.files[0];

        if (!selectedFile) {
            alert('Please select a file first!');
            return;
        }

        // Show friendly confirmation message
        statusMessage.className = 'status-message success';
        statusMessage.innerHTML = '<strong>[SYS.EXECUTE]</strong> "' + selectedFile.name + '" locked & loaded. Backend Flask pipeline ready for extraction.';
        statusMessage.classList.remove('hidden');
    });
});
