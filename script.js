// Comparison Slider Function
function createComparisonSlider(beforeSrc, afterSrc, container) {
    container.innerHTML = `
        <div class="comparison-container">
            <img src="${beforeSrc}" class="comparison-before">
            <div class="comparison-after" style="clip-path: inset(0 50% 0 0);">
                <img src="${afterSrc}">
            </div>
            <div class="comparison-slider" style="left: 50%;"></div>
            <div class="comparison-label before">BEFORE</div>
            <div class="comparison-label after">AFTER</div>
        </div>
    `;
    
    const slider = container.querySelector('.comparison-slider');
    const afterDiv = container.querySelector('.comparison-after');
    const compContainer = container.querySelector('.comparison-container');
    
    let isDragging = false;
    
    slider.addEventListener('mousedown', () => isDragging = true);
    document.addEventListener('mouseup', () => isDragging = false);
    
    compContainer.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const rect = compContainer.getBoundingClientRect();
        let x = e.clientX - rect.left;
        x = Math.max(0, Math.min(x, rect.width));
        const percent = (x / rect.width) * 100;
        slider.style.left = percent + '%';
        afterDiv.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
    });
    
    compContainer.addEventListener('click', (e) => {
        const rect = compContainer.getBoundingClientRect();
        let x = e.clientX - rect.left;
        const percent = (x / rect.width) * 100;
        slider.style.left = percent + '%';
        afterDiv.style.clipPath = `inset(0 ${100 - percent}% 0 0)`;
    });
}

function addTaskLog(type, message) {
    const log = document.getElementById('tasksLog');
    if (!log) return;
    const entry = document.createElement('div');
    const time = new Date().toLocaleTimeString();
    entry.className = 'text-pixelMint';
    entry.textContent = `[${time}] ${type}: ${message}`;
    log.insertBefore(entry, log.firstChild);
    while (log.children.length > 50) log.removeChild(log.lastChild);
}

// Tab switching
function switchTab(tab) {
    const imageTab = document.getElementById('imageTab');
    const videoTab = document.getElementById('videoTab');
    const multiTab = document.getElementById('multiTab');
    const facesTab = document.getElementById('facesTab');
    const tasksTab = document.getElementById('tasksTab');
    const historyTab = document.getElementById('historyTab');
    const tabs = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    imageTab.classList.add('hidden');
    videoTab.classList.add('hidden');
    multiTab.classList.add('hidden');
    facesTab.classList.add('hidden');
    tasksTab.classList.add('hidden');
    historyTab.classList.add('hidden');
    
    if (tab === 'image') {
        imageTab.classList.remove('hidden');
        tabs[0].classList.add('active');
    } else if (tab === 'video') {
        videoTab.classList.remove('hidden');
        tabs[1].classList.add('active');
    } else if (tab === 'multi') {
        multiTab.classList.remove('hidden');
        tabs[2].classList.add('active');
    } else if (tab === 'faces') {
        facesTab.classList.remove('hidden');
        tabs[3].classList.add('active');
        loadSavedFaces();
    } else if (tab === 'tasks') {
        tasksTab.classList.remove('hidden');
        tabs[4].classList.add('active');
        loadTasks();
    } else if (tab === 'history') {
        historyTab.classList.remove('hidden');
        tabs[5].classList.add('active');
        loadHistory();
    }
}

function switchHistoryTab(type) {
    const imgDiv = document.getElementById('historyImages');
    const vidDiv = document.getElementById('historyVideos');
    const tabs = document.querySelectorAll('#historyTab .tab-btn');
    
    tabs.forEach(t => t.classList.remove('active'));
    
    if (type === 'images') {
        imgDiv.classList.remove('hidden');
        vidDiv.classList.add('hidden');
        tabs[0].classList.add('active');
    } else {
        imgDiv.classList.add('hidden');
        vidDiv.classList.remove('hidden');
        tabs[1].classList.add('active');
    }
}

// Toggle enhance options
window.toggleEnhanceOptions = function(type) {
    let checkboxId, optionsId;
    
    if (type === 'image') {
        checkboxId = 'enhanceCheckbox';
        optionsId = 'enhanceOptionsImage';
    } else if (type === 'video') {
        checkboxId = 'enhanceVideoCheckbox';
        optionsId = 'enhanceOptionsVideo';
    } else if (type === 'multi') {
        checkboxId = 'enhanceMultiCheckbox';
        optionsId = 'enhanceOptionsMulti';
    }
    
    const checkbox = document.getElementById(checkboxId);
    const options = document.getElementById(optionsId);
    
    if (checkbox.checked) {
        options.classList.remove('hidden');
    } else {
        options.classList.add('hidden');
    }
};

// File input setup with preview and remove
const setupFileInput = (inputId, textId, previewId) => {
    const input = document.getElementById(inputId);
    const zone = document.getElementById(inputId.replace('Input', 'Zone'));
    const previewEl = document.getElementById(previewId);
    
    input.addEventListener('change', function(e) {
        previewEl.innerHTML = '';
        
        if (this.files.length === 0) {
            zone.classList.remove('has-files');
            previewEl.classList.add('hidden');
            return;
        }
        
        zone.classList.add('has-files');
        previewEl.classList.remove('hidden');
        
        // Show previews with remove button
        Array.from(this.files).forEach((file, index) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'preview-item';
            
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.type = 'button';
                    removeBtn.className = 'preview-remove';
                    removeBtn.innerHTML = '×';
                    removeBtn.onclick = (ev) => {
                        ev.stopPropagation();
                        wrapper.remove();
                        removeFileFromInput(inputId, index);
                        if (input.files.length === 0) {
                            zone.classList.remove('has-files');
                            previewEl.classList.add('hidden');
                        }
                    };
                    
                    wrapper.appendChild(img);
                    wrapper.appendChild(removeBtn);
                    previewEl.appendChild(wrapper);
                };
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.muted = true;
                video.onloadeddata = () => {
                    video.currentTime = 1;
                };
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'preview-remove';
                removeBtn.innerHTML = '×';
                removeBtn.onclick = (ev) => {
                    ev.stopPropagation();
                    wrapper.remove();
                    removeFileFromInput(inputId, index);
                    if (input.files.length === 0) {
                        zone.classList.remove('has-files');
                        previewEl.classList.add('hidden');
                    }
                };
                
                wrapper.appendChild(video);
                wrapper.appendChild(removeBtn);
                previewEl.appendChild(wrapper);
            }
        });
    });
    
    // Drag and drop
    if (zone) {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            zone.style.borderColor = '#98ff98';
            zone.style.backgroundColor = '#222';
        });
        
        zone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            zone.style.borderColor = '';
            zone.style.backgroundColor = '';
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            zone.style.borderColor = '';
            zone.style.backgroundColor = '';
            
            const dt = new DataTransfer();
            Array.from(e.dataTransfer.files).forEach(file => dt.items.add(file));
            input.files = dt.files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }
};

