document.addEventListener('DOMContentLoaded', () => {
  // DOM elements
  const initialView = document.getElementById('initial-view');
  const loadingView = document.getElementById('loading-view');
  const resultsView = document.getElementById('results-view');
  const settingsView = document.getElementById('settings-view');
  
  const analyzeBtn = document.getElementById('analyze-btn');
  const backBtn = document.getElementById('back-btn');
  const settingsBtn = document.getElementById('settings-btn');
  const settingsBackBtn = document.getElementById('settings-back-btn');
  const clearHistoryBtn = document.getElementById('clear-history-btn');
  
  const biasScore = document.getElementById('bias-score');
  const biasScoreBar = document.getElementById('bias-score-bar');
  const biasScoreBadge = document.getElementById('bias-score-badge');
  const biasAssessment = document.getElementById('bias-assessment');
  const biasCategories = document.getElementById('bias-categories');
  const biasInstances = document.getElementById('bias-instances');
  const missingContext = document.getElementById('missing-context');
  const rewrittenContent = document.getElementById('rewritten-content');
  const originalContent = document.getElementById('original-content');
  const compareRewrittenContent = document.getElementById('compare-rewritten-content');
  const diffContent = document.getElementById('diff-content');
  const recentArticles = document.getElementById('recent-articles');
  
  // Default settings
  let settings = {
    apiUrl: 'https://' + window.location.hostname + (window.location.hostname.includes('.replit.app') ? '' : ':5000'),
    openaiApiKey: '',
    autoAnalyze: false
  };
  
  // Load settings
  chrome.storage.local.get('settings', (data) => {
    if (data.settings) {
      settings = data.settings;
      document.getElementById('api-url').value = settings.apiUrl;
      document.getElementById('auto-analyze').checked = settings.autoAnalyze;
      if (settings.openaiApiKey) {
        document.getElementById('openai-api-key').value = settings.openaiApiKey;
      }
    }
  });
  
  // Current analysis data
  let currentAnalysis = null;
  
  // Initialize the extension
  loadRecentArticles();
  
  // Event listeners
  analyzeBtn.addEventListener('click', analyzeCurrentArticle);
  backBtn.addEventListener('click', showInitialView);
  settingsBtn.addEventListener('click', showSettingsView);
  settingsBackBtn.addEventListener('click', showInitialView);
  clearHistoryBtn.addEventListener('click', clearHistory);
  
  document.getElementById('api-url').addEventListener('change', saveSettings);
  document.getElementById('auto-analyze').addEventListener('change', saveSettings);
  document.getElementById('openai-api-key').addEventListener('change', saveSettings);
  
  // Toggle API key visibility
  document.getElementById('toggle-api-key').addEventListener('click', () => {
    const apiKeyInput = document.getElementById('openai-api-key');
    const toggleIcon = document.querySelector('#toggle-api-key i');
    
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleIcon.className = 'bi bi-eye-slash';
    } else {
      apiKeyInput.type = 'password';
      toggleIcon.className = 'bi bi-eye';
    }
  });
  
  // Functions
  function saveSettings() {
    settings.apiUrl = document.getElementById('api-url').value.trim();
    settings.autoAnalyze = document.getElementById('auto-analyze').checked;
    settings.openaiApiKey = document.getElementById('openai-api-key').value.trim();
    
    chrome.storage.local.set({ settings });
  }
  
  function showInitialView() {
    initialView.classList.remove('d-none');
    loadingView.classList.add('d-none');
    resultsView.classList.add('d-none');
    settingsView.classList.add('d-none');
    
    // Refresh recent articles list
    loadRecentArticles();
  }
  
  function showLoadingView(message = 'Analyzing article for bias...') {
    initialView.classList.add('d-none');
    loadingView.classList.remove('d-none');
    resultsView.classList.add('d-none');
    settingsView.classList.add('d-none');
    
    document.getElementById('loading-message').textContent = message;
  }
  
  function showResultsView() {
    initialView.classList.add('d-none');
    loadingView.classList.add('d-none');
    resultsView.classList.remove('d-none');
    settingsView.classList.add('d-none');
    
    // Initialize the Bootstrap tabs if needed
    const tabEl = document.querySelector('#resultTabs .nav-link:first-child');
    const tab = new bootstrap.Tab(tabEl);
    tab.show();
  }
  
  function showSettingsView() {
    initialView.classList.add('d-none');
    loadingView.classList.add('d-none');
    resultsView.classList.add('d-none');
    settingsView.classList.remove('d-none');
  }
  
  function clearHistory() {
    chrome.storage.local.set({ recentArticles: [] }, () => {
      loadRecentArticles();
    });
  }
  
  function loadRecentArticles() {
    chrome.storage.local.get('recentArticles', (data) => {
      const recentArticlesData = data.recentArticles || [];
      
      if (recentArticlesData.length === 0) {
        recentArticles.innerHTML = '<p class="text-center text-muted small py-3">No recent articles analyzed</p>';
        return;
      }
      
      let html = '<div class="list-group list-group-flush">';
      
      recentArticlesData.slice(0, 5).forEach((article, index) => {
        const date = new Date(article.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        html += `
          <div class="list-group-item p-2">
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1 text-truncate" style="max-width: 180px;">${article.title}</h6>
              <small class="text-muted">${getBiasLabel(article.biasScore)}</small>
            </div>
            <small class="text-muted d-block text-truncate" style="max-width: 240px;">${article.url}</small>
            <small class="text-muted">${formattedDate}</small>
            <div class="mt-1">
              <button class="btn btn-sm btn-outline-secondary load-article" data-index="${index}">
                View Analysis
              </button>
            </div>
          </div>
        `;
      });
      
      html += '</div>';
      recentArticles.innerHTML = html;
      
      // Add event listeners to load article buttons
      document.querySelectorAll('.load-article').forEach(button => {
        button.addEventListener('click', (e) => {
          const index = e.target.dataset.index;
          loadSavedArticle(index);
        });
      });
    });
  }
  
  function loadSavedArticle(index) {
    chrome.storage.local.get('recentArticles', (data) => {
      const recentArticlesData = data.recentArticles || [];
      
      if (index >= 0 && index < recentArticlesData.length) {
        const savedAnalysis = recentArticlesData[index];
        currentAnalysis = savedAnalysis;
        
        displayAnalysisResults(savedAnalysis);
        showResultsView();
      }
    });
  }
  
  function analyzeCurrentArticle() {
    showLoadingView();
    
    // Get the current tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      const currentTab = tabs[0];
      
      // Execute content script to extract article
      chrome.scripting.executeScript({
        target: {tabId: currentTab.id},
        function: extractArticleContent
      }, (results) => {
        if (chrome.runtime.lastError) {
          showError(`Error: ${chrome.runtime.lastError.message}`);
          return;
        }
        
        const result = results[0].result;
        
        if (!result.success) {
          showError(`Error: ${result.error}`);
          return;
        }
        
        const articleData = {
          url: currentTab.url,
          title: currentTab.title,
          content: result.content
        };
        
        // Send to backend for analysis
        analyzeArticle(articleData);
      });
    });
  }
  
  function extractArticleContent() {
    try {
      // Try to find the article content
      // This is a simplified version and would need to be enhanced for production
      
      // Check for common article container selectors
      const selectors = [
        'article',
        '[itemtype*="Article"]',
        '.article-content',
        '.story-body',
        '.post-content',
        '#article-body',
        '.article-body',
        '.entry-content',
        '.content-article',
        '.story',
        '.news-content'
      ];
      
      let articleElement = null;
      
      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
          articleElement = element;
          break;
        }
      }
      
      // If no article element found, use the main content or body
      if (!articleElement) {
        articleElement = document.querySelector('main') || document.querySelector('body');
      }
      
      // Get the article content
      let content = '';
      
      // Get the article paragraphs
      const paragraphs = articleElement.querySelectorAll('p');
      if (paragraphs.length > 0) {
        content = Array.from(paragraphs)
          .map(p => p.textContent.trim())
          .filter(text => text.length > 0)
          .join('\n\n');
      } else {
        // If no paragraphs found, use the text content of the article element
        content = articleElement.textContent.trim();
      }
      
      // Clean up the content
      content = content
        .replace(/\s+/g, ' ')  // Replace multiple spaces with a single space
        .replace(/\n\s+/g, '\n')  // Remove leading spaces after newlines
        .trim();
      
      return {
        success: true,
        content
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  function analyzeArticle(articleData) {
    fetch(`${settings.apiUrl}/analyze_and_rewrite`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-OpenAI-Key': settings.openaiApiKey
      },
      body: JSON.stringify({
        url: articleData.url,
        content: articleData.content
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Store the analysis results
      const analysisData = {
        url: articleData.url,
        title: articleData.title,
        content: articleData.content,
        original: data.original,
        rewritten: data.rewritten,
        biasAnalysis: data.bias_analysis,
        comparison: data.comparison,
        biasScore: data.bias_analysis.bias_score,
        timestamp: Date.now()
      };
      
      currentAnalysis = analysisData;
      
      // Save to recent articles
      saveToRecentArticles(analysisData);
      
      // Display the results
      displayAnalysisResults(analysisData);
      showResultsView();
    })
    .catch(error => {
      showError(`Error analyzing article: ${error.message}`);
    });
  }
  
  function saveToRecentArticles(analysisData) {
    chrome.storage.local.get('recentArticles', (data) => {
      const recentArticlesData = data.recentArticles || [];
      
      // Add to the beginning of the array
      recentArticlesData.unshift(analysisData);
      
      // Keep only the last 10 articles
      const updatedArticles = recentArticlesData.slice(0, 10);
      
      chrome.storage.local.set({ recentArticles: updatedArticles });
    });
  }
  
  function displayAnalysisResults(analysis) {
    // Display bias score
    const score = Math.round(analysis.biasScore);
    biasScore.textContent = score;
    biasScoreBar.style.width = `${score}%`;
    biasScoreBar.setAttribute('aria-valuenow', score);
    
    // Set bias score color
    let biasScoreClass = 'bg-success';
    if (score > 30 && score <= 70) {
      biasScoreClass = 'bg-warning';
    } else if (score > 70) {
      biasScoreClass = 'bg-danger';
    }
    biasScoreBar.className = `progress-bar ${biasScoreClass}`;
    biasScoreBadge.className = `bias-score ${biasScoreClass}`;
    
    // Set bias assessment text
    biasAssessment.textContent = getBiasAssessment(score);
    
    // Display bias categories
    const categories = analysis.biasAnalysis.bias_categories;
    if (categories) {
      let categoriesHtml = '<div class="row">';
      
      const categoryLabels = {
        political: 'Political',
        emotional: 'Emotional',
        framing: 'Framing',
        source: 'Source',
        factual: 'Factual',
        omission: 'Omission'
      };
      
      for (const [category, count] of Object.entries(categories)) {
        if (count > 0) {
          const label = categoryLabels[category] || category;
          categoriesHtml += `
            <div class="col-6 mb-2">
              <div class="d-flex justify-content-between">
                <span>${label}</span>
                <span class="badge bg-secondary">${count}</span>
              </div>
              <div class="progress" style="height: 5px;">
                <div class="progress-bar" role="progressbar" style="width: ${Math.min(count * 10, 100)}%;" aria-valuenow="${count}" aria-valuemin="0" aria-valuemax="10"></div>
              </div>
            </div>
          `;
        }
      }
      
      categoriesHtml += '</div>';
      biasCategories.innerHTML = categoriesHtml;
    } else {
      biasCategories.innerHTML = '<p class="text-center text-muted small py-3">No categories data available</p>';
    }
    
    // Display bias instances
    const instances = analysis.biasAnalysis.bias_instances;
    if (instances && instances.length > 0) {
      let instancesHtml = '<div class="accordion" id="biasInstancesAccordion">';
      
      instances.forEach((instance, index) => {
        const severityClass = getSeverityClass(instance.severity);
        
        instancesHtml += `
          <div class="accordion-item">
            <h2 class="accordion-header" id="instance-heading-${index}">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#instance-collapse-${index}" aria-expanded="false" aria-controls="instance-collapse-${index}">
                <div class="d-flex w-100 justify-content-between align-items-center">
                  <span class="text-truncate" style="max-width: 200px;">${instance.text}</span>
                  <span class="badge ${severityClass} ms-2">${instance.category}</span>
                </div>
              </button>
            </h2>
            <div id="instance-collapse-${index}" class="accordion-collapse collapse" aria-labelledby="instance-heading-${index}" data-bs-parent="#biasInstancesAccordion">
              <div class="accordion-body">
                <p class="mb-2"><strong>Biased text:</strong> ${instance.text}</p>
                <p class="mb-2"><strong>Category:</strong> ${instance.category}</p>
                <p class="mb-2"><strong>Severity:</strong> ${instance.severity}/10</p>
                <p class="mb-2"><strong>Balanced alternative:</strong> ${instance.balanced_alternative}</p>
                ${instance.missing_context ? `<p class="mb-0"><strong>Missing context:</strong> ${instance.missing_context}</p>` : ''}
              </div>
            </div>
          </div>
        `;
      });
      
      instancesHtml += '</div>';
      biasInstances.innerHTML = instancesHtml;
    } else {
      biasInstances.innerHTML = '<p class="text-center text-muted small py-3">No bias instances detected</p>';
    }
    
    // Display missing context
    const missingContextItems = analysis.biasAnalysis.missing_context;
    if (missingContextItems && missingContextItems.length > 0) {
      let missingContextHtml = '<div class="accordion" id="missingContextAccordion">';
      
      missingContextItems.forEach((item, index) => {
        const importanceClass = getImportanceClass(item.importance);
        
        missingContextHtml += `
          <div class="accordion-item">
            <h2 class="accordion-header" id="context-heading-${index}">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#context-collapse-${index}" aria-expanded="false" aria-controls="context-collapse-${index}">
                <div class="d-flex w-100 justify-content-between align-items-center">
                  <span class="text-truncate" style="max-width: 200px;">${item.statement}</span>
                  <span class="badge ${importanceClass} ms-2">Importance: ${item.importance}/10</span>
                </div>
              </button>
            </h2>
            <div id="context-collapse-${index}" class="accordion-collapse collapse" aria-labelledby="context-heading-${index}" data-bs-parent="#missingContextAccordion">
              <div class="accordion-body">
                <p class="mb-2"><strong>Statement:</strong> ${item.statement}</p>
                <p class="mb-2"><strong>Missing context:</strong> ${item.context}</p>
                ${item.sources && item.sources.length > 0 ? `
                <p class="mb-0"><strong>Sources:</strong></p>
                <ul class="mb-0 ps-3">
                  ${item.sources.map(source => `<li>${source}</li>`).join('')}
                </ul>` : ''}
              </div>
            </div>
          </div>
        `;
      });
      
      missingContextHtml += '</div>';
      missingContext.innerHTML = missingContextHtml;
    } else {
      missingContext.innerHTML = '<p class="text-center text-muted small py-3">No missing context identified</p>';
    }
    
    // Display original and rewritten content
    rewrittenContent.innerHTML = formatArticleContent(analysis.rewritten);
    originalContent.innerHTML = formatArticleContent(analysis.original);
    compareRewrittenContent.innerHTML = formatArticleContent(analysis.rewritten);
    
    // Display diff
    if (analysis.comparison && analysis.comparison.diff) {
      diffContent.innerHTML = displayDiff(analysis.comparison);
    } else {
      diffContent.innerHTML = '<p class="text-center text-muted small py-3">No comparison data available</p>';
    }
    
    // Create visualization chart
    if (analysis.categories) {
      createBiasChart(analysis);
    }
    
    // Add export button if not exists
    if (!document.getElementById('export-btn')) {
      const exportBtn = document.createElement('button');
      exportBtn.id = 'export-btn';
      exportBtn.className = 'btn btn-outline-secondary btn-sm ms-2';
      exportBtn.innerHTML = '<i class="bi bi-download"></i> Export';
      exportBtn.onclick = exportAnalysis;
      document.querySelector('.result-actions').appendChild(exportBtn);
    }
  }
  
  // Chart visualization functions
  function createBiasChart(data) {
    const ctx = document.getElementById('biasChart').getContext('2d');
    if (window.biasChart) {
      window.biasChart.destroy();
    }
    
    window.biasChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: Object.keys(data.categories),
        datasets: [{
          label: 'Bias Categories',
          data: Object.values(data.categories),
          fill: true,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgb(54, 162, 235)',
          pointBackgroundColor: 'rgb(54, 162, 235)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(54, 162, 235)'
        }]
      },
      options: {
        elements: {
          line: { borderWidth: 3 }
        },
        scales: {
          r: {
            angleLines: { display: true },
            suggestedMin: 0,
            suggestedMax: 100
          }
        }
      }
    });
  }
  
  // Real-time analysis function
  let analysisTimeout;
  function setupRealTimeAnalysis() {
    const textArea = document.getElementById('article-text');
    textArea.addEventListener('input', () => {
      clearTimeout(analysisTimeout);
      analysisTimeout = setTimeout(() => {
        if (textArea.value.length > 100) {
          analyzeText(textArea.value);
        }
      }, 1000);
    });
  }
  
  // Data export/import functions
  function exportAnalysis() {
    const dataStr = JSON.stringify(currentAnalysis, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `bias-analysis-${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  
  function importAnalysis() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
      const file = e.target.files[0];
      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const analysis = JSON.parse(event.target.result);
          currentAnalysis = analysis;
          displayAnalysisResults(analysis);
          showResultsView();
        } catch (error) {
          showError('Invalid analysis file');
        }
      };
      
      reader.readAsText(file);
    };
    
    input.click();
  }
  
  // Error handling function
  function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(errorDiv, document.body.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(errorDiv);
      bsAlert.close();
    }, 5000);
  }
  
  function getBiasLabel(score) {
    if (score <= 30) {
      return 'Low Bias';
    } else if (score <= 70) {
      return 'Medium Bias';
    } else {
      return 'High Bias';
    }
  }
  
  function getBiasAssessment(score) {
    if (score <= 30) {
      return 'This article demonstrates a relatively balanced presentation of the subject matter.';
    } else if (score <= 70) {
      return 'This article shows some bias that may influence the reader\'s perception of the topic.';
    } else {
      return 'This article contains significant bias that substantially impacts the presentation of the subject.';
    }
  }
  
  function getSeverityClass(severity) {
    if (severity <= 3) {
      return 'bg-success';
    } else if (severity <= 7) {
      return 'bg-warning';
    } else {
      return 'bg-danger';
    }
  }
  
  function getImportanceClass(importance) {
    if (importance <= 3) {
      return 'bg-secondary';
    } else if (importance <= 7) {
      return 'bg-warning';
    } else {
      return 'bg-danger';
    }
  }
});
