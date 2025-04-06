# BiasDetector Documentation

**Author:** Amar Kumar  
**Version:** 1.0.0  
**License:** MIT

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Installation](#installation)
   - [Chrome Extension](#chrome-extension)
   - [Backend Server](#backend-server)
4. [User Guide](#user-guide)
   - [Using the Extension](#using-the-extension)
   - [Understanding Bias Analysis](#understanding-bias-analysis)
   - [Reading Rewritten Content](#reading-rewritten-content)
   - [Comparing Versions](#comparing-versions)
5. [Technical Reference](#technical-reference)
   - [Chrome Extension](#chrome-extension-technical)
   - [Backend API](#backend-api)
   - [AI Processing](#ai-processing)
6. [Development](#development)
   - [Project Structure](#project-structure)
   - [Adding Features](#adding-features)
   - [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)
9. [License](#license)

## Introduction

BiasDetector is a Chrome extension with Python backend that analyzes news articles for bias and rewrites them to present balanced viewpoints. The extension helps readers gain a more objective understanding of news by highlighting bias, providing context, and offering alternative perspectives.

The primary goals of BiasDetector are:

1. **Detect Bias**: Identify different types of bias in news articles including political, emotional, framing, source, factual, and omission bias.
2. **Rewrite Content**: Generate more balanced versions of articles that present multiple perspectives.
3. **Provide Context**: Add important context that may be missing from the original article.
4. **Compare Versions**: Allow users to see differences between original and rewritten content.
5. **Track Bias**: Build a database of bias scores for different news sources over time.

## Architecture Overview

BiasDetector consists of two main components:

1. **Chrome Extension**: A browser extension that extracts article content from web pages, sends it to the backend for analysis, and displays the results to the user.

2. **Python Backend**: A Flask-based API server that uses AI processing (OpenAI GPT-4o) to analyze articles for bias, rewrite them for balance, and return the results to the extension.

The high-level data flow is as follows:

1. User visits a news article website
2. The extension extracts the article content
3. The content is sent to the backend server
4. The backend analyzes the content for bias using AI algorithms
5. The backend rewrites the content to be more balanced
6. The results are sent back to the extension
7. The extension displays the analysis and rewritten content to the user

## Installation

### Chrome Extension

#### Method 1: Chrome Web Store (Coming Soon)

1. Visit the Chrome Web Store (link to be added when available)
2. Click "Add to Chrome"
3. Follow the prompts to install

#### Method 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amarzeus/BiasDetector.git
   ```

2. Open Chrome and navigate to `chrome://extensions/`

3. Enable "Developer Mode" by toggling the switch in the top-right corner

4. Click "Load unpacked" and select the `extension` folder from the cloned repository

5. The BiasDetector icon should now appear in your browser toolbar

### Backend Server

1. Clone the repository (if not already done):
   ```bash
   git clone https://github.com/amarzeus/BiasDetector.git
   ```

2. Navigate to the backend directory:
   ```bash
   cd BiasDetector/backend
   ```

3. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install flask flask-cors openai nltk
   ```

5. Set up your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```

6. Initialize NLTK data (for sentence tokenization):
   ```python
   python -c "import nltk; nltk.download('punkt')"
   ```

7. Run the backend server:
   ```bash
   python main.py
   ```

8. The server should start running on `http://localhost:5000`

## User Guide

### Using the Extension

1. **Basic Usage**:
   - Click the BiasDetector icon in your browser toolbar while on a news article
   - Click "Analyze Article" to start the analysis
   - Wait for the analysis to complete (this may take a few seconds)
   - View the results in the popup window

2. **Extension Popup**:
   - **Analysis Tab**: Shows bias score, categories, instances, and missing context
   - **Rewritten Tab**: Shows the rewritten article with balanced viewpoints
   - **Compare Tab**: Shows side-by-side and inline differences between versions

3. **Page Overlay**:
   - When viewing an article, you can also use the overlay mode
   - Click "View in Article" to show the overlay on the page
   - The overlay allows you to switch between original and rewritten versions directly on the page

4. **Settings**:
   - Click the gear icon in the extension popup to access settings
   - You can configure the backend API URL
   - Enable/disable automatic analysis when visiting news sites
   - Clear your analysis history

### Understanding Bias Analysis

The bias analysis provides several key pieces of information:

1. **Bias Score (0-100)**:
   - 0-30: Low bias - relatively balanced viewpoint
   - 31-70: Moderate bias - some one-sided aspects
   - 71-100: High bias - significantly one-sided viewpoint

2. **Bias Categories**:
   - **Political**: Left-leaning or right-leaning rhetoric
   - **Emotional**: Use of emotional language to influence opinions
   - **Framing**: Presenting facts selectively to promote a particular interpretation
   - **Source**: Selective use of sources or authorities
   - **Factual**: Presenting opinions as facts or using cherry-picked facts
   - **Omission**: Leaving out key information that would change context

3. **Bias Instances**:
   - Specific examples of biased text from the article
   - The category and severity of each instance
   - Suggested balanced alternatives

4. **Missing Context**:
   - Important information that's missing from the article
   - Additional context that would provide a more complete understanding
   - Sources for the missing information (when available)

### Reading Rewritten Content

The rewritten content aims to:

1. Present multiple perspectives on the topic
2. Use neutral language instead of emotionally charged words
3. Add important context that was missing
4. Cite sources for added information
5. Maintain the core information and flow of the original article

### Comparing Versions

The comparison view offers:

1. **Side-by-Side Comparison**: Original and rewritten versions displayed side by side
2. **Inline Differences**: Text highlighted to show what was removed and added
3. **Detailed Changes**: Statistics on the number of modifications made

## Technical Reference

### Chrome Extension Technical

The Chrome extension consists of the following key files:

1. **manifest.json**: Extension configuration
2. **popup.html/js/css**: User interface for the extension popup
3. **content.js**: Script that runs on web pages to extract article content
4. **background.js**: Background script that handles communication and state management

#### Main Components:

- **Article Extraction**: Uses DOM selectors to find and extract article content from web pages.
- **API Communication**: Sends article content to the backend and processes responses.
- **UI Rendering**: Displays analysis results and rewritten content to the user.
- **State Management**: Tracks recently analyzed articles and user settings.

### Backend API

The backend provides the following API endpoints:

#### 1. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "healthy", "message": "Bias Detector API is running"}`

#### 2. Analyze Article
- **URL**: `/analyze`
- **Method**: `POST`
- **Body**: `{"url": "article_url", "content": "article_content"}`
- **Response**: Analysis results including bias score, categories, instances, and missing context

#### 3. Rewrite Article
- **URL**: `/rewrite`
- **Method**: `POST`
- **Body**: `{"content": "article_content", "bias_analysis": {bias_analysis_object}}`
- **Response**: Original and rewritten content with comparison data

#### 4. Analyze and Rewrite
- **URL**: `/analyze_and_rewrite`
- **Method**: `POST`
- **Body**: `{"url": "article_url", "content": "article_content"}`
- **Response**: Complete analysis and rewrite in a single request

### AI Processing

The AI processing uses OpenAI's GPT-4o model to perform three main tasks:

1. **Detect Bias**:
   - Analyzes text for different categories of bias
   - Provides specific instances with severity ratings
   - Generates balanced alternatives for biased statements

2. **Detect Missing Context**:
   - Identifies important information that's missing
   - Provides the missing context with sources
   - Rates the importance of the missing context

3. **Rewrite for Balance**:
   - Rewrites the article to present a more balanced viewpoint
   - Maintains the core information and flow
   - Adds context and alternative perspectives

## Development

### Project Structure