function removeFileFromInput(inputId, indexToRemove) {
    const input = document.getElementById(inputId);
    const dt = new DataTransfer();
    const files = input.files;
    
    for (let i = 0; i < files.length; i++) {
        if (i !== indexToRemove) {
            dt.items.add(files[i]);
        }
    }
    
    input.files = dt.files;
}

function updateFileCount(inputId, textId, previewId) {
    const input = document.getElementById(inputId);
    const textEl = document.getElementById(textId);
    const previewEl = document.getElementById(previewId);
    
    if (input.files.length === 0) {
        textEl.textContent = '[NONE SELECTED]';
        textEl.classList.replace('text-white', 'text-pixelMintDark');
        previewEl.innerHTML = '';
    } else if (input.files.length === 1) {
        textEl.textContent = `[${input.files[0].name.toUpperCase()}]`;
    } else {
        textEl.textContent = `[${input.files.length} FILES LOADED]`;
    }
}

// Setup all file inputs
setupFileInput('imgSourceInput', null, 'imgSourcePreview');
setupFileInput('imgTargetInput', null, 'imgTargetPreview');
setupFileInput('vidSourceInput', null, 'vidSourcePreview');
setupFileInput('vidTargetInput', null, 'vidTargetPreview');

// Make switchTab and switchHistoryTab global
window.switchTab = switchTab;
window.switchHistoryTab = switchHistoryTab;

// Upload Modal
let currentUploadInput = null;
let selectedSavedFaces = [];

window.openUploadModal = async function(inputId) {
    currentUploadInput = inputId;
    selectedSavedFaces = [];
    const modal = document.getElementById('uploadModal');
    const savedFacesGrid = document.getElementById('uploadModalSavedFaces');
    const multipleCheckbox = document.getElementById('uploadModalMultiple');
    
    // Check if input allows multiple
    const input = document.getElementById(inputId);
    const allowsMultiple = input.hasAttribute('multiple');
    multipleCheckbox.checked = false;
    multipleCheckbox.disabled = !allowsMultiple;
    
    modal.classList.remove('hidden');
    
    // Setup paste button
    document.getElementById('uploadModalPasteBtn').onclick = async () => {
        try {
            const items = await navigator.clipboard.read();
            const input = document.getElementById(currentUploadInput);
            const dt = new DataTransfer();
            
            for (const item of items) {
                for (const type of item.types) {
                    if (type.startsWith('image/')) {
                        const blob = await item.getType(type);
                        const file = new File([blob], `pasted_${Date.now()}.png`, { type });
                        dt.items.add(file);
                    }
                }
            }
            
            if (dt.files.length > 0) {
                input.files = dt.files;
                input.dispatchEvent(new Event('change', { bubbles: true }));
                closeUploadModal();
            } else {
                showErrorModal('No image in clipboard');
            }
        } catch (error) {
            showErrorModal('Paste failed. Try copying an image first.');
        }
    };
    
    // Setup upload from PC button
    document.getElementById('uploadModalFileBtn').onclick = () => {
        document.getElementById(currentUploadInput).click();
        closeUploadModal();
    };
    
    // Load saved faces
    savedFacesGrid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center text-sm">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/saved-faces`);
        const data = await response.json();
        
        savedFacesGrid.innerHTML = '';
        
        if (data.faces.length === 0) {
            savedFacesGrid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center text-sm">No saved faces</span>';
            return;
        }
        
        for (const faceUrl of data.faces) {
            const wrapper = document.createElement('div');
            wrapper.className = 'cursor-pointer hover:opacity-80 transition-opacity relative';
            wrapper.dataset.faceUrl = faceUrl;
            
            const img = document.createElement('img');
            img.src = faceUrl;
            img.className = 'w-full h-20 object-cover border-2 border-pixelMint';
            
            const checkmark = document.createElement('div');
            checkmark.className = 'hidden absolute inset-0 bg-pixelMint/50 flex items-center justify-center text-4xl text-white';
            checkmark.textContent = '✓';
            
            wrapper.appendChild(img);
            wrapper.appendChild(checkmark);
            
            wrapper.onclick = async () => {
                const isMultiple = multipleCheckbox.checked;
                
                if (isMultiple) {
                    // Toggle selection
                    const index = selectedSavedFaces.indexOf(faceUrl);
                    if (index > -1) {
                        selectedSavedFaces.splice(index, 1);
                        checkmark.classList.add('hidden');
                        img.style.opacity = '1';
                    } else {
                        selectedSavedFaces.push(faceUrl);
                        checkmark.classList.remove('hidden');
                        img.style.opacity = '0.5';
                    }
                } else {
                    // Single selection - load immediately
                    try {
                        const response = await fetch(faceUrl);
                        const blob = await response.blob();
                        const filename = faceUrl.split('/').pop();
                        const file = new File([blob], filename, { type: blob.type });
                        
                        const input = document.getElementById(currentUploadInput);
                        const dt = new DataTransfer();
                        dt.items.add(file);
                        input.files = dt.files;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        closeUploadModal();
                    } catch (error) {
                        showErrorModal('Error loading saved face');
                    }
                }
            };
            
            savedFacesGrid.appendChild(wrapper);
        }
        
        // Add confirm button for multiple selection
        if (allowsMultiple) {
            const confirmBtn = document.createElement('button');
            confirmBtn.className = 'pixel-btn font-heading text-sm py-2 px-4 col-span-full mt-2';
            confirmBtn.textContent = 'CONFIRM SELECTION';
            confirmBtn.onclick = async () => {
                if (selectedSavedFaces.length === 0) {
                    showErrorModal('No faces selected');
                    return;
                }
                
                try {
                    const input = document.getElementById(currentUploadInput);
                    const dt = new DataTransfer();
                    
                    for (const faceUrl of selectedSavedFaces) {
                        const response = await fetch(faceUrl);
                        const blob = await response.blob();
                        const filename = faceUrl.split('/').pop();
                        const file = new File([blob], filename, { type: blob.type });
                        dt.items.add(file);
                    }
                    
                    input.files = dt.files;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    closeUploadModal();
                } catch (error) {
                    showErrorModal('Error loading saved faces');
                }
            };
            savedFacesGrid.appendChild(confirmBtn);
        }
    } catch (error) {
        savedFacesGrid.innerHTML = '<span class="text-red-500 col-span-full text-center text-sm">Error loading faces</span>';
    }
};

