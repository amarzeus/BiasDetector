# BiasDetector Deployment Guide

This guide will help you set up and run the BiasDetector project on your laptop.

## Backend Setup

### Prerequisites
- Python 3.11 or later
- OpenAI API Key

### Installation Steps

1. **Clone or extract the project:**
   - Extract the `BiasDetector.zip` file to a directory of your choice

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a file named `.env` in the project root directory
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   - Alternatively, you can provide the API key through the extension interface

4. **Download NLTK data (one-time setup):**
   ```python
   python -c "import nltk; nltk.download('punkt')"
   ```

5. **Start the backend server:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```
   - The server will run at http://localhost:5000

## Chrome Extension Setup

1. **Open Chrome Extensions page:**
   - Navigate to `chrome://extensions/` in Chrome browser
   - Enable "Developer mode" using the toggle in the top-right corner

2. **Load the extension:**
   - Click "Load unpacked"
   - Select the `extension` folder from the extracted project

3. **Configure the extension:**
   - Click on the BiasDetector extension icon in your browser toolbar
   - Go to Settings (gear icon)
   - Verify the API URL is set to `http://localhost:5000`
   - Optionally, add your OpenAI API key if you didn't set it as an environment variable

## Usage

1. Navigate to a news article
2. Click the BiasDetector extension icon
3. Click "Analyze Article" 
4. View the bias analysis results, rewritten content, and comparison

## Troubleshooting

- If the extension can't connect to the backend, make sure the server is running at http://localhost:5000
- If you get OpenAI API errors, verify your API key is correct and has sufficient credits
- Check the browser console and server logs for detailed error messages

## System Requirements

- Windows 10/11, macOS, or Linux
- Chrome browser (version 88 or later recommended)
- Internet connection (required for OpenAI API calls)
- 500MB+ free disk space
- 4GB+ RAM recommended