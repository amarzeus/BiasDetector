# Developer Guide

## Development Environment Setup

### Backend Development

1. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Environment Variables**
   ```bash
   # Create .env file in project root
   OPENAI_API_KEY=your_api_key_here
   SESSION_SECRET=your_session_secret
   LOG_LEVEL=DEBUG
   ```

3. **Running Tests**
   ```bash
   pytest
   pytest --cov=backend  # With coverage
   ```

### Extension Development

1. **Node.js Setup**
   ```bash
   cd extension
   npm install
   ```

2. **Development Build**
   ```bash
   npm run dev     # Watch mode
   npm run build   # Production build
   ```

3. **Testing the Extension**
   - Load unpacked extension in Chrome/Firefox
   - Enable developer mode in browser
   - Use React Developer Tools for component inspection

## Architecture

### Backend Components

1. **AI Processor (`ai_processor.py`)**
   - Handles OpenAI API integration
   - Manages text analysis and rewriting
   - Implements bias detection algorithms

2. **Bias Detector (`bias_detector.py`)**
   - Core bias detection logic
   - Pattern matching and analysis
   - Scoring and rating system

3. **Flask App (`app.py`)**
   - REST API endpoints
   - Request handling and validation
   - Response formatting

### Extension Components

1. **Background Script (`background.js`)**
   - Handles browser events
   - Manages communication with backend
   - Controls extension state

2. **Content Script (`content.js`)**
   - DOM manipulation
   - Text extraction
   - UI overlay management

3. **Popup Interface (`popup.js`, `popup.html`)**
   - User settings
   - Quick actions
   - Results display

## API Reference

### Endpoints

#### 1. Analyze Text
```http
POST /analyze
Content-Type: application/json

{
    "text": "string",
    "options": {
        "detectPolitical": boolean,
        "detectEmotional": boolean,
        "detectFactual": boolean
    }
}
```

#### 2. Rewrite Text
```http
POST /rewrite
Content-Type: application/json

{
    "text": "string",
    "style": "balanced|neutral|academic"
}
```

#### 3. Combined Analysis
```http
POST /analyze_and_rewrite
Content-Type: application/json

{
    "text": "string",
    "options": {
        "detectPolitical": boolean,
        "detectEmotional": boolean,
        "detectFactual": boolean
    },
    "style": "balanced|neutral|academic"
}
```

### Response Format

```json
{
    "success": true,
    "data": {
        "biasScore": number,
        "categories": {
            "political": number,
            "emotional": number,
            "factual": number
        },
        "suggestions": [
            {
                "original": "string",
                "suggested": "string",
                "reason": "string"
            }
        ],
        "rewrittenText": "string"
    },
    "errors": []
}
```

## Contributing Guidelines

### Code Style

1. **Python**
   - Follow PEP 8
   - Use type hints
   - Document with docstrings
   - Maximum line length: 88 characters (Black formatter)

2. **JavaScript**
   - Use ESLint configuration
   - Follow Prettier formatting
   - Use TypeScript for type safety

### Git Workflow

1. **Branch Naming**
   - feature/description
   - bugfix/description
   - hotfix/description
   - release/version

2. **Commit Messages**
   ```
   type(scope): description

   [optional body]
   [optional footer]
   ```
   Types: feat, fix, docs, style, refactor, test, chore

### Testing Requirements

1. **Backend Tests**
   - Unit tests for all modules
   - Integration tests for API endpoints
   - Minimum 80% coverage

2. **Extension Tests**
   - Component tests
   - E2E tests with Cypress
   - Browser compatibility tests

## Deployment Guide

### Backend Deployment

1. **Environment Setup**
   ```bash
   python -m venv prod-env
   source prod-env/bin/activate
   pip install -r requirements.txt
   ```

2. **Running with Gunicorn**
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:5000 main:app
   ```

### Extension Publishing

1. **Build Production Version**
   ```bash
   cd extension
   npm run build
   ```

2. **Package Extension**
   - Zip contents of build directory
   - Submit to Chrome Web Store/Firefox Add-ons

## Monitoring and Maintenance

### Logging

- Use structured logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Include request ID in logs
- Monitor API usage and errors

### Performance Metrics

- Response times
- Error rates
- API usage statistics
- Memory consumption
- CPU utilization

### Security

- Regular dependency updates
- API key rotation
- Input validation
- Rate limiting
- CORS configuration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
