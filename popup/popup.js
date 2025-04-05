document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('analyze-btn');
  const statusDiv = document.getElementById('status');
  const enhancedToggle = document.getElementById('enhanced-mode');
  const apiKeyInput = document.getElementById('api-key');
  const infoIcon = document.querySelector('.info-icon');

  // Load settings
  chrome.storage.sync.get(['settings'], (data) => {
    enhancedToggle.checked = data.settings?.enhancedMode || false;
    apiKeyInput.value = data.settings?.apiKey || '';
    toggleKeyInput();
  });

  // Event listeners
  enhancedToggle.addEventListener('change', toggleKeyInput);
  infoIcon.addEventListener('click', toggleInfo);
  apiKeyInput.addEventListener('blur', saveSettings);
  enhancedToggle.addEventListener('change', saveSettings);
  analyzeBtn.addEventListener('click', analyzeCurrentPage);

  function toggleKeyInput() {
    apiKeyInput.style.display = enhancedToggle.checked ? 'block' : 'none';
  }

  function toggleInfo() {
    document.querySelector('.api-details').classList.toggle('show');
  }

  function saveSettings() {
    chrome.storage.sync.set({
      settings: {
        enhancedMode: enhancedToggle.checked,
        apiKey: apiKeyInput.value.trim()
      }
    });
  }

  async function analyzeCurrentPage() {
    analyzeBtn.disabled = true;
    statusDiv.innerHTML = '<div class="spinner">⌛ Analyzing...</div>';
    
    try {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: 'analyze',
        enhancedMode: enhancedToggle.checked,
        apiKey: apiKeyInput.value.trim()
      });
      
      showStatus(
        `Found ${response.found} biased phrases | ${response.contextCount} contexts added`, 
        'success'
      );
      
    } catch (error) {
      showStatus(`Error: ${error.message}`, 'error');
      console.error(error);
    }
    
    analyzeBtn.disabled = false;
  }

  function showStatus(message, type) {
    statusDiv.innerHTML = `
      <div class="status-${type}">
        ${type === 'success' ? '✓' : '✗'} ${message}
      </div>
    `;
  }
});