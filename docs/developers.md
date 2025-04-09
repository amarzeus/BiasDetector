---
layout: default
title: Developer Documentation - BiasDetector
---

# Developer Documentation

## Project Structure

BiasDetector consists of three main components:

1. **Chrome Extension**: User interface and article extraction
2. **Python Backend**: API server handling bias analysis
3. **GitHub Pages Website**: Documentation and distribution

### Chrome Extension

```
extension/
├── manifest.json    # Extension configuration
├── popup.html       # Main UI
├── popup.js         # UI logic
├── content.js       # Article extraction
├── background.js    # Background processes
└── styles.css       # UI styling
```

### Python Backend

```
backend/
├── app.py           # Flask API server
├── bias_detector.py # Core analysis logic
└── ai_processor.py  # OpenAI API interactions
```

## Core Technologies

### Web Scraping with Trafilatura

BiasDetector uses Trafilatura for extracting clean text content from web pages. This library efficiently removes ads, navigation, and other non-content elements.

Example usage:
```python
import trafilatura

def get_website_text_content(url):
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text
```

### AI Analysis with OpenAI

The project leverages OpenAI's GPT-4o model for bias detection and article rewriting. Key features:

- **Bias Detection**: Identifies different types of bias in text
- **Content Rewriting**: Generates balanced alternatives to biased content
- **Missing Context**: Suggests information that may be missing for a balanced view

Example OpenAI integration:
```python
from openai import OpenAI

openai = OpenAI(api_key=api_key)

response = openai.chat.completions.create(
    model="gpt-4o",  # Using the latest model available
    messages=[
        {"role": "system", "content": "Analyze the following text for bias..."},
        {"role": "user", "content": text}
    ],
    response_format={"type": "json_object"}
)
```

### Two-Mode Operation

The system operates in two modes:
1. **Full Mode**: Uses OpenAI API for accurate analysis (requires API key)
2. **Demo Mode**: Uses pre-defined patterns for demonstration (no API key needed)

## API Documentation

### Endpoints

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Bias Detector API is running"
}
```

#### POST /analyze
Analyze article content for bias

#### POST /rewrite
Rewrite article to present a more balanced viewpoint

#### POST /analyze_and_rewrite
Analyze and rewrite in one step

## License

This project is licensed under the MIT License - see the LICENSE file for details.
