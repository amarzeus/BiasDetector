# Standard library imports
import os
import sys
import argparse
import logging
import time
from functools import wraps
from datetime import datetime
import json
from pathlib import Path

# Third-party imports
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
from flask_cors import CORS
import markdown
from werkzeug.contrib.cache import SimpleCache
from prometheus_client import Counter, Histogram, generate_latest


# Configure metrics
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BiasDetector")

# Initialize cache with larger default timeout for API responses
cache = SimpleCache(default_timeout=300)

class Config:
    def __init__(self):
        self.config_path = Path("config.json")
        self.load_config()
        
    def load_config(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "api": {
                    "rate_limit": 100,
                    "cache_timeout": 300
                },
                "analysis": {
                    "min_text_length": 100,
                    "max_text_length": 10000,
                    "default_model": "gpt-4o"
                },
                "features": {
                    "real_time_analysis": True,
                    "source_credibility": True,
                    "comparative_analysis": True
                }
            }
            self.save_config()
            
    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=2)
            
config = Config()

# Enhanced performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        status_code = 200
        
        try:
            response = f(*args, **kwargs)
            
            if isinstance(response, (tuple, list)):
                response, status_code = response
                
        except Exception as e:
            status_code = 500
            raise
            
        finally:
            duration = time.time() - start_time
            endpoint = request.endpoint or 'unknown'
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                endpoint=endpoint
            ).observe(duration)
            
            # Log detailed performance data
            logger.info({
                'method': request.method,
                'path': request.path,
                'endpoint': endpoint,
                'duration': f"{duration:.2f}s",
                'status': status_code,
                'ip': request.remote_addr
            })
        
        if isinstance(response, str):
            response = make_response(response)
            
        # Add performance headers
        response.headers['X-Response-Time'] = f"{duration:.2f}s"
        response.headers['X-Rate-Limit-Remaining'] = str(get_rate_limit())
        
        return response if isinstance(response, str) else (response, status_code)
    return decorated_function

# Rate limiting functionality
def get_rate_limit():
    """Get remaining API calls for current IP"""
    ip = request.remote_addr
    current = cache.get(f"rate_limit_{ip}") or 0
    return max(0, config.settings['api']['rate_limit'] - current)

def update_rate_limit():
    """Update rate limit counter for current IP"""
    ip = request.remote_addr
    current = cache.get(f"rate_limit_{ip}") or 0
    cache.set(f"rate_limit_{ip}", current + 1, timeout=3600)

# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {f.__name__}: {str(e)}")
            error_response = {
                'error': str(e),
                'type': e.__class__.__name__,
                'timestamp': datetime.utcnow().isoformat()
            }
            return jsonify(error_response), 500
    return decorated_function

# Create Flask application
app = Flask(__name__, static_folder='docs/assets')
app.secret_key = os.environ.get("SESSION_SECRET", "bias_detector_secret_key")

# Enable CORS with more specific configuration
CORS(app, 
     origins=["http://localhost:*", "https://*.biasdetector.dev"],
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])


# Register backend API endpoints with enhanced functionality
try:
    from backend.app import (
        health_check, analyze, rewrite, analyze_and_rewrite,
        analyze_v2, comparative_analysis, check_source_credibility
    )
    
    @app.route('/health', methods=['GET'])
    @monitor_performance
    @handle_errors
    def wrapped_health_check():
        status = health_check()
        return {
            **status,
            'config': config.settings,
            'metrics': {
                'requests': generate_latest().decode()
            }
        }
    
    @app.route('/api/v2/analyze', methods=['POST'])
    @monitor_performance
    @handle_errors
    def wrapped_analyze_v2():
        if get_rate_limit() <= 0:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': 3600
            }), 429
            
        update_rate_limit()
        return analyze_v2()
        
    @app.route('/api/v2/compare', methods=['POST'])
    @monitor_performance
    @handle_errors
    def wrapped_comparative_analysis():
        if get_rate_limit() <= 0:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': 3600
            }), 429
            
        update_rate_limit()
        return comparative_analysis()
        
    @app.route('/api/v2/source-credibility', methods=['GET'])
    @monitor_performance
    @handle_errors
    def wrapped_source_credibility():
        if get_rate_limit() <= 0:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': 3600
            }), 429
            
        update_rate_limit()
        return check_source_credibility()
        
    # Legacy API endpoints with rate limiting
    @app.route('/analyze', methods=['POST'])
    @monitor_performance
    @handle_errors
    def wrapped_analyze():
        if get_rate_limit() <= 0:
            return jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': 3600
            }), 429
            
        update_rate_limit()
        return analyze()
    
    @app.route('/rewrite', methods=['POST'])
    @monitor_performance
    @handle_errors
    def wrapped_rewrite():
        return rewrite()
    
    @app.route('/analyze_and_rewrite', methods=['POST'])
    @monitor_performance
    @handle_errors
    def wrapped_analyze_and_rewrite():
        return analyze_and_rewrite()
    
    logger.info("Backend API routes registered successfully")