window.closeUploadModal = function() {
    document.getElementById('uploadModal').classList.add('hidden');
    currentUploadInput = null;
    selectedSavedFaces = [];
};

// Paste from clipboard
window.pasteFromClipboard = async function(inputId) {
    try {
        const items = await navigator.clipboard.read();
        const input = document.getElementById(inputId);
        const dt = new DataTransfer();
        
        for (const item of items) {
            for (const type of item.types) {
                if (type.startsWith('image/')) {
                    const blob = await item.getType(type);
                    const file = new File([blob], `pasted_${Date.now()}.png`, { type });
                    dt.items.add(file);
                }
            }
        }
        
        if (dt.files.length > 0) {
            input.files = dt.files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
            alert('No image in clipboard');
        }
    } catch (error) {
        alert('Paste failed. Try Ctrl+V or copy an image first.');
    }
};

// Saved faces picker
let currentPickerTarget = null;

window.openSavedFacesPicker = async function(inputId) {
    currentPickerTarget = inputId;
    const modal = document.getElementById('facePickerModal');
    const grid = document.getElementById('facePickerGrid');
    
    modal.classList.remove('hidden');
    grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/saved-faces`);
        const data = await response.json();
        
        grid.innerHTML = '';
        
        if (data.faces.length === 0) {
            grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No saved faces. Add some in SAVED_FACES tab!</span>';
            return;
        }
        
        for (const faceUrl of data.faces) {
            const wrapper = document.createElement('div');
            wrapper.className = 'cursor-pointer hover:opacity-80 transition-opacity';
            
            const img = document.createElement('img');
            img.src = faceUrl;
            img.className = 'w-full h-24 object-cover border-2 border-pixelMint';
            img.onclick = () => selectSavedFace(faceUrl);
            
            wrapper.appendChild(img);
            grid.appendChild(wrapper);
        }
    } catch (error) {
        grid.innerHTML = '<span class="text-red-500 col-span-full text-center">Error loading faces</span>';
    }
};

window.closeFacePicker = function() {
    document.getElementById('facePickerModal').classList.add('hidden');
    currentPickerTarget = null;
};

async function selectSavedFace(faceUrl) {
    if (!currentPickerTarget) return;
    
    try {
        const response = await fetch(faceUrl);
        const blob = await response.blob();
        const filename = faceUrl.split('/').pop();
        const file = new File([blob], filename, { type: blob.type });
        
        const input = document.getElementById(currentPickerTarget);
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        closeFacePicker();
    } catch (error) {
        alert('Error loading saved face');
    }
}

// Image swap form
document.getElementById('imageForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('imgSubmitBtn');
    const btnText = document.getElementById('imgBtnText');
    const outputPanel = document.getElementById('imageOutputPanel');
    const gallery = document.getElementById('imageOutputGallery');
    const progressBar = document.getElementById('progressBar');

    const formData = new FormData();
    const sourceFiles = document.getElementById('imgSourceInput').files;
    const targetFiles = document.getElementById('imgTargetInput').files;
    const enhanceCheckbox = document.getElementById('enhanceCheckbox');
    const enhanceType = enhanceCheckbox.checked ? document.querySelector('input[name="enhance_type_image"]:checked').value : 'none';

    // Store target images for comparison
    const targetImages = {};
    for (let i = 0; i < targetFiles.length; i++) {
        const reader = new FileReader();
        reader.onload = (e) => targetImages[i] = e.target.result;
        reader.readAsDataURL(targetFiles[i]);
    }

    for (let i = 0; i < sourceFiles.length; i++) formData.append('source', sourceFiles[i]);
    for (let i = 0; i < targetFiles.length; i++) formData.append('target', targetFiles[i]);
    formData.append('enhance_type', enhanceType);

    submitBtn.disabled = true;
    btnText.innerHTML = '<span class="blink">> PROCESSING...</span>';
    outputPanel.classList.add('hidden');
    gallery.innerHTML = '';
    progressBar.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/swap`, { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'SYS_ERROR');

        activeGenerations.add(data.session_id);
        addTaskLog('IMAGE_SWAP', 'Started processing...');

        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        const progressDetail = document.getElementById('progressDetail');
        
        progressBar.classList.remove('hidden');
        const enhanceLabel = enhanceType === 'full' ? ' + FULL ENHANCE' : enhanceType === 'faces' ? ' + FACE ENHANCE' : '';
        btnText.innerHTML = `<span class="blink">> PROCESSING${enhanceLabel} (0/${data.total})...</span>`;

        const timer = createProgressTimer('image', enhanceType);
        const timerElement = document.getElementById('progressTimer');
        timerElement.textContent = '--:--';
        const eventSource = new EventSource(`/swap-stream/${data.session_id}`);
        let completedCount = 0;

        eventSource.onmessage = (event) => {
            const result = JSON.parse(event.data);
            
            if (result.done) {
                eventSource.close();
                submitBtn.disabled = false;
                btnText.innerHTML = '> SWAP';
                progressBar.classList.add('hidden');
                addTaskLog('IMAGE_SWAP', 'Completed successfully');
                
                setTimeout(() => {
                    outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
                
                showNotification('COMPLETE', 'Image swap finished!', 'success');
                return;
            }
            
            if (result.status === 'swapping') {
                const percent = Math.round(((result.current - 0.5) / data.total) * 100);
                animateProgress(progressFill, percent);
                progressPercent.textContent = percent + '%';
                progressText.textContent = `SWAPPING ${result.current}/${data.total}`;
                progressDetail.textContent = enhanceType === 'full' ? 'Swapping + Full Enhance...' : enhanceType === 'faces' ? 'Swapping + Face Enhance...' : 'Swapping face...';
                const timerEl = document.getElementById('progressTimer');
                if (timerEl) timer.update(result.current - 1, data.total, timerEl);
            }
            
            if (result.image) {
                completedCount++;
                const percent = Math.round((completedCount / data.total) * 100);
                
                animateProgress(progressFill, percent);
                progressPercent.textContent = percent + '%';
                progressText.textContent = `COMPLETED ${completedCount}/${data.total}`;
                progressDetail.textContent = enhanceType === 'full' ? 'Swapped + Full Enhanced!' : enhanceType === 'faces' ? 'Swapped + Face Enhanced!' : 'Swapped!';
                btnText.innerHTML = `<span class="blink">> PROCESSING${enhanceLabel} (${completedCount}/${data.total})...</span>`;
                const timerEl = document.getElementById('progressTimer');
                if (timerEl) timer.update(completedCount, data.total, timerEl);
                
                outputPanel.classList.remove('hidden');
                
                const wrapper = document.createElement('div');
                wrapper.className = 'mb-8';
                
                // Get target index for this result
                const targetIdx = Math.floor((completedCount - 1) / sourceFiles.length);
                
                // Create comparison slider
                const comparisonDiv = document.createElement('div');
                comparisonDiv.className = 'mb-4';
                
                // Wait for target image to load
                const checkTarget = setInterval(() => {
                    if (targetImages[targetIdx]) {
                        clearInterval(checkTarget);
                        createComparisonSlider(targetImages[targetIdx], result.image, comparisonDiv);
                    }
                }, 100);
                
                const downloadBtn = document.createElement('a');
                downloadBtn.href = result.image;
                downloadBtn.download = '';
                downloadBtn.className = 'pixel-btn font-heading text-sm py-3 px-6 block text-center';
                downloadBtn.textContent = '> DOWNLOAD';
                
                wrapper.appendChild(comparisonDiv);
                wrapper.appendChild(downloadBtn);
                gallery.appendChild(wrapper);
                
                outputPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            submitBtn.disabled = false;
            btnText.innerHTML = '> SWAP';
            progressBar.classList.add('hidden');
        };

    } catch (error) {
        showErrorModal(error.message);
        submitBtn.disabled = false;
        btnText.innerHTML = '> SWAP';
        progressBar.classList.add('hidden');
    }
});

// Video swap form
document.getElementById('videoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('vidSubmitBtn');
    const btnText = document.getElementById('vidBtnText');
    const outputPanel = document.getElementById('videoOutputPanel');
    const gallery = document.getElementById('videoOutputGallery');
    const progressBar = document.getElementById('progressBar');

    const formData = new FormData();
    const sourceFiles = document.getElementById('vidSourceInput').files;
    const videoFiles = document.getElementById('vidTargetInput').files;
    const speedMode = document.querySelector('input[name="speed_mode"]:checked').value;
    const enhanceCheckbox = document.getElementById('enhanceVideoCheckbox');
    const enhanceType = enhanceCheckbox.checked ? document.querySelector('input[name="enhance_type_video"]:checked').value : 'none';

    for (let i = 0; i < sourceFiles.length; i++) formData.append('source', sourceFiles[i]);
    for (let i = 0; i < videoFiles.length; i++) formData.append('video', videoFiles[i]);
    formData.append('speed_mode', speedMode);
    formData.append('enhance_type', enhanceType);

    submitBtn.disabled = true;
    btnText.innerHTML = '<span class="blink">> UPLOADING...</span>';
    outputPanel.classList.add('hidden');
    gallery.innerHTML = '';
    progressBar.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/swap-video`, { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'SYS_ERROR');

        activeGenerations.add(data.session_id);
        addTaskLog('VIDEO_SWAP', 'Started processing...');

        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        const progressDetail = document.getElementById('progressDetail');
        
        progressBar.classList.remove('hidden');
        const speedLabel = speedMode === 'default' ? 'DEFAULT MODE' : speedMode === 'speed' ? 'SPEED MODE' : 'EXTRA SPEED MODE';
        progressText.textContent = `GENERATING (${speedLabel})`;
        progressDetail.textContent = 'Preparing video processing...';
        btnText.innerHTML = `<span class="blink">> PROCESSING (${speedLabel})...</span>`;

        const timer = createProgressTimer('video_frame', enhanceType);
        const timerElement = document.getElementById('progressTimer');
        timerElement.textContent = '--:--';
        const eventSource = new EventSource(`/swap-video-stream/${data.session_id}/${data.speed_mode}`);
        let totalFrames = 0;

        eventSource.onmessage = (event) => {
            const result = JSON.parse(event.data);
            
            if (result.done) {
                eventSource.close();
                submitBtn.disabled = false;
                btnText.innerHTML = '> SWAP VIDEO';
                progressBar.classList.add('hidden');
                addTaskLog('VIDEO_SWAP', 'Completed successfully');
                
                setTimeout(() => {
                    outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
                
                showNotification('COMPLETE', 'Video swap finished!', 'success');
                return;
            }
            
            if (result.status === 'extracting') {
                progressText.textContent = 'EXTRACTING FRAMES...';
                progressDetail.textContent = 'Reading video file...';
                progressFill.style.width = '10%';
                progressPercent.textContent = '10%';
            }
            
            if (result.status === 'processing') {
                totalFrames = result.total_frames;
                progressText.textContent = `PROCESSING ${totalFrames} FRAMES`;
                progressDetail.textContent = 'Swapping faces in each frame...';
                progressFill.style.width = '20%';
                progressPercent.textContent = '20%';
            }
            
            if (result.status === 'frame') {
                const percent = Math.round((result.current / result.total) * 70) + 20;
                animateProgress(progressFill, percent);
                progressPercent.textContent = percent + '%';
                progressText.textContent = `FRAME ${result.current}/${result.total}`;
                progressDetail.textContent = enhanceType === 'full' ? 'Swapping + Full Enhance...' : enhanceType === 'faces' ? 'Swapping + Face Enhance...' : 'Swapping faces...';
                const timerEl = document.getElementById('progressTimer');
                if (timerEl) timer.update(result.current, result.total, timerEl);
            }
            
            if (result.status === 'encoding') {
                progressText.textContent = 'ENCODING VIDEO...';
                progressDetail.textContent = 'Creating final video file...';
                progressFill.style.width = '95%';
                progressPercent.textContent = '95%';
            }
            
            if (result.video) {
                progressFill.style.width = '100%';
                progressPercent.textContent = '100%';
                
                outputPanel.classList.remove('hidden');
                
                const videoWrapper = document.createElement('div');
                videoWrapper.className = 'result-img-wrapper mb-6';

                const video = document.createElement('video');
                video.src = result.video + '?t=' + Date.now();
                video.controls = true;
                video.preload = 'metadata';
                video.className = 'w-full h-auto block mb-4';
                
                const downloadBtn = document.createElement('a');
                downloadBtn.href = result.video;
                downloadBtn.download = '';
                downloadBtn.className = 'pixel-btn font-heading text-sm py-3 px-6 block text-center';
                downloadBtn.textContent = '> DOWNLOAD VIDEO';

                videoWrapper.appendChild(video);
                videoWrapper.appendChild(downloadBtn);
                gallery.appendChild(videoWrapper);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            submitBtn.disabled = false;
            btnText.innerHTML = '> SWAP VIDEO';
            progressBar.classList.add('hidden');
        };

    } catch (error) {
        showErrorModal(error.message);
        submitBtn.disabled = false;
        btnText.innerHTML = '> SWAP VIDEO';
        progressBar.classList.add('hidden');
    }
});

// Saved Faces
async function loadSavedFaces() {
    const grid = document.getElementById('savedFacesGrid');
    grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/saved-faces`);
        const data = await response.json();
        
        grid.innerHTML = '';
        
        if (data.faces.length === 0) {
            grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No saved faces</span>';
            return;
        }
        
        data.faces.forEach(faceUrl => {
            const wrapper = document.createElement('div');
            wrapper.className = 'relative group cursor-pointer';
            
            const img = document.createElement('img');
            img.src = faceUrl;
            img.className = 'w-full h-32 object-cover border-2 border-pixelMint';
            img.onclick = () => useSavedFace(faceUrl);
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'absolute top-1 right-1 bg-red-600 text-white w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity font-bold text-xs';
            deleteBtn.innerHTML = 'X';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSavedFace(faceUrl);
            };
            
            wrapper.appendChild(img);
            wrapper.appendChild(deleteBtn);
            grid.appendChild(wrapper);
        });
    } catch (error) {
        grid.innerHTML = '<span class="text-red-500 col-span-full text-center">Error loading faces</span>';
    }
}

