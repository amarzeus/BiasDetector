# 🔍 BiasDetector Chrome Extension 
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/amarzeus/BiasDetector?style=social)](https://github.com/amarzeus/BiasDetector)

**AI-powered tool that detects media bias and provides contextual analysis**

![Demo](docs/assets/demo.gif)

## ✨ Features
- 🚨 Real-time bias detection using BERT models
- 📈 Economic context (inflation, household metrics)
- 🟢🔴 Side-by-side comparison view
- 🛠️ Self-contained Chrome extension + local API

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Chrome browser
- [BLS API Key](https://data.bls.gov/registrationEngine/) (free)

### Installation
```powershell
# Clone repository
git clone https://github.com/amarzeus/BiasDetector.git
cd BiasDetector/backend

# Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables (PowerShell)
[System.Environment]::SetEnvironmentVariable('BLS_API_KEY','your_key','User')

Load Extension
Visit chrome://extensions

Enable Developer mode

Click Load unpacked → Select /extension folder

📸 Demo
Original Article	Analyzed Version
Before	After

🏗️ Architecture
flowchart TD
    A[Chrome Extension] -->|Text| B[Flask API]
    B --> C[Bias Detection]
    B --> D[Context Engine]
    C --> E[Highlighted Phrases]
    D --> F[Economic Data]
    E & F --> G[Redline Output]

    📂 Files
    BiasDetector/
├── backend/           # Python server
│   ├── bias_detector.py
│   └── requirements.txt
├── extension/         # Chrome files
│   ├── manifest.json
│   ├── content-script.js
│   └── popup/
├── docs/
│   ├── TECHNICAL.md   # Architecture details
│   └── assets/        # Demo media
└── LICENSE

🤝 How to Contribute
Fork the repository

Create a branch (git checkout -b improve-feature)

Commit changes (git commit -m 'Add feature')

Push (git push origin improve-feature)

Open a Pull Request

📜 License
MIT © 2024 Amar Kumar
Project Link: https://github.com/amarzeus/BiasDetector