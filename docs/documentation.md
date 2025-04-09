# BiasDetector Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage Guide](#usage-guide)
4. [Developer Documentation](#developer-documentation)
5. [License](#license)

## Introduction

**BiasDetector** is a Chrome extension that uses advanced AI technology to analyze and neutralize media bias in news articles, providing users with balanced, multi-perspective insights into digital content.

### What is BiasDetector?

BiasDetector helps readers identify and understand bias in news articles. By analyzing text for various types of bias, it offers:

- **Bias Score**: A numerical rating of how biased an article is
- **Bias Categories**: Types of bias present (political, framing, emotional, etc.)
- **Rewritten Content**: A more balanced version of the article
- **Side-by-Side Comparison**: Easy comparison between original and balanced content

### Key Features

- **Instant Analysis**: One-click analysis of any news article
- **Bias Breakdown**: Detailed analysis of different bias types
- **Article Rewriting**: AI-powered rewriting for balanced presentation
- **Missing Context**: Identification of important missing context
- **Recent History**: Access to your previously analyzed articles

## Installation

### Chrome Web Store Installation
The easiest way to install BiasDetector is through the Chrome Web Store:

1. Visit the [Chrome Web Store](https://chrome.google.com/webstore)
2. Search for "BiasDetector"
3. Click "Add to Chrome"
4. Confirm the installation when prompted

### Manual Installation
For developers or users who want to install the latest version directly:

1. Download the latest `BiasDetector.zip` file from the [releases section](https://github.com/amarzeus/BiasDetector/releases)
2. Extract the zip file to a folder on your computer
3. Open Chrome and navigate to `chrome://extensions`
4. Enable "Developer mode" by toggling the switch in the top right corner
5. Click "Load unpacked" and select the folder where you extracted the extension
6. The BiasDetector icon should now appear in your browser toolbar

### Configuration
Once installed, you can configure BiasDetector:

1. Click the BiasDetector icon in your browser toolbar
2. Click the Settings button (gear icon)
3. Enter your OpenAI API key if you have one
4. Adjust other settings as needed
5. Click back to save your settings

Note: BiasDetector will work in demo mode without an API key, but with limited functionality.

## Usage Guide

### Basic Usage

#### Analyzing an Article
1. Navigate to any news article you want to analyze
2. Click the BiasDetector icon in your browser toolbar
3. Click "Analyze Article"
4. Wait for the analysis to complete (usually takes 15-30 seconds)

#### Understanding the Results
The analysis results include:

- **Bias Score**: A 0-100 rating of overall bias (higher = more biased)
- **Bias Categories**: Types of bias detected (political, emotional, etc.)
- **Bias Instances**: Specific examples of biased language
- **Rewritten Article**: A more balanced version of the content
- **Side-by-Side Comparison**: Compare original and balanced versions

#### Viewing the Rewritten Article
1. Once analysis is complete, click the "Rewritten" tab
2. Read the AI-generated neutral version of the article
3. Click "Compare" to see a side-by-side comparison highlighting changes

#### Analyzing Missing Context
1. Click the "Missing Context" tab after analysis
2. Review the AI-identified important context that may be missing
3. This helps understand what perspectives or facts might be omitted

### Advanced Features

#### Working with API Keys
For full functionality, you can use your own OpenAI API key:

1. Click the Settings button (gear icon)
2. Enter your OpenAI API key in the designated field
3. Click back to save

Without an API key, BiasDetector operates in demo mode with limited functionality.

#### Recent Articles History
BiasDetector stores your recently analyzed articles:

1. Click the "Recent" tab in the extension popup
2. Select any previous analysis to view it again
3. Click "Clear History" to remove all stored analyses

### Troubleshooting

If BiasDetector fails to analyze an article:

1. Refresh the page and try again
2. Check if the article content is properly loading
3. Ensure your API key is valid (if using one)
4. Some complex page layouts may not be properly detected

## Developer Documentation

### Project Structure

BiasDetector consists of three main components:

1. **Chrome Extension**: User interface and article extraction
2. **Python Backend**: API server handling bias analysis
3. **GitHub Pages Website**: Documentation and distribution

#### Chrome Extension

```
extension/
├── manifest.json    # Extension configuration
├── popup.html       # Main UI
├── popup.js         # UI logic
├── content.js       # Article extraction
├── background.js    # Background processes
└── styles.css       # UI styling
```

#### Python Backend

```
backend/
├── app.py           # Flask API server
├── bias_detector.py # Core analysis logic
└── ai_processor.py  # OpenAI API interactions
```

### Setting Up Development Environment

#### Prerequisites
- Python 3.8+
- Node.js and npm
- Chrome browser

#### Extension Development

1. Clone the repository
   ```
   git clone https://github.com/amarzeus/BiasDetector.git
   cd BiasDetector
   ```

2. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension` folder

3. Make changes to the extension files
4. Reload the extension in Chrome to test changes

#### Backend Development

1. Set up Python environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key
   ```
   export OPENAI_API_KEY=your_api_key  # On Windows: set OPENAI_API_KEY=your_api_key
   ```

3. Run the development server
   ```
   cd backend
   flask run --host=0.0.0.0 --port=5000 --debug
   ```

4. Test the API endpoints using Postman or curl

### API Documentation

#### Endpoints

##### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Bias Detector API is running"
}
```

##### POST /analyze
Analyze article content for bias

**Request:**
```json
{
  "url": "https://example.com/article",
  "content": "Article text content..."
}
```

**Response:**
```json
{
  "bias_score": 75,
  "bias_categories": {
    "political": 0.8,
    "emotional": 0.6,
    "framing": 0.7
  },
  "bias_instances": [
    {
      "text": "Example biased text",
      "category": "political",
      "severity": 0.8
    }
  ]
}
```

##### POST /rewrite
Rewrite article to present a more balanced viewpoint

**Request:**
```json
{
  "content": "Article text content...",
  "bias_analysis": {
    // Bias analysis object from /analyze
  }
}
```

**Response:**
```json
{
  "original": "Original text...",
  "rewritten": "Rewritten text...",
  "comparison": {
    "diff": [
      // Difference information
    ]
  }
}
```

##### POST /analyze_and_rewrite
Analyze and rewrite in one step

**Request:**
```json
{
  "url": "https://example.com/article",
  "content": "Article text content..."
}
```

**Response:**
```json
{
  "original": "Original text...",
  "rewritten": "Rewritten text...",
  "bias_analysis": {
    // Bias analysis object
  },
  "comparison": {
    // Comparison object
  }
}
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Building for Distribution

To build the extension for distribution:

1. Update version in `manifest.json`
2. Run the build script:
   ```
   python build_extension.py
   ```
3. The packaged extension will be in the `dist/` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

© 2023 Amar Kumar. All rights reserved.