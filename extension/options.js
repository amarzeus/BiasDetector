// BiasDetector Options Page Script

// Default settings
const DEFAULT_SETTINGS = {
    apiKey: '',
    apiEndpoint: 'http://localhost:5000',
    detectPolitical: true,
    detectEmotional: true,
    detectFactual: true,
    minConfidence: 0.7,
    theme: 'system',
    highlightColor: '#FFE4E1',
    showTooltips: true,
    enableNotifications: true,
    soundAlerts: false,
    cacheTime: 86400,
    realTimeAnalysis: false
};

// DOM Elements
const elements = {
    apiKey: document.getElementById('apiKey'),
    apiEndpoint: document.getElementById('apiEndpoint'),
    detectPolitical: document.getElementById('detectPolitical'),
    detectEmotional: document.getElementById('detectEmotional'),
    detectFactual: document.getElementById('detectFactual'),
    minConfidence: document.getElementById('minConfidence'),
    theme: document.getElementById('theme'),
    highlightColor: document.getElementById('highlightColor'),
    showTooltips: document.getElementById('showTooltips'),
    enableNotifications: document.getElementById('enableNotifications'),
    soundAlerts: document.getElementById('soundAlerts'),
    cacheTime: document.getElementById('cacheTime'),
    realTimeAnalysis: document.getElementById('realTimeAnalysis'),
    themePreview: document.getElementById('themePreview'),
    status: document.getElementById('status'),
    saveButton: document.getElementById('saveSettings'),
    exportButton: document.getElementById('exportData'),
    importButton: document.getElementById('importData'),
    resetButton: document.getElementById('resetData')
};

// Load settings from storage
async function loadSettings() {
    try {
        const settings = await chrome.storage.sync.get(DEFAULT_SETTINGS);
        Object.keys(elements).forEach(key => {
            if (elements[key] && settings[key] !== undefined) {
                if (elements[key].type === 'checkbox') {
                    elements[key].checked = settings[key];
                } else {
                    elements[key].value = settings[key];
                }
            }
        });
        updateThemePreview();
    } catch (error) {
        showStatus('Error loading settings: ' + error.message, 'error');
    }
}

// Save settings to storage
async function saveSettings() {
    try {
        const settings = {};
        Object.keys(elements).forEach(key => {
            if (elements[key] && !['status', 'themePreview'].includes(key)) {
                settings[key] = elements[key].type === 'checkbox' 
                    ? elements[key].checked 
                    : elements[key].value;
            }
        });
        await chrome.storage.sync.set(settings);
        showStatus('Settings saved successfully!', 'success');
        
        // Notify background script of settings change
        chrome.runtime.sendMessage({ type: 'settingsUpdated', settings });
    } catch (error) {
        showStatus('Error saving settings: ' + error.message, 'error');
    }
}

// Export settings
function exportSettings() {
    chrome.storage.sync.get(null, (settings) => {
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'biasdetector-settings.json';
        a.click();
        URL.revokeObjectURL(url);
    });
}

// Import settings
function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        try {
            const file = e.target.files[0];
            const text = await file.text();
            const settings = JSON.parse(text);
            await chrome.storage.sync.set(settings);
            loadSettings();
            showStatus('Settings imported successfully!', 'success');
        } catch (error) {
            showStatus('Error importing settings: ' + error.message, 'error');
        }
    };
    input.click();
}

// Reset settings
async function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
        try {
            await chrome.storage.sync.set(DEFAULT_SETTINGS);
            loadSettings();
            showStatus('Settings reset to defaults!', 'success');
        } catch (error) {
            showStatus('Error resetting settings: ' + error.message, 'error');
        }
    }
}

// Update theme preview
function updateThemePreview() {
    const theme = elements.theme.value;
    const preview = elements.themePreview;
    
    preview.style.backgroundColor = theme === 'dark' ? '#333' : 
                                  theme === 'light' ? '#fff' : 
                                  window.matchMedia('(prefers-color-scheme: dark)').matches ? '#333' : '#fff';
    
    preview.style.color = theme === 'dark' ? '#fff' : 
                         theme === 'light' ? '#333' : 
                         window.matchMedia('(prefers-color-scheme: dark)').matches ? '#fff' : '#333';
}

// Show status message
function showStatus(message, type = 'success') {
    const status = elements.status;
    status.textContent = message;
    status.className = 'status ' + type;
    status.style.display = 'block';
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', loadSettings);
elements.saveButton.addEventListener('click', saveSettings);
elements.exportButton.addEventListener('click', exportSettings);
elements.importButton.addEventListener('click', importSettings);
elements.resetButton.addEventListener('click', resetSettings);
elements.theme.addEventListener('change', updateThemePreview);

// Theme system preference change listener
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (elements.theme.value === 'system') {
        updateThemePreview();
    }
});
