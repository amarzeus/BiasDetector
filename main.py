# Standard library imports
import os
import sys
import argparse
import logging
import time
import json
import secrets
from functools import wraps
from datetime import datetime
from pathlib import Path

# Third-party imports
import nltk
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
from flask_cors import CORS
import markdown
from werkzeug.contrib.cache import SimpleCache
from prometheus_client import Counter, Histogram, generate_latest


# Configure metrics
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("BiasDetector")

# Initialize cache with larger default timeout for API responses
cache = SimpleCache(default_timeout=300)

class Config:
    def __init__(self):
        self.config_path = Path("config.json")
        self.settings = {
            "api": {
                "rate_limit": 100,
                "cache_timeout": 300
            }
        }
        self.load_config()
        
    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self.settings.update(json.load(f))
            except json.JSONDecodeError:
                logger.error("Invalid config.json file")
        else:
            self.save_config()
            
    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=4)
            
config = Config()

# Enhanced performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            response = f(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else 200
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=status).inc()
            REQUEST_LATENCY.labels(endpoint=request.endpoint).observe(time.time() - start_time)
            return response
        except Exception as e:
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=500).inc()
            REQUEST_LATENCY.labels(endpoint=request.endpoint).observe(time.time() - start_time)
            raise
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
            # Check rate limit
            if get_rate_limit() <= 0:
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            # Update rate limit counter
            update_rate_limit()
            
            # Execute the function
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


# Initialize NLTK
nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)  # type: ignore

def ensure_nltk_data() -> None:
    """Ensure NLTK data is downloaded, with fallback for offline mode"""
    required_packages = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    
    for package in required_packages:
        try:
            nltk.data.find(f'tokenizers/{package}' if package == 'punkt' else package)  # type: ignore
        except LookupError:
            try:
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)  # type: ignore
            except Exception as e:
                logger.error(f"Failed to download NLTK package {package}: {e}")
                if package == 'punkt':
                    raise RuntimeError("Critical NLTK data 'punkt' could not be downloaded. Cannot continue.")