document.getElementById('addFaceInput').addEventListener('change', async function(e) {
    const files = this.files;
    if (files.length === 0) return;
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('face', file);
        
        try {
            await fetch(`${API_BASE_URL}/save-face`, { method: 'POST', body: formData });
        } catch (error) {
            alert('Error saving face: ' + error.message);
        }
    }
    
    loadSavedFaces();
    this.value = '';
});

async function deleteSavedFace(faceUrl) {
    if (!confirm('Delete this face?')) return;
    
    try {
        await fetch(`${API_BASE_URL}/delete-face`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: faceUrl })
        });
        loadSavedFaces();
    } catch (error) {
        alert('Error deleting face');
    }
}

function useSavedFace(faceUrl) {
    alert('Click on source upload area, then select this face from your saved faces!');
}

// History
async function loadHistory() {
    const imgDiv = document.getElementById('historyImages');
    const vidDiv = document.getElementById('historyVideos');
    
    imgDiv.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">Loading...</span>';
    vidDiv.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        const data = await response.json();
        
        imgDiv.innerHTML = '';
        vidDiv.innerHTML = '';
        
        if (data.images.length === 0) {
            imgDiv.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No images</span>';
        } else {
            data.images.forEach(imgUrl => {
                const wrapper = document.createElement('div');
                wrapper.className = 'result-img-wrapper relative group';
                
                const img = document.createElement('img');
                img.src = imgUrl;
                img.className = 'w-full h-auto block';
                
                const downloadOverlay = document.createElement('div');
                downloadOverlay.className = 'absolute inset-0 bg-pixelDark/80 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity';
                downloadOverlay.innerHTML = `
                    <a href="${imgUrl}" download class="pixel-btn font-heading text-xs py-2 px-4 no-underline text-center">
                        > DOWNLOAD
                    </a>`;
                
                wrapper.appendChild(img);
                wrapper.appendChild(downloadOverlay);
                imgDiv.appendChild(wrapper);
            });
        }
        
        if (data.videos.length === 0) {
            vidDiv.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No videos</span>';
        } else {
            data.videos.forEach(videoUrl => {
                const wrapper = document.createElement('div');
                wrapper.className = 'result-img-wrapper relative';
                
                const video = document.createElement('video');
                video.src = videoUrl;
                video.controls = true;
                video.className = 'w-full h-auto block';
                
                const downloadBtn = document.createElement('a');
                downloadBtn.href = videoUrl;
                downloadBtn.download = '';
                downloadBtn.className = 'pixel-btn font-heading text-xs py-2 px-4 no-underline text-center block mt-2';
                downloadBtn.textContent = '> DOWNLOAD';
                
                wrapper.appendChild(video);
                wrapper.appendChild(downloadBtn);
                vidDiv.appendChild(wrapper);
            });
        }
    } catch (error) {
        imgDiv.innerHTML = '<span class="text-red-500 col-span-full text-center">Error loading history</span>';
        vidDiv.innerHTML = '<span class="text-red-500 col-span-full text-center">Error loading history</span>';
    }
}

// Multi-Face Swap
let multiSessionId = null;
let detectedFaces = [];
const faceAssignments = {};

document.getElementById('multiTargetInput').addEventListener('change', async function(e) {
    const file = this.files[0];
    if (!file) return;
    
    // Clear previous session data
    multiSessionId = null;
    detectedFaces = [];
    Object.keys(faceAssignments).forEach(key => delete faceAssignments[key]);
    
    const formData = new FormData();
    formData.append('image', file);
    
    const detectionDiv = document.getElementById('multiFaceDetection');
    const grid = document.getElementById('detectedFacesGrid');
    const resultDiv = document.getElementById('multiResult');
    const progressBar = document.getElementById('multiProgressBar');
    
    grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center blink">Detecting faces...</span>';
    detectionDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    progressBar.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/detect-faces`, { method: 'POST', body: formData });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || 'Detection failed');
        
        multiSessionId = data.session_id;
        detectedFaces = data.faces;
        
        grid.innerHTML = '';
        
        if (detectedFaces.length === 0) {
            grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No faces detected</span>';
            return;
        }
        
        detectedFaces.forEach(face => {
            const wrapper = document.createElement('div');
            wrapper.className = 'border-2 border-pixelMint p-2 bg-pixelDark';
            
            const label = document.createElement('div');
            label.className = 'font-heading text-xs text-pixelMint mb-2 text-center';
            label.textContent = `FACE ${face.index}`;
            
            const img = document.createElement('img');
            img.src = face.url;
            img.className = 'w-full h-24 object-cover border border-pixelMintDark mb-2';
            
            // Source face preview (will be shown when assigned)
            const sourcePreview = document.createElement('div');
            sourcePreview.id = `source_preview_${face.index}`;
            sourcePreview.className = 'hidden mb-2';
            sourcePreview.innerHTML = '<div class="font-heading text-xs text-white mb-1 text-center">SOURCE</div>';
            
            const sourceImg = document.createElement('img');
            sourceImg.id = `source_img_${face.index}`;
            sourceImg.className = 'w-full h-24 object-cover border border-pixelMint';
            sourcePreview.appendChild(sourceImg);
            
            // Paste and Saved Faces buttons
            const btnContainer = document.createElement('div');
            btnContainer.className = 'flex gap-1 mb-2';
            
            const pasteBtn = document.createElement('button');
            pasteBtn.type = 'button';
            pasteBtn.className = 'pixel-btn font-heading text-xs py-1 px-2 flex-1';
            pasteBtn.style.boxShadow = 'inset -2px -2px 0px rgba(0, 0, 0, 0.4), 2px 2px 0px #000';
            pasteBtn.innerHTML = 'PASTE';
            pasteBtn.onclick = () => pasteForMultiFace(face.index);
            
            const savedBtn = document.createElement('button');
            savedBtn.type = 'button';
            savedBtn.className = 'pixel-btn font-heading text-xs py-1 px-2 flex-1';
            savedBtn.style.boxShadow = 'inset -2px -2px 0px rgba(0, 0, 0, 0.4), 2px 2px 0px #000';
            savedBtn.innerHTML = 'SAVED';
            savedBtn.onclick = () => openSavedFacesForMulti(face.index);
            
            btnContainer.appendChild(pasteBtn);
            btnContainer.appendChild(savedBtn);
            
            const uploadLabel = document.createElement('label');
            uploadLabel.className = 'pixel-btn font-heading text-xs py-1 px-2 cursor-pointer block text-center';
            uploadLabel.style.boxShadow = 'inset -2px -2px 0px rgba(0, 0, 0, 0.4), 2px 2px 0px #000';
            uploadLabel.innerHTML = 'ASSIGN';
            uploadLabel.id = `label_${face.index}`;
            
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.style.display = 'none';
            fileInput.id = `input_${face.index}`;
            fileInput.onchange = (e) => {
                if (e.target.files[0]) {
                    faceAssignments[face.index] = e.target.files[0];
                    uploadLabel.innerHTML = 'ASSIGNED';
                    uploadLabel.style.backgroundColor = '#3eb489';
                    
                    // Show source preview
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        document.getElementById(`source_img_${face.index}`).src = ev.target.result;
                        document.getElementById(`source_preview_${face.index}`).classList.remove('hidden');
                    };
                    reader.readAsDataURL(e.target.files[0]);
                    
                    checkAllAssigned();
                }
            };
            
            uploadLabel.appendChild(fileInput);
            wrapper.appendChild(label);
            wrapper.appendChild(img);
            wrapper.appendChild(sourcePreview);
            wrapper.appendChild(btnContainer);
            wrapper.appendChild(uploadLabel);
            grid.appendChild(wrapper);
        });
        
    } catch (error) {
        grid.innerHTML = `<span class="text-red-500 col-span-full text-center">${error.message}</span>`;
        showErrorModal(error.message);
    }
});

async function pasteForMultiFace(faceIndex) {
    try {
        const items = await navigator.clipboard.read();
        
        for (const item of items) {
            for (const type of item.types) {
                if (type.startsWith('image/')) {
                    const blob = await item.getType(type);
                    const file = new File([blob], `pasted_${Date.now()}.png`, { type });
                    
                    faceAssignments[faceIndex] = file;
                    const label = document.getElementById(`label_${faceIndex}`);
                    label.innerHTML = 'ASSIGNED';
                    label.style.backgroundColor = '#3eb489';
                    
                    // Show source preview
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        document.getElementById(`source_img_${faceIndex}`).src = ev.target.result;
                        document.getElementById(`source_preview_${faceIndex}`).classList.remove('hidden');
                    };
                    reader.readAsDataURL(file);
                    
                    checkAllAssigned();
                    return;
                }
            }
        }
        alert('No image in clipboard');
    } catch (error) {
        alert('Paste failed. Try copying an image first.');
    }
}

async function openSavedFacesForMulti(faceIndex) {
    const modal = document.getElementById('facePickerModal');
    const grid = document.getElementById('facePickerGrid');
    
    modal.classList.remove('hidden');
    grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/saved-faces`);
        const data = await response.json();
        
        grid.innerHTML = '';
        
        if (data.faces.length === 0) {
            grid.innerHTML = '<span class="text-pixelMintDark col-span-full text-center">No saved faces</span>';
            return;
        }
        
        for (const faceUrl of data.faces) {
            const wrapper = document.createElement('div');
            wrapper.className = 'cursor-pointer hover:opacity-80 transition-opacity';
            
            const img = document.createElement('img');
            img.src = faceUrl;
            img.className = 'w-full h-24 object-cover border-2 border-pixelMint';
            img.onclick = async () => {
                try {
                    const response = await fetch(faceUrl);
                    const blob = await response.blob();
                    const filename = faceUrl.split('/').pop();
                    const file = new File([blob], filename, { type: blob.type });
                    
                    faceAssignments[faceIndex] = file;
                    const label = document.getElementById(`label_${faceIndex}`);
                    label.innerHTML = 'ASSIGNED';
                    label.style.backgroundColor = '#3eb489';
                    
                    // Show source preview
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        document.getElementById(`source_img_${faceIndex}`).src = ev.target.result;
                        document.getElementById(`source_preview_${faceIndex}`).classList.remove('hidden');
                    };
                    reader.readAsDataURL(blob);
                    
                    checkAllAssigned();
                    closeFacePicker();
                } catch (error) {
                    alert('Error loading saved face');
                }
            };
            
            wrapper.appendChild(img);
            grid.appendChild(wrapper);
        }
    } catch (error) {
        grid.innerHTML = '<span class="text-red-500 col-span-full text-center">Error loading faces</span>';
    }
}

