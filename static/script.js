// API helper functions
async function fetchConfig() {
    const response = await fetch('/api/config');
    return await response.json();
}

async function updateConfig(sabnzbdDir) {
    const response = await fetch('/api/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sabnzbd_complete_dir: sabnzbdDir
        })
    });
    return await response.json();
}

async function fetchFolders() {
    const response = await fetch('/api/folders');
    return await response.json();
}

async function unpackFolder(path) {
    const response = await fetch('/api/unpack', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path })
    });
    return await response.json();
}

// UI functions
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('folders-list').innerHTML = '';
    document.getElementById('error-message').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    hideLoading();
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

function displayToolsStatus(tools) {
    const toolsDiv = document.getElementById('tools-status');
    const toolNames = {
        'unrar': 'UnRAR',
        '7z': '7-Zip',
        'unzip': 'Unzip',
        'tar': 'Tar'
    };
    
    let html = '<strong>Available unpacking tools:</strong><br>';
    for (const [tool, available] of Object.entries(tools)) {
        const className = available ? 'tool-available' : 'tool-unavailable';
        const status = available ? '✓' : '✗';
        html += `<span class="tool-item ${className}">${status} ${toolNames[tool]}</span>`;
    }
    
    toolsDiv.innerHTML = html;
}

function displayFolders(folders) {
    const foldersList = document.getElementById('folders-list');
    
    if (folders.length === 0) {
        foldersList.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 40px;">No folders with archives found in the SABnzbd complete directory.</p>';
        return;
    }
    
    foldersList.innerHTML = '';
    
    folders.forEach(folder => {
        const folderDiv = document.createElement('div');
        folderDiv.className = 'folder-item' + (folder.needs_unpack ? ' needs-unpack' : '');
        folderDiv.dataset.path = folder.path;
        
        const badge = folder.needs_unpack 
            ? '<span class="badge badge-warning">Needs Unpacking</span>'
            : '<span class="badge badge-success">Already Unpacked</span>';
        
        folderDiv.innerHTML = `
            <div class="folder-header">
                <div class="folder-name">
                    📁 ${escapeHtml(folder.name)}
                    ${badge}
                </div>
            </div>
            <div class="folder-path">${escapeHtml(folder.path)}</div>
            <div class="folder-actions">
                <button class="btn btn-success unpack-btn" data-path="${escapeHtml(folder.path)}">
                    🔓 Unpack Now
                </button>
            </div>
            <div class="unpack-status" style="display: none;"></div>
        `;
        
        foldersList.appendChild(folderDiv);
    });
    
    // Add event listeners to unpack buttons
    document.querySelectorAll('.unpack-btn').forEach(btn => {
        btn.addEventListener('click', handleUnpack);
    });
}

async function handleUnpack(event) {
    const btn = event.target;
    const path = btn.dataset.path;
    const folderItem = btn.closest('.folder-item');
    const statusDiv = folderItem.querySelector('.unpack-status');
    
    // Disable button and show loading
    btn.disabled = true;
    btn.textContent = '⏳ Unpacking...';
    statusDiv.style.display = 'none';
    
    try {
        const result = await unpackFolder(path);
        
        // Show result
        statusDiv.style.display = 'block';
        if (result.success) {
            statusDiv.className = 'unpack-status success-message';
            statusDiv.textContent = `✓ ${result.message}`;
            
            // Update folder badge after successful unpack
            setTimeout(() => {
                loadFolders();
            }, 2000);
        } else {
            statusDiv.className = 'unpack-status error-message';
            statusDiv.textContent = `✗ ${result.message}`;
            btn.disabled = false;
            btn.textContent = '🔓 Unpack Now';
        }
    } catch (error) {
        statusDiv.style.display = 'block';
        statusDiv.className = 'unpack-status error-message';
        statusDiv.textContent = `Error: ${error.message}`;
        btn.disabled = false;
        btn.textContent = '🔓 Unpack Now';
    }
}

async function loadConfig() {
    try {
        const config = await fetchConfig();
        document.getElementById('sabnzbd-dir').value = config.sabnzbd_complete_dir;
        displayToolsStatus(config.tools);
    } catch (error) {
        showError('Failed to load configuration: ' + error.message);
    }
}

async function loadFolders() {
    showLoading();
    hideError();
    
    try {
        const data = await fetchFolders();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        hideLoading();
        displayFolders(data.folders);
    } catch (error) {
        showError('Failed to load folders: ' + error.message);
    }
}

async function handleUpdateConfig() {
    const sabnzbdDir = document.getElementById('sabnzbd-dir').value.trim();
    
    if (!sabnzbdDir) {
        alert('Please enter a valid directory path');
        return;
    }
    
    const btn = document.getElementById('update-config-btn');
    btn.disabled = true;
    btn.textContent = 'Updating...';
    
    try {
        const result = await updateConfig(sabnzbdDir);
        
        if (result.success) {
            alert('Configuration updated successfully!');
            loadFolders();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('Failed to update configuration: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Update';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    loadFolders();
    
    // Event listeners
    document.getElementById('update-config-btn').addEventListener('click', handleUpdateConfig);
    document.getElementById('refresh-btn').addEventListener('click', loadFolders);
    
    // Allow Enter key to update config
    document.getElementById('sabnzbd-dir').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleUpdateConfig();
        }
    });
});
