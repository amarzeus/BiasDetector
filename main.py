import os
from flask import Flask, render_template, send_from_directory, redirect, url_for, request, jsonify
from flask_cors import CORS
import markdown
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__, static_folder='docs/assets')
app.secret_key = os.environ.get("SESSION_SECRET", "bias_detector_secret_key")

# Enable CORS 
CORS(app, origins="*", supports_credentials=True)

# Serve API endpoints from backend
try:
    from backend.app import health_check, analyze, rewrite, analyze_and_rewrite
    
    # Register backend API routes
    app.route('/health', methods=['GET'])(health_check)
    app.route('/analyze', methods=['POST'])(analyze)
    app.route('/rewrite', methods=['POST'])(rewrite)
    app.route('/analyze_and_rewrite', methods=['POST'])(analyze_and_rewrite)
    
    logger.info("Backend API routes registered successfully")
except ImportError as e:
    logger.warning(f"Failed to import backend API: {e}")

# Documentation Pages
def render_markdown(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            # Extract YAML front matter if present
            title = "BiasDetector"
            if content.startswith('---'):
                end = content.find('---', 3)
                if end != -1:
                    front_matter = content[3:end].strip()
                    for line in front_matter.split('\n'):
                        if line.startswith('title:'):
                            title = line[6:].strip()
                    content = content[end+3:].strip()
            
            # Convert Markdown to HTML
            html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
            return render_template('layout.html', title=title, content=html_content)
    except FileNotFoundError:
        return "Page not found", 404

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

# Create a simple template for rendering markdown
os.makedirs('templates', exist_ok=True)
with open('templates/layout.html', 'w') as f:
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
        <h1><a href="/" style="text-decoration: none; color: inherit;">BiasDetector</a></h1>
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
        © 2023 Amar Kumar. Released under the <a href="https://opensource.org/licenses/MIT">MIT License</a>.
    </footer>
</body>
</html>''')

# Add empty .md files if they don't exist
for file in ['README.md', 'installation.md', 'usage.md', 'developers.md']:
    path = os.path.join('docs', file)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(f'# {file[:-3].title()}\n\nContent coming soon.')

if __name__ == "__main__":
    # Determine port based on environment variables that Replit might set
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Log the configuration for debugging
    logger.info(f"Starting server on {host}:{port}")
    
    # Run the Flask application
    app.run(host=host, port=port, debug=True)