function checkAllAssigned() {
    const btn = document.getElementById('multiSwapBtn');
    const assignedCount = Object.keys(faceAssignments).length;
    
    if (assignedCount > 0) {
        btn.disabled = false;
        btn.textContent = `> SWAP ${assignedCount} FACE${assignedCount > 1 ? 'S' : ''}`;
    } else {
        btn.disabled = true;
        btn.textContent = '> SWAP ALL FACES';
    }
}

document.getElementById('multiSwapBtn').addEventListener('click', async () => {
    if (Object.keys(faceAssignments).length === 0) {
        alert('Assign at least one face!');
        return;
    }
    
    const btn = document.getElementById('multiSwapBtn');
    const resultDiv = document.getElementById('multiResult');
    const resultImg = document.getElementById('multiResultImg');
    const progressBar = document.getElementById('multiProgressBar');
    const progressFill = document.getElementById('multiProgressFill');
    const progressPercent = document.getElementById('multiProgressPercent');
    const progressText = document.getElementById('multiProgressText');
    const progressDetail = document.getElementById('multiProgressDetail');
    
    btn.disabled = true;
    btn.innerHTML = '<span class="blink">> UPLOADING...</span>';
    resultDiv.classList.add('hidden');
    progressBar.classList.add('hidden');
    
    try {
        const formData = new FormData();
        const mappings = [];
        const enhanceCheckbox = document.getElementById('enhanceMultiCheckbox');
        const enhanceType = enhanceCheckbox.checked ? document.querySelector('input[name="enhance_type_multi"]:checked').value : 'none';
        
        for (const [faceIndex, file] of Object.entries(faceAssignments)) {
            formData.append(`source_${faceIndex}`, file);
            mappings.push({ face_index: parseInt(faceIndex) });
        }
        
        formData.append('session_id', multiSessionId);
        formData.append('mappings', JSON.stringify(mappings));
        formData.append('enhance_type', enhanceType);
        
        const response = await fetch(`${API_BASE_URL}/swap-multi`, { method: 'POST', body: formData });
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error || 'Upload failed');
        
        // Track this generation
        activeGenerations.add(data.session_id);
        
        // Start streaming
        progressBar.classList.remove('hidden');
        btn.innerHTML = '<span class="blink">> SWAPPING...</span>';
        
        const timer = createProgressTimer('multi', enhanceType);
        const timerElement = document.getElementById('multiProgressTimer');
        timerElement.textContent = '--:--';
        const eventSource = new EventSource(`/swap-multi-stream/${data.session_id}`);
        const totalFaces = mappings.length;
        
        eventSource.onmessage = (event) => {
            const result = JSON.parse(event.data);
            
            if (result.error) {
                progressDetail.textContent = 'Error: ' + result.error;
                progressDetail.style.color = '#ff0000';
                return;
            }
            
            if (result.status === 'swapping') {
                const percent = Math.round(((result.current - 1) / totalFaces) * 100);
                progressFill.style.width = percent + '%';
                progressPercent.textContent = percent + '%';
                progressText.textContent = `SWAPPING FACE ${result.current}/${totalFaces}`;
                progressDetail.textContent = enhanceType === 'full' ? 'Swapping + Full Enhance...' : enhanceType === 'faces' ? 'Swapping + Face Enhance...' : 'Swapping face...';
                progressDetail.style.color = '';
                const timerEl = document.getElementById('multiProgressTimer');
                if (timerEl) timer.update(result.current - 1, totalFaces, timerEl);
            }
            
            if (result.status === 'completed') {
                const percent = Math.round((result.current / totalFaces) * 100);
                progressFill.style.width = percent + '%';
                progressPercent.textContent = percent + '%';
                progressText.textContent = `COMPLETED ${result.current}/${totalFaces}`;
                progressDetail.textContent = enhanceType === 'full' ? 'Swapped + Full Enhanced!' : enhanceType === 'faces' ? 'Swapped + Face Enhanced!' : 'Swapped!';
                const timerEl = document.getElementById('multiProgressTimer');
                if (timerEl) timer.update(result.current, totalFaces, timerEl);
            }
            
            if (result.done) {
                eventSource.close();
                progressFill.style.width = '100%';
                progressPercent.textContent = '100%';
                progressText.textContent = 'ALL FACES SWAPPED!';
                progressDetail.textContent = 'Processing complete';
                
                resultImg.src = result.result + '?t=' + Date.now();
                resultDiv.classList.remove('hidden');
                resultDiv.scrollIntoView({ behavior: 'smooth' });
                
                btn.disabled = false;
                checkAllAssigned();
                showNotification('COMPLETE', 'Multi-face swap finished!', 'success');
            }
        };
        
        eventSource.onerror = () => {
            eventSource.close();
            btn.disabled = false;
            checkAllAssigned();
        };
        
    } catch (error) {
        showErrorModal(error.message);
        btn.disabled = false;
        checkAllAssigned();
    }
});

