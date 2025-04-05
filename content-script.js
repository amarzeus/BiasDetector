/**
 * @license
 * Copyright 2024 Amar Kumar
 * SPDX-License-Identifier: MIT
 */

// Initialize diff-match-patch
const dmp = new diff_match_patch();

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyze') {
    analyzePage(request.enhancedMode, request.apiKey)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({error: error.message}));
    return true;
  }
});

async function analyzePage(enhancedMode, apiKey) {
  try {
    const article = document.querySelector('article') || document.body;
    const originalHTML = article.innerHTML;
    const text = article.innerText.slice(0, 2000);
    
    const response = await fetch('http://127.0.0.1:5000/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ 
        text, 
        enhancedMode, 
        apiKey 
      })
    });
    
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    
    // Generate diff
    const diffs = dmp.diff_main(originalHTML, data.neutralized);
    dmp.diff_cleanupSemantic(diffs);
    
    // Apply styling
    article.innerHTML = dmp.diff_prettyHtml(diffs)
      .replace(/<ins>/g, '<ins class="added-text">')
      .replace(/<del>/g, '<del class="removed-text">');
    
    // Add context markers
    data.context.forEach((ctx, i) => {
      const marker = document.createElement('sup');
      marker.className = 'context-marker';
      marker.dataset.context = ctx;
      marker.innerHTML = `[${i+1}]`;
      article.appendChild(marker);
    });
    
    return { 
      found: data.biased_phrases.length,
      contextCount: data.context.length 
    };
    
  } catch (error) {
    console.error('Content script error:', error);
    throw error;
  }
}

// Add styles
const style = document.createElement('style');
style.textContent = `
  .added-text {
    background-color: #e6ffec;
    text-decoration: none;
    border-left: 2px solid #2ecc71;
    padding: 0 2px;
  }
  .removed-text {
    background-color: #ffebee;
    text-decoration: none;
    border-left: 2px solid #e74c3c;
    padding: 0 2px;
  }
  .context-marker {
    color: #3498db;
    cursor: pointer;
    font-size: 0.8em;
    margin: 0 2px;
  }
  .context-marker:hover::after {
    content: attr(data-context);
    position: absolute;
    background: white;
    border: 1px solid #ddd;
    padding: 8px;
    z-index: 100;
    max-width: 300px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  }
`;
document.head.appendChild(style);

// Load diff-match-patch library
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/diff-match-patch/20121119/diff_match_patch.min.js';
document.head.appendChild(script);