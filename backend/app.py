"""Backend application module with API routes"""
from typing import Union, Dict, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import os
import sys
import secrets
from backend.ai_processor import analyze_text, rewrite_text, analyze_and_rewrite
from backend.errors import ValidationError, handle_error

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Use a strong secret key from environment or generate a random one
if 'SESSION_SECRET' in os.environ:
    app.secret_key = os.environ['SESSION_SECRET']
else:
    app.secret_key = secrets.token_hex(32)
    logger.warning("No SESSION_SECRET environment variable set. Using random secret key.")

# Enable CORS for Chrome extension with proper configuration
CORS(app, 
     origins=os.environ.get('ALLOWED_ORIGINS', '*'),
     supports_credentials=True,
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'X-OpenAI-Key'])

# Register error handlers
@app.errorhandler(Exception)
def handle_all_errors(error: Exception) -> Union[Response, tuple[Response, int]]:
    """Global error handler for all exceptions"""
    return handle_error(error)

@app.route('/', methods=['GET'])
def index():
    """Main page of the API server"""
    return """
    <html>
        <head>
            <title>BiasDetector API Server</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }
                h1, h2 {
                    color: #2c3e50;
                }
                .status {
                    display: inline-block;
                    background-color: #27ae60;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                code {
                    background-color: #f8f8f8;
                    padding: 2px 5px;
                    border-radius: 3px;
                    font-family: monospace;
                }
                ul {
                    margin-top: 20px;
                }
                .card {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .btn {
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                }
                .btn:hover {
                    background-color: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>BiasDetector API Server</h1>
                <p class="status">Running</p>
            </div>
            
            <div class="card">
                <h2>Live Demo</h2>
                <p>Try out the BiasDetector with a sample article:</p>
                <a href="/demo" class="btn">View Demo</a>
            </div>
            
            <div class="card">
                <h2>API Endpoints</h2>
                <ul>
                    <li><code>/health</code> - Health check endpoint</li>
                    <li><code>/analyze</code> - Analyze article content for bias</li>
                    <li><code>/rewrite</code> - Rewrite article to present balanced viewpoint</li>
                    <li><code>/analyze_and_rewrite</code> - Analyze and rewrite in one step</li>
                    <li><code>/demo</code> - Interactive demo with sample article</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>Usage</h2>
                <p>This API server is intended to be used with the BiasDetector Chrome extension.</p>
                <p>For more information, see the project documentation.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the API"""
    return jsonify({"status": "healthy", "message": "Bias Detector API is running"})

@app.route('/analyze', methods=['POST'])
def analyze() -> tuple[Response, int]:
    """
    Analyze article content for bias
    
    Expected JSON payload: {"url": "article_url", "content": "article_content"}
    
    Returns:
        tuple[Response, int]: JSON response with analysis results and HTTP status code
    
    Raises:
        ValidationError: If request data is invalid
        APIError: If OpenAI API fails
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No JSON data provided")
            
        content = data.get('content')
        if not content:
            raise ValidationError("No article content provided")
            
        context = {"url": data.get('url')} if data.get('url') else None
        analysis = analyze_text(content, context)
        
        return jsonify(analysis), 200
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error in analyze endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/rewrite', methods=['POST'])
def rewrite():
    """
    Rewrite article to remove bias
    Expected JSON payload: {"content": "article_content", "bias_analysis": {bias_analysis_object}}
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No JSON data provided")
            
        content = data.get('content')
        if not content:
            raise ValidationError("No article content provided")
            
        analysis = data.get('bias_analysis')
        if not analysis:
            raise ValidationError("No bias analysis provided")
            
        rewritten = rewrite_text(content, analysis)
        
        return jsonify({
            "rewritten_content": rewritten
        }), 200
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error in rewrite endpoint")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_and_rewrite', methods=['POST'])
def analyze_and_rewrite_endpoint():
    """
    Analyze article for bias and rewrite it in one step
    Expected JSON payload: {"url": "article_url", "content": "article_content"}
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No JSON data provided")
            
        content = data.get('content')
        if not content:
            raise ValidationError("No article content provided")
            
        context = {"url": data.get('url')} if data.get('url') else None
        result = analyze_and_rewrite(content, context)
        
        return jsonify(result), 200
    
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error in analyze_and_rewrite endpoint")
        return jsonify({"error": str(e)}), 500
