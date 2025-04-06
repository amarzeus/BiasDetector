// BiasDetector Content Script
// This script runs on web pages to extract article content and inject UI elements

// Store the original article content
let originalArticleContent = null;
let articleContainer = null;
let biasDetectorOverlay = null;
let isOverlayActive = false;

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractArticle') {
    const articleData = extractArticle();
    sendResponse(articleData);
    return true;
  }
  
  if (request.action === 'showOverlay') {
    showBiasDetectorOverlay(request.data);
    sendResponse({ success: true });
    return true;
  }
  
  if (request.action === 'hideOverlay') {
    hideBiasDetectorOverlay();
    sendResponse({ success: true });
    return true;
  }
});

// Extract article content from the page
function extractArticle() {
  try {
    // Find the article container
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
    
    articleContainer = null;
    
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) {
        articleContainer = element;
        break;
      }
    }
    
    // If no article element found, use the main content or body
    if (!articleContainer) {
      articleContainer = document.querySelector('main') || document.querySelector('body');
    }
    
    // Get the article paragraphs
    const paragraphs = articleContainer.querySelectorAll('p');
    let content = '';
    
    if (paragraphs.length > 0) {
      content = Array.from(paragraphs)
        .map(p => p.textContent.trim())
        .filter(text => text.length > 0)
        .join('\n\n');
    } else {
      // If no paragraphs found, use the text content of the article element
      content = articleContainer.textContent.trim();
    }
    
    // Clean up the content
    content = content
      .replace(/\s+/g, ' ')  // Replace multiple spaces with a single space
      .replace(/\n\s+/g, '\n')  // Remove leading spaces after newlines
      .trim();
    
    originalArticleContent = content;
    
    return {
      success: true,
      content: content
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// Show the BiasDetector overlay with the rewritten article
function showBiasDetectorOverlay(data) {
  if (isOverlayActive) {
    hideBiasDetectorOverlay();
  }
  
  // Create overlay container
  biasDetectorOverlay = document.createElement('div');
  biasDetectorOverlay.id = 'bias-detector-overlay';
  biasDetectorOverlay.classList.add('bias-detector-overlay');
  
  // Create the header
  const header = document.createElement('div');
  header.classList.add('bias-detector-header');
  
  const title = document.createElement('div');
  title.classList.add('bias-detector-title');
  title.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="bias-detector-icon">
      <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M12 16V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    BiasDetector
  `;
  
  const biasScore = document.createElement('div');
  biasScore.classList.add('bias-detector-score');
  
  const score = Math.round(data.biasAnalysis.bias_score);
  let biasScoreClass = 'bias-detector-score-low';
  let biasLabel = 'Low Bias';
  
  if (score > 30 && score <= 70) {
    biasScoreClass = 'bias-detector-score-medium';
    biasLabel = 'Moderate Bias';
  } else if (score > 70) {
    biasScoreClass = 'bias-detector-score-high';
    biasLabel = 'High Bias';
  }
  
  biasScore.classList.add(biasScoreClass);
  biasScore.textContent = `${biasLabel}: ${score}/100`;
  
  const closeButton = document.createElement('button');
  closeButton.classList.add('bias-detector-close');
  closeButton.innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
  closeButton.addEventListener('click', hideBiasDetectorOverlay);
  
  header.appendChild(title);
  header.appendChild(biasScore);
  header.appendChild(closeButton);
  
  // Create the tabs
  const tabs = document.createElement('div');
  tabs.classList.add('bias-detector-tabs');
  
  const tabButtonOriginal = document.createElement('button');
  tabButtonOriginal.classList.add('bias-detector-tab', 'active');
  tabButtonOriginal.textContent = 'Original';
  tabButtonOriginal.addEventListener('click', () => {
    setActiveTab(tabButtonOriginal);
    showTabContent('original');
  });
  
  const tabButtonRewritten = document.createElement('button');
  tabButtonRewritten.classList.add('bias-detector-tab');
  tabButtonRewritten.textContent = 'Rewritten';
  tabButtonRewritten.addEventListener('click', () => {
    setActiveTab(tabButtonRewritten);
    showTabContent('rewritten');
  });
  
  const tabButtonCompare = document.createElement('button');
  tabButtonCompare.classList.add('bias-detector-tab');
  tabButtonCompare.textContent = 'Compare';
  tabButtonCompare.addEventListener('click', () => {
    setActiveTab(tabButtonCompare);
    showTabContent('compare');
  });
  
  const tabButtonBias = document.createElement('button');
  tabButtonBias.classList.add('bias-detector-tab');
  tabButtonBias.textContent = 'Bias Analysis';
  tabButtonBias.addEventListener('click', () => {
    setActiveTab(tabButtonBias);
    showTabContent('bias');
  });
  
  tabs.appendChild(tabButtonOriginal);
  tabs.appendChild(tabButtonRewritten);
  tabs.appendChild(tabButtonCompare);
  tabs.appendChild(tabButtonBias);
  
  // Create the content
  const content = document.createElement('div');
  content.classList.add('bias-detector-content');
  
  // Create the tab contents
  const originalTabContent = document.createElement('div');
  originalTabContent.classList.add('bias-detector-tab-content', 'active');
  originalTabContent.id = 'bias-detector-tab-original';
  originalTabContent.innerHTML = formatContent(data.original);
  
  const rewrittenTabContent = document.createElement('div');
  rewrittenTabContent.classList.add('bias-detector-tab-content');
  rewrittenTabContent.id = 'bias-detector-tab-rewritten';
  rewrittenTabContent.innerHTML = formatContent(data.rewritten);
  
  const compareTabContent = document.createElement('div');
  compareTabContent.classList.add('bias-detector-tab-content');
  compareTabContent.id = 'bias-detector-tab-compare';
  compareTabContent.innerHTML = createCompareView(data.original, data.rewritten, data.comparison);
  
  const biasTabContent = document.createElement('div');
  biasTabContent.classList.add('bias-detector-tab-content');
  biasTabContent.id = 'bias-detector-tab-bias';
  biasTabContent.innerHTML = createBiasAnalysisView(data.biasAnalysis);
  
  content.appendChild(originalTabContent);
  content.appendChild(rewrittenTabContent);
  content.appendChild(compareTabContent);
  content.appendChild(biasTabContent);
  
  // Add footer with attribution
  const footer = document.createElement('div');
  footer.classList.add('bias-detector-footer');
  footer.innerHTML = 'BiasDetector by <a href="https://github.com/amarzeus/BiasDetector" target="_blank">Amar Kumar</a>';
  
  // Assemble the overlay
  biasDetectorOverlay.appendChild(header);
  biasDetectorOverlay.appendChild(tabs);
  biasDetectorOverlay.appendChild(content);
  biasDetectorOverlay.appendChild(footer);
  
  // Add the overlay to the page
  document.body.appendChild(biasDetectorOverlay);
  
  // Mark as active
  isOverlayActive = true;
  
  // Helper functions for tabs
  function setActiveTab(activeTab) {
    document.querySelectorAll('.bias-detector-tab').forEach(tab => {
      tab.classList.remove('active');
    });
    activeTab.classList.add('active');
  }
  
  function showTabContent(tabId) {
    document.querySelectorAll('.bias-detector-tab-content').forEach(tabContent => {
      tabContent.classList.remove('active');
    });
    document.getElementById(`bias-detector-tab-${tabId}`).classList.add('active');
  }
}

// Hide the BiasDetector overlay
function hideBiasDetectorOverlay() {
  if (biasDetectorOverlay) {
    biasDetectorOverlay.remove();
    biasDetectorOverlay = null;
    isOverlayActive = false;
  }
}

// Format article content for display
function formatContent(content) {
  if (!content) return '<p>No content available</p>';
  
  return content
    .split('\n\n')
    .map(paragraph => `<p>${paragraph.trim()}</p>`)
    .join('');
}

// Create the side-by-side comparison view
function createCompareView(original, rewritten, comparison) {
  return `
    <div class="bias-detector-compare-container">
      <div class="bias-detector-compare-columns">
        <div class="bias-detector-compare-column">
          <h3>Original</h3>
          <div class="bias-detector-compare-content">
            ${formatContent(original)}
          </div>
        </div>
        <div class="bias-detector-compare-column">
          <h3>Rewritten</h3>
          <div class="bias-detector-compare-content">
            ${formatContent(rewritten)}
          </div>
        </div>
      </div>
      
      <h3 class="bias-detector-compare-diff-title">Detailed Changes</h3>
      <div class="bias-detector-diff">
        ${formatDiff(comparison)}
      </div>
    </div>
  `;
}

// Format the diff for display
function formatDiff(comparison) {
  if (!comparison || !comparison.diff) {
    return '<p>No comparison data available</p>';
  }
  
  let diffHtml = '';
  
  comparison.diff.forEach(diff => {
    if (diff.type === 'unchanged') {
      diffHtml += `<p>${diff.text}</p>`;
    } else if (diff.type === 'removed') {
      diffHtml += `<p class="bias-detector-diff-removed">${diff.text}</p>`;
    } else if (diff.type === 'added') {
      diffHtml += `<p class="bias-detector-diff-added">${diff.text}</p>`;
    }
  });
  
  return diffHtml;
}

// Create the bias analysis view
function createBiasAnalysisView(analysis) {
  let biasInstancesHtml = '';
  const instances = analysis.bias_instances || [];
  
  if (instances.length > 0) {
    biasInstancesHtml = '<div class="bias-detector-instances">';
    
    instances.forEach((instance, index) => {
      const severityClass = instance.severity <= 3 ? 'low' : instance.severity <= 7 ? 'medium' : 'high';
      
      biasInstancesHtml += `
        <div class="bias-detector-instance">
          <div class="bias-detector-instance-header">
            <span class="bias-detector-instance-text">${instance.text}</span>
            <span class="bias-detector-instance-category bias-detector-severity-${severityClass}">${instance.category}</span>
          </div>
          <div class="bias-detector-instance-details">
            <p><strong>Severity:</strong> ${instance.severity}/10</p>
            <p><strong>Balanced alternative:</strong> ${instance.balanced_alternative}</p>
            ${instance.missing_context ? `<p><strong>Missing context:</strong> ${instance.missing_context}</p>` : ''}
          </div>
        </div>
      `;
    });
    
    biasInstancesHtml += '</div>';
  } else {
    biasInstancesHtml = '<p>No bias instances detected</p>';
  }
  
  let categoriesHtml = '';
  const categories = analysis.bias_categories;
  
  if (categories) {
    categoriesHtml = '<div class="bias-detector-categories">';
    
    for (const [category, count] of Object.entries(categories)) {
      if (count > 0) {
        const categoryLabel = category.charAt(0).toUpperCase() + category.slice(1);
        categoriesHtml += `
          <div class="bias-detector-category">
            <div class="bias-detector-category-header">
              <span>${categoryLabel}</span>
              <span class="bias-detector-category-count">${count}</span>
            </div>
            <div class="bias-detector-category-bar">
              <div class="bias-detector-category-progress" style="width: ${Math.min(count * 10, 100)}%;"></div>
            </div>
          </div>
        `;
      }
    }
    
    categoriesHtml += '</div>';
  } else {
    categoriesHtml = '<p>No categories data available</p>';
  }
  
  let missingContextHtml = '';
  const missingContextItems = analysis.missing_context || [];
  
  if (missingContextItems.length > 0) {
    missingContextHtml = '<div class="bias-detector-missing-context">';
    
    missingContextItems.forEach((item, index) => {
      const importanceClass = item.importance <= 3 ? 'low' : item.importance <= 7 ? 'medium' : 'high';
      
      missingContextHtml += `
        <div class="bias-detector-context-item">
          <div class="bias-detector-context-header">
            <span class="bias-detector-context-statement">${item.statement}</span>
            <span class="bias-detector-context-importance bias-detector-importance-${importanceClass}">Importance: ${item.importance}/10</span>
          </div>
          <div class="bias-detector-context-details">
            <p><strong>Missing context:</strong> ${item.context}</p>
            ${item.sources && item.sources.length > 0 ? `
              <p><strong>Sources:</strong></p>
              <ul>
                ${item.sources.map(source => `<li>${source}</li>`).join('')}
              </ul>
            ` : ''}
          </div>
        </div>
      `;
    });
    
    missingContextHtml += '</div>';
  } else {
    missingContextHtml = '<p>No missing context detected</p>';
  }
  
  return `
    <div class="bias-detector-analysis">
      <div class="bias-detector-analysis-section">
        <h3>Bias Score</h3>
        <div class="bias-detector-score-container">
          <div class="bias-detector-score-display">
            <span class="bias-detector-score-value">${Math.round(analysis.bias_score)}</span>
            <span class="bias-detector-score-label">/100</span>
          </div>
          <div class="bias-detector-score-bar">
            <div class="bias-detector-score-progress" style="width: ${analysis.bias_score}%;"></div>
          </div>
          <p class="bias-detector-score-description">${getBiasAssessment(analysis.bias_score)}</p>
        </div>
      </div>
      
      <div class="bias-detector-analysis-section">
        <h3>Bias Categories</h3>
        ${categoriesHtml}
      </div>
      
      <div class="bias-detector-analysis-section">
        <h3>Bias Instances</h3>
        ${biasInstancesHtml}
      </div>
      
      <div class="bias-detector-analysis-section">
        <h3>Missing Context</h3>
        ${missingContextHtml}
      </div>
    </div>
  `;
}

// Get bias assessment text based on score
function getBiasAssessment(score) {
  if (score <= 30) {
    return 'This article shows low levels of bias and presents a relatively balanced viewpoint.';
  } else if (score <= 70) {
    return 'This article contains moderate bias. Some statements may lack context or present a particular viewpoint.';
  } else {
    return 'This article shows significant bias. It presents a one-sided viewpoint with emotional language or missing context.';
  }
}