except ImportError as e:
    logger.warning(f"Failed to import backend API: {e}")

# Add system health endpoint
@app.route('/system/health')
@monitor_performance
def system_health():
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.environ.get('APP_VERSION', '1.0.0'),
        'python_version': sys.version,
        'environment': os.environ.get('FLASK_ENV', 'production')
    }
    return jsonify(health_info)

# Utility: Render Markdown documentation with caching
def render_markdown(path, cache_timeout=300):  # Cache for 5 minutes
    cache_key = f'markdown_{path}'
    content = cache.get(cache_key)
    
    if content is None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                title = "BiasBuster"
                if content.startswith('---'):
                    end = content.find('---', 3)
                    if end != -1:
                        front_matter = content[3:end].strip()
                        for line in front_matter.split('\n'):
                            if line.startswith('title:'):
                                title = line[6:].strip()
                        content = content[end+3:].strip()
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
                rendered = render_template('layout.html', title=title, content=html_content)
                cache.set(cache_key, rendered, timeout=cache_timeout)
                return rendered
        except FileNotFoundError:
            return "Page not found", 404
    return content


# Documentation and static asset routes
@app.route('/')
def index():
    return render_markdown('docs/README.md')

@app.route('/installation')
def installation():
    return render_markdown('docs/installation.md')

@app.route('/usage')
def usage():
    return render_markdown('docs/usage.md')

@app.route('/developers')
def developers():
    return render_markdown('docs/developers.md')

@app.route('/api')
def api_docs():
    return render_markdown('docs/api_endpoints.md')

@app.route('/extension.zip')
def download_extension():
    return send_from_directory('docs', 'BiasDetector-Extension.zip')

@app.route('/developer.zip')
def download_developer_package():
    return send_from_directory('docs', 'BiasDetector-Dev.zip')

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('docs/assets', path)


# Ensure template exists for Markdown rendering
TEMPLATE_PATH = 'templates/layout.html'
os.makedirs('templates', exist_ok=True)
if not os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        header {
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        nav {
            margin-bottom: 20px;
        }
        nav a {
            margin-right: 15px;
            text-decoration: none;
            color: #3498db;
            font-weight: bold;
        }
        nav a:hover {
            text-decoration: underline;
        }
        .content {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #777;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }
        pre {
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 3px;
            overflow: auto;
        }
        code {
            font-family: monospace;
            background-color: #f6f8fa;
            padding: 2px 4px;
            border-radius: 3px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        h2 {
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        img {
            max-width: 100%;
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
            text-decoration: none;
        }
    </style>
</head>
<body>
    <header>
        <h1><a href="/" style="text-decoration: none; color: inherit;">BiasBuster</a></h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/installation">Installation</a>
        <a href="/usage">Usage</a>
        <a href="/developers">Developers</a>
        <a href="/api">API</a>
        <a href="/extension.zip">Download Extension</a>
        <a href="/developer.zip">For Developers</a>
    </nav>
    <div class="content">
        {{ content | safe }}
    </div>
    <footer>
        © 2025 Amar Kumar. Released under the <a href="https://opensource.org/licenses/MIT">MIT License</a>.
    </footer>
</body>
</html>''')


# Ensure basic documentation files exist
for file in ['README.md', 'installation.md', 'usage.md', 'developers.md']:
    path = os.path.join('docs', file)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'# {file[:-3].title()}\n\nContent coming soon.')


# Entrypoint: Run the BiasBuster app
def run_bias_buster():
    parser = argparse.ArgumentParser(description='Run BiasBuster')
    parser.add_argument('--dev', action='store_true', help='Run in development mode with hot reloading')
    parser.add_argument('--port', type=int, default=int(os.environ.get("PORT", 5000)), help='Port to run on (default: 5000)')
    parser.add_argument('--host', type=str, default=os.environ.get("HOST", "0.0.0.0"), help='Host to bind (default: 0.0.0.0)')
    args = parser.parse_args()

    port = args.port
    host = args.host

    if args.dev:
        logger.info(f"Starting BiasBuster in development mode on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)
    else:
        try:
            from gunicorn.app.base import BaseApplication

            class GunicornApplication(BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            options = {
                'bind': f'{host}:{port}',
                'workers': 2,
                'timeout': 60,
                'reload': False
            }

            logger.info(f"Starting BiasBuster in production mode on http://{host}:{port}")
            GunicornApplication(app, options).run()
        except ImportError:
            logger.warning("Gunicorn not found. Starting BiasBuster with Flask's built-in server. Not recommended for production use.")
            app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_bias_buster()