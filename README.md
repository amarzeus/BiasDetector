# BiasDetector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![BiasDetector Logo](extension/images/icon128.svg)

## 🎯 Overview

BiasDetector is an advanced tool designed to identify and mitigate bias in text content. It combines machine learning with natural language processing to help users create more inclusive and fair content. The system includes both a powerful web API and a browser extension for real-time analysis.

## 🌟 Key Features

- **Real-time Bias Detection**: Identifies political, emotional, and factual bias in text content
- **Smart Rewriting**: AI-powered suggestions for more balanced and inclusive language
- **Context Enhancement**: Adds missing context and alternative viewpoints
- **Source Analysis**: Evaluates and rates content sources for bias patterns
- **Browser Integration**: Seamless Chrome/Firefox extension
- **REST API**: Enterprise-ready API for custom integrations
- **Modern UI**: Clean, intuitive interface for all skill levels

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js 14+ (for extension development)
- Chrome or Firefox browser

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BiasDetector.git
   cd BiasDetector
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   # Development mode with hot reloading
   python main.py --dev

   # Production mode
   python main.py
   ```

### Browser Extension Setup

1. Open Chrome/Firefox extensions page
2. Enable Developer Mode
3. Click "Load unpacked" and select the `extension` folder
4. The BiasDetector icon will appear in your toolbar

### API Key Configuration (Optional)

For enhanced analysis capabilities:

1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
2. Or configure via extension settings

The system operates in two modes:
- **Full Mode**: Complete analysis with OpenAI integration
- **Demo Mode**: Basic functionality without API key

## 🛠️ Development Guide

### Backend Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with debug logging
python main.py --dev --log-level=DEBUG
```

### Extension Development

```bash
cd extension
npm install
npm run build
```

## 📚 API Documentation

### Core Endpoints

- `POST /analyze`: Analyze text for potential bias
- `POST /rewrite`: Get suggestions for more inclusive language
- `POST /analyze_and_rewrite`: Combined analysis and rewriting
- `GET /health`: API health check

Example usage:
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

Detailed API documentation available at `/api` when server is running.

## 🔧 Configuration

Configure via environment variables or command-line:

- `PORT`: Server port (default: 5000)
- `HOST`: Host address (default: 0.0.0.0)
- `SESSION_SECRET`: Session security key
- `LOG_LEVEL`: Logging level (default: INFO)

## 📦 Project Structure

```
BiasDetector/
├── backend/           # Core Python backend
├── docs/             # Documentation
├── extension/        # Browser extension
├── templates/        # HTML templates
├── website/          # Marketing website
├── main.py          # Main application
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Follow our coding standards and include tests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All our amazing contributors
- Built with Flask and modern web technologies
- Powered by advanced NLP models

## 📧 Contact & Support

- Website: [https://biasdetector.dev](https://biasdetector.dev)
- Email: support@biasdetector.dev
- Twitter: [@BiasDetector](https://twitter.com/BiasDetector)

---

Made with ❤️ by the BiasDetector team
