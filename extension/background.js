// BiasDetector Background Script
// This script runs in the background and handles communication between the popup and content scripts

// Default settings
const defaultSettings = {
  apiUrl: 'http://localhost:5000',
  openaiApiKey: '',
  autoAnalyze: false
};

// Store the last analyzed article data
let lastAnalyzedData = null;

// Initialize extension on install
chrome.runtime.onInstalled.addListener(() => {
  // Set default settings
  chrome.storage.local.get('settings', (data) => {
    if (!data.settings) {
      chrome.storage.local.set({ settings: defaultSettings });
    }
  });
  
  // Initialize recent articles array
  chrome.storage.local.get('recentArticles', (data) => {
    if (!data.recentArticles) {
      chrome.storage.local.set({ recentArticles: [] });
    }
  });
});

// Listen for messages from the popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Handle analyze request from popup
  if (request.action === 'analyzeArticle') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentTab = tabs[0];
      
      // Execute content script to extract article
      chrome.scripting.executeScript({
        target: { tabId: currentTab.id },
        function: () => {
          // This function runs in the context of the page
          // It extracts the article content and sends it back
          
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
          
          let articleContainer = null;
          
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
          
          return {
            success: true,
            content: content
          };
        }
      }, (results) => {
        if (chrome.runtime.lastError) {
          sendResponse({ 
            success: false, 
            error: chrome.runtime.lastError.message 
          });
          return;
        }
        
        const result = results[0].result;
        
        if (!result.success) {
          sendResponse({ 
            success: false, 
            error: result.error 
          });
          return;
        }
        
        // Get API URL from settings
        chrome.storage.local.get('settings', (data) => {
          const settings = data.settings || defaultSettings;
          const apiUrl = settings.apiUrl;
          const openaiApiKey = settings.openaiApiKey || '';
          
          // Send article to backend for analysis
          fetch(`${apiUrl}/analyze_and_rewrite`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-OpenAI-Key': openaiApiKey
            },
            body: JSON.stringify({
              url: currentTab.url,
              content: result.content
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
              url: currentTab.url,
              title: currentTab.title,
              content: result.content,
              original: data.original,
              rewritten: data.rewritten,
              biasAnalysis: data.bias_analysis,
              comparison: data.comparison,
              biasScore: data.bias_analysis.bias_score,
              timestamp: Date.now()
            };
            
            lastAnalyzedData = analysisData;
            
            // Save to recent articles
            saveToRecentArticles(analysisData);
            
            // Send response back to popup
            sendResponse({ 
              success: true, 
              data: analysisData 
            });
          })
          .catch(error => {
            sendResponse({ 
              success: false, 
              error: error.message 
            });
          });
        });
        
        // Keep the message channel open for the async response
        return true;
      });
      
      // Keep the message channel open for the async response
      return true;
    });
    
    // Keep the message channel open for the async response
    return true;
  }
  
  // Handle show overlay request
  if (request.action === 'showOverlay') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentTab = tabs[0];
      
      // Send message to content script to show overlay
      chrome.tabs.sendMessage(currentTab.id, {
        action: 'showOverlay',
        data: request.data
      }, (response) => {
        sendResponse(response);
      });
    });
    
    // Keep the message channel open for the async response
    return true;
  }
  
  // Handle hide overlay request
  if (request.action === 'hideOverlay') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentTab = tabs[0];
      
      // Send message to content script to hide overlay
      chrome.tabs.sendMessage(currentTab.id, {
        action: 'hideOverlay'
      }, (response) => {
        sendResponse(response);
      });
    });
    
    // Keep the message channel open for the async response
    return true;
  }
});

// Save analysis to recent articles
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