// Notification System
function showNotification(title, message, type = 'success') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
    `;
    container.appendChild(notification);
    
    notification.onclick = () => {
        notification.classList.add('removing');
        setTimeout(() => notification.remove(), 300);
    };
    
    setTimeout(() => {
        notification.classList.add('removing');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Task Management
let taskCheckInterval = null;
let activeGenerations = new Set(); // Track only active generations

function startTaskMonitoring() {
    if (taskCheckInterval) return;
    taskCheckInterval = setInterval(checkTasks, 2000);
}

async function checkTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        const data = await response.json();
        
        data.tasks.forEach(task => {
            // Only notify if task was in activeGenerations and just completed
            if (task.status === 'completed' && activeGenerations.has(task.session_id)) {
                activeGenerations.delete(task.session_id);
                const typeLabel = task.type === 'image' ? 'IMAGE SWAP' : task.type === 'video' ? 'VIDEO SWAP' : 'MULTI-FACE SWAP';
                showNotification('COMPLETE', `${typeLabel} finished!`, 'success');
            }
        });
    } catch (error) {
        console.error('Task check failed:', error);
    }
}

async function loadTasks() {
    const grid = document.getElementById('tasksGrid');
    grid.innerHTML = '<span class="text-pixelMintDark text-center block">Loading...</span>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        const data = await response.json();
        
        grid.innerHTML = '';
        
        if (data.tasks.length === 0) {
            grid.innerHTML = '<span class="text-pixelMintDark text-center block">No active or recent tasks</span>';
            return;
        }
        
        data.tasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'border-4 border-pixelMint p-4 bg-pixelDark';
            
            const typeLabel = task.type === 'image' ? 'IMAGE SWAP' : task.type === 'video' ? 'VIDEO SWAP' : 'MULTI-FACE SWAP';
            const statusColor = task.status === 'completed' ? 'text-pixelMint' : task.status === 'processing' ? 'text-yellow-400' : 'text-pixelMintDark';
            const statusLabel = task.status === 'completed' ? 'COMPLETED' : task.status === 'processing' ? 'PROCESSING' : 'DETECTING';
            
            let progressHTML = '';
            if (task.total > 0) {
                const percent = Math.round((task.current / task.total) * 100);
                progressHTML = `
                    <div class="mt-2">
                        <div class="w-full bg-pixelGray border-2 border-pixelMintDark h-6 relative">
                            <div class="h-full bg-pixelMint" style="width: ${percent}%"></div>
                            <div class="absolute inset-0 flex items-center justify-center font-heading text-xs text-pixelDark">${task.current}/${task.total}</div>
                        </div>
                    </div>
                `;
            }
            
            let actionHTML = '';
            if (task.status === 'completed' && task.result) {
                actionHTML = `
                    <button onclick="viewTaskResult('${task.result}', '${task.type}')" class="pixel-btn font-heading text-xs py-2 px-4 mt-3" style="box-shadow: inset -2px -2px 0px rgba(0, 0, 0, 0.4), 3px 3px 0px #000;">
                        > VIEW RESULT
                    </button>
                `;
            } else if (task.status === 'processing') {
                const hasCheckpoint = task.checkpoint && (task.checkpoint.completed || task.checkpoint.last_frame !== undefined || task.checkpoint.completed_faces);
                if (hasCheckpoint) {
                    actionHTML = `
                        <button onclick="resumeTask('${task.session_id}', '${task.type}')" class="pixel-btn font-heading text-xs py-2 px-4 mt-3" style="box-shadow: inset -2px -2px 0px rgba(0, 0, 0, 0.4), 3px 3px 0px #000;">
                            RESUME TASK
                        </button>
                    `;
                } else {
                    actionHTML = '<div class="text-pixelMintDark text-sm mt-2">Task interrupted - no checkpoint found</div>';
                }
            }
            
            taskCard.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <div class="font-heading text-sm text-white">${typeLabel}</div>
                    <div class="font-heading text-xs ${statusColor}">${statusLabel}</div>
                </div>
                <div class="text-xs text-pixelMintDark">ID: ${task.session_id.substring(0, 8)}</div>
                ${progressHTML}
                ${actionHTML}
            `;
            
            grid.appendChild(taskCard);
        });
    } catch (error) {
        grid.innerHTML = '<span class="text-red-500 text-center block">Error loading tasks</span>';
    }
}

window.resumeTask = function(sessionId, taskType) {
    if (taskType === 'image') {
        const eventSource = new EventSource(`/swap-stream/${sessionId}`);
        showNotification('RESUMING', 'Image swap resuming...', 'success');
        
        eventSource.onmessage = (event) => {
            const result = JSON.parse(event.data);
            if (result.done) {
                eventSource.close();
                showNotification('COMPLETE', 'Image swap finished!', 'success');
                loadTasks();
            }
        };
    } else if (taskType === 'multi') {
        const eventSource = new EventSource(`/swap-multi-stream/${sessionId}`);
        showNotification('RESUMING', 'Multi-face swap resuming...', 'success');
        
        eventSource.onmessage = (event) => {
            const result = JSON.parse(event.data);
            if (result.done) {
                eventSource.close();
                showNotification('COMPLETE', 'Multi-face swap finished!', 'success');
                loadTasks();
            }
        };
    }
};

window.viewTaskResult = function(resultPath, taskType) {
    if (taskType === 'video') {
        window.open(resultPath, '_blank');
    } else {
        switchTab('history');
    }
};

// Start monitoring on page load
startTaskMonitoring();

// Error Modal
function showErrorModal(message) {
    document.getElementById('errorModalMessage').textContent = message;
    document.getElementById('errorModal').classList.remove('hidden');
}

window.closeErrorModal = function() {
    document.getElementById('errorModal').classList.add('hidden');
};