# Entrypoint: Run the BiasBuster app
def run_bias_buster() -> None:
    """Run the BiasDetector application with proper error handling"""
    try:
        parser = argparse.ArgumentParser(description='Run BiasBuster')
        parser.add_argument('--dev', action='store_true', help='Run in development mode with hot reloading')
        parser.add_argument('--port', type=int, default=int(os.environ.get("PORT", "5000")), help='Port to run on (default: 5000)')
        parser.add_argument('--host', type=str, default=os.environ.get("HOST", "0.0.0.0"), help='Host to bind (default: 0.0.0.0)')
        
        args = parser.parse_args()
        port: int = args.port
        host: str = args.host
        
        # Validate port number
        if port < 1 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")
            
        # Initialize required NLTK data
        ensure_nltk_data()
        
        if args.dev:
            logger.info(f"Starting BiasBuster in development mode on http://{host}:{port}")
            app.run(host=host, port=port, debug=True)
        else:
            try:
                from gunicorn.app.base import BaseApplication  # type: ignore

                class GunicornApplication(BaseApplication):  # type: ignore
                    def __init__(self, app, options=None):
                        self.application = app
                        self.options = options or {}
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

                logger.info(f"Starting BiasDetector in production mode on http://{host}:{port}")
                GunicornApplication(app, options).run()
            except ImportError:
                logger.warning("Gunicorn not found. Starting BiasDetector with Flask's built-in server. Not recommended for production use.")
                app.run(host=host, port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start BiasBuster: {str(e)}")
        raise

@app.route('/generate_article', methods=['GET'])
@monitor_performance
@handle_errors
def generate_article():
    """Generate a new biased article for demo purposes"""
    # List of biased article templates with different topics and biases
    article_templates = {
        "left": """
        The heartless right-wing extremists have once again demonstrated their complete disregard for struggling families with their latest cruel tax policy. This shameful legislation, designed by corporate puppets and billionaire donors, will devastate working-class Americans while further enriching the ultra-wealthy elite. Every credible economist warns that this regressive approach will widen inequality to dangerous levels.

        The callous disregard for basic human needs in this bill exposes the moral bankruptcy of conservative ideology. It's nothing but a thinly veiled attempt to dismantle social safety nets that millions of vulnerable citizens depend on. The bill's supporters deliberately ignore overwhelming evidence about the catastrophic social consequences we've seen from similar failed trickle-down experiments.

        Progressive lawmakers heroically fought to protect ordinary citizens from this assault on their livelihoods. They understand what real American families truly need, unlike the out-of-touch conservative politicians who only care about pleasing their wealthy donors and corporate masters.

        We must stand united against this dangerous regression to failed policies of the past. History has proven time and again that shared prosperity comes from investing in people, not giving handouts to the already privileged. This bill is nothing less than class warfare against struggling Americans.
        """,
        "right": """
        The radical left-wing Democrats have once again pushed their extreme agenda on hardworking Americans with their latest legislative disaster. This bill, crafted by out-of-touch coastal elites, will surely destroy jobs and wreck our economy. Experts who have actually studied economics, unlike these politicians, agree that these policies always fail.

        The reckless spending in this legislation will bankrupt our nation while doing nothing to help ordinary citizens. It's simply a power grab designed to control more aspects of Americans' lives through big government programs. The bill's supporters ignore the catastrophic consequences we've seen time and again from similar socialist experiments in other countries.

        Conservative lawmakers courageously fought against this terrible bill, standing up for freedom and fiscal responsibility. They understand what everyday Americans truly need, unlike the liberal politicians who only listen to special interest groups and their radical base.

        We must reject this destructive ideology before it's too late. Real Americans know that the free market, not government intervention, is the path to prosperity. This bill is nothing short of an attack on our values and way of life.
        """,
        "environmental": """
        Climate change deniers have once again blocked crucial environmental protection legislation, proving they care more about corporate profits than the future of our planet. This reckless obstruction, orchestrated by fossil fuel lobbyists and their political puppets, dooms future generations to a catastrophic environmental collapse. Every legitimate scientist has warned us about the dire consequences of inaction.

        The complete dismissal of scientific consensus in this debate reveals how corrupted our political system has become by dirty energy money. It's a shameful abdication of moral responsibility to protect our shared natural resources. The opponents of climate action callously disregard the overwhelming evidence linking fossil fuel consumption to devastating extreme weather events already affecting millions.

        Environmental champions continue their brave fight against these powerful corporate interests despite being massively outspent. They represent the true will of the people, unlike the bought-and-paid-for politicians who serve only their industry donors while betraying their constituents.

        We cannot surrender to this corrupt alliance between polluters and politicians. The undeniable reality is that sustainable practices and renewable energy represent our only viable future. This obstruction of progress is nothing short of an intergenerational crime against humanity.
        """,
        "technology": """
        Big Tech monopolies are systematically destroying small businesses and recklessly invading our privacy with their predatory practices. These Silicon Valley giants, run by arrogant billionaires with god complexes, have accumulated unprecedented power over our economy and democracy. Independent experts universally condemn their anti-competitive tactics that crush innovation.

        The blatant disregard for user privacy and data security demonstrates the moral bankruptcy of these digital overlords. They've created addictive platforms deliberately designed to harvest our personal information and manipulate our behavior. The defenders of these companies conveniently ignore the mounting evidence linking social media to serious mental health issues, especially among vulnerable youth.

        A few brave lawmakers continue speaking truth to power despite massive lobbying campaigns from the tech industry. They understand what ordinary citizens truly need, unlike the tech-captured regulators who rotate between government positions and lucrative industry jobs.

        We must break up these dangerous monopolies before they completely undermine our democratic institutions. History has shown that unchecked corporate power inevitably leads to exploitation and abuse. This threat to our fundamental freedoms cannot be overstated.
        """,
        "healthcare": """
        The heartless opponents of universal healthcare have once again blocked vital reforms that would save countless lives, proving they value corporate profits over human suffering. This cruel obstruction, orchestrated by pharmaceutical and insurance lobbyists, condemns millions of Americans to bankruptcy and preventable deaths. Every reputable medical organization supports these necessary changes.

        The callous disregard for public health in this debate exposes the moral bankruptcy of those who defend our broken system. It's nothing but a cynical attempt to preserve the obscene profits of healthcare corporations at the expense of ordinary citizens. The reform opponents deliberately ignore overwhelming evidence from dozens of countries with successful universal healthcare models.

        Progressive advocates continue their heroic fight despite being massively outspent by industry propaganda. They represent the true will of the people, unlike the corrupt politicians who serve only their donors while betraying their constituents' healthcare needs.

        We cannot surrender to this sinister alliance between profiteers and politicians. The undeniable reality is that universal healthcare is not only morally necessary but economically superior to our wasteful private system. This obstruction of reform is costing American lives every single day.
        """
    }
    
    # Select a template based on bias type parameter or default to left
    bias_type = request.args.get('bias_type', 'left')
    article = article_templates.get(bias_type, article_templates['left'])
    
    return jsonify({
        "content": article.strip(),
        "bias_type": bias_type
    })

@app.route('/demo')
@monitor_performance
@handle_errors
def demo():
    """Interactive demo page for the BiasDetector API"""
    return render_template('demo.html')