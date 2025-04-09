# BiasDetector - Balancing News Media

![BiasDetector Logo](extension/images/icon128.svg)

## Overview
BiasDetector is a Chrome extension with a Python backend that analyzes news articles for bias and rewrites them to present balanced viewpoints. The extension helps readers gain a more objective understanding of news by highlighting bias, providing context, and offering alternative perspectives.

## Features
- **Bias Detection**: Identifies political, emotional, and factual bias in news articles
- **Content Rewriting**: Rewrites articles to present balanced viewpoints
- **Redline Comparison**: Shows differences between original and rewritten content
- **Context Addition**: Adds missing context to incomplete statements
- **Source Citation**: Provides alternative sources and viewpoints
- **Bias Scoring**: Rates websites based on detected bias over time

## Installation

### Chrome Extension
1. Clone this repository:
   ```
   git clone https://github.com/amarzeus/BiasDetector.git
   ```
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer Mode" (toggle in the top-right corner)
4. Click "Load unpacked" and select the `extension` folder from the cloned repository
5. The BiasDetector icon should now appear in your browser toolbar

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd BiasDetector/backend
<<<<<<< HEAD
   ```
   
2. Install required dependencies:
   ```
   pip install flask flask-cors openai nltk trafilatura gunicorn
   ```

3. Download NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt')"
   ```

4. Start the server:
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

### API Key Setup (Optional)

The extension can operate in two modes:

#### Full Mode (with OpenAI API)
For the complete experience with real-time bias analysis, you'll need an OpenAI API key:

1. Create a `.env` file in the project root directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. Alternatively, you can add your API key in the extension settings.

#### Demo Mode (no API key required)
The extension will run in demo mode when no API key is provided, showing placeholder content and example analysis. This is useful for testing the interface without using the OpenAI API.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2023-2025 Amar Kumar

=======
   
>>>>>>> 7b55693 (Add project files and documentation for the BiasDetector Chrome extension.)
