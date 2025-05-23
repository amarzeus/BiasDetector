
# Standard library imports
import os
import sys
import argparse
import logging

# Third-party imports
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import markdown


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BiasBuster")


# Create Flask application
app = Flask(__name__, static_folder='docs/assets')
app.secret_key = os.environ.get("SESSION_SECRET", "bias_buster_secret_key")

# Enable CORS
CORS(app, origins="*", supports_credentials=True)


# Register backend API endpoints if available
try:
    from backend.app import health_check, analyze, rewrite, analyze_and_rewrite
    app.add_url_rule('/health', view_func=health_check, methods=['GET'])
    app.add_url_rule('/analyze', view_func=analyze, methods=['POST'])
    app.add_url_rule('/rewrite', view_func=rewrite, methods=['POST'])
    app.add_url_rule('/analyze_and_rewrite', view_func=analyze_and_rewrite, methods=['POST'])
    logger.info("Backend API routes registered successfully")
except ImportError as e:
    logger.warning(f"Failed to import backend API: {e}")


# Utility: Render Markdown documentation with optional YAML front matter for title
def render_markdown(path):
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
            return render_template('layout.html', title=title, content=html_content)
    except FileNotFoundError:
        return "Page not found", 404


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