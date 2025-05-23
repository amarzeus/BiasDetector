import os
import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.bias_detector import analyze_article, rewrite_article, compare_texts
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bias_detector_secret_key")

# Enable CORS for Chrome extension with all origins
CORS(app, origins="*", supports_credentials=True)

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
def analyze():
    """
    Analyze article content for bias
    Expected JSON payload: {"url": "article_url", "content": "article_content"}
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        content = data.get('content')
        url = data.get('url')
        
        if not content:
            return jsonify({"error": "No article content provided"}), 400
        
        # Get the OpenAI API key from the request headers (if provided)
        api_key = request.headers.get('X-OpenAI-Key')
        
        # Analyze the article for bias
        analysis_result = analyze_article(content, url, api_key)
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logging.error(f"Error analyzing article: {str(e)}")
        return jsonify({"error": f"Failed to analyze article: {str(e)}"}), 500

@app.route('/rewrite', methods=['POST'])
def rewrite():
    """
    Rewrite article to remove bias
    Expected JSON payload: {"content": "article_content", "bias_analysis": {bias_analysis_object}}
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        content = data.get('content')
        bias_analysis = data.get('bias_analysis')
        
        if not content:
            return jsonify({"error": "No article content provided"}), 400
        
        # Get the OpenAI API key from the request headers (if provided)
        api_key = request.headers.get('X-OpenAI-Key')
        
        # Rewrite the article to be more balanced
        rewritten_content = rewrite_article(content, bias_analysis, api_key)
        
        # Generate a comparison between original and rewritten
        comparison = compare_texts(content, rewritten_content)
        
        return jsonify({
            "original": content,
            "rewritten": rewritten_content,
            "comparison": comparison
        })
    
    except Exception as e:
        logging.error(f"Error rewriting article: {str(e)}")
        return jsonify({"error": f"Failed to rewrite article: {str(e)}"}), 500

@app.route('/analyze_and_rewrite', methods=['POST'])
def analyze_and_rewrite():
    """
    Analyze article for bias and rewrite it in one step
    Expected JSON payload: {"url": "article_url", "content": "article_content"}
    """
    try:
        logger.debug("Received request for /analyze_and_rewrite")
        logger.debug(f"Request headers: {request.headers}")

        data = request.json
        logger.debug(f"Request data: {data}")
        
        if not data:
            logger.error("No data provided in request")
            return jsonify({"error": "No data provided"}), 400
        
        content = data.get('content')
        url = data.get('url')
        
        logger.debug(f"URL: {url}")
        logger.debug(f"Content length: {len(content) if content else 0}")
        
        if not content:
            logger.error("No article content provided")
            return jsonify({"error": "No article content provided"}), 400
        
        # Get the OpenAI API key from the request headers (if provided)
        api_key = request.headers.get('X-OpenAI-Key')
        logger.debug(f"API key provided: {bool(api_key)}")
        
        # Analyze the article for bias
        logger.debug("Starting article analysis")
        analysis_result = analyze_article(content, url, api_key)
        logger.debug("Analysis completed successfully")
        
        # Rewrite the article to be more balanced
        logger.debug("Starting article rewrite")
        rewritten_content = rewrite_article(content, analysis_result, api_key)
        logger.debug("Rewrite completed successfully")
        
        # Generate a comparison between original and rewritten
        logger.debug("Generating text comparison")
        comparison = compare_texts(content, rewritten_content)
        logger.debug("Comparison generated successfully")
        
        # Create the response
        response = {
            "original": content,
            "rewritten": rewritten_content,
            "bias_analysis": analysis_result,
            "comparison": comparison
        }
        logger.debug("Returning successful response")
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error analyzing and rewriting article: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to analyze and rewrite article: {str(e)}"}), 500

@app.route('/generate_article', methods=['GET'])
def generate_article():
    """Generate a new biased article for demo purposes"""
    # List of biased article templates with different topics and biases
    article_templates = {
        # Left-leaning bias
        "left": """
        The heartless right-wing extremists have once again demonstrated their complete disregard for struggling families with their latest cruel tax policy. This shameful legislation, designed by corporate puppets and billionaire donors, will devastate working-class Americans while further enriching the ultra-wealthy elite. Every credible economist warns that this regressive approach will widen inequality to dangerous levels.

        The callous disregard for basic human needs in this bill exposes the moral bankruptcy of conservative ideology. It's nothing but a thinly veiled attempt to dismantle social safety nets that millions of vulnerable citizens depend on. The bill's supporters deliberately ignore overwhelming evidence about the catastrophic social consequences we've seen from similar failed trickle-down experiments.

        Progressive lawmakers heroically fought to protect ordinary citizens from this assault on their livelihoods. They understand what real American families truly need, unlike the out-of-touch conservative politicians who only care about pleasing their wealthy donors and corporate masters.

        We must stand united against this dangerous regression to failed policies of the past. History has proven time and again that shared prosperity comes from investing in people, not giving handouts to the already privileged. This bill is nothing less than class warfare against struggling Americans.
        """,
        
        # Right-leaning bias
        "right": """
        The radical left-wing Democrats have once again pushed their extreme agenda on hardworking Americans with their latest legislative disaster. This bill, crafted by out-of-touch coastal elites, will surely destroy jobs and wreck our economy. Experts who have actually studied economics, unlike these politicians, agree that these policies always fail.

        The reckless spending in this legislation will bankrupt our nation while doing nothing to help ordinary citizens. It's simply a power grab designed to control more aspects of Americans' lives through big government programs. The bill's supporters ignore the catastrophic consequences we've seen time and again from similar socialist experiments in other countries.

        Conservative lawmakers courageously fought against this terrible bill, standing up for freedom and fiscal responsibility. They understand what everyday Americans truly need, unlike the liberal politicians who only listen to special interest groups and their radical base.

        We must reject this destructive ideology before it's too late. Real Americans know that the free market, not government intervention, is the path to prosperity. This bill is nothing short of an attack on our values and way of life.
        """,
        
        # Environmental bias
        "environmental": """
        Climate change deniers have once again blocked crucial environmental protection legislation, proving they care more about corporate profits than the future of our planet. This reckless obstruction, orchestrated by fossil fuel lobbyists and their political puppets, dooms future generations to a catastrophic environmental collapse. Every legitimate scientist has warned us about the dire consequences of inaction.

        The complete dismissal of scientific consensus in this debate reveals how corrupted our political system has become by dirty energy money. It's a shameful abdication of moral responsibility to protect our shared natural resources. The opponents of climate action callously disregard the overwhelming evidence linking fossil fuel consumption to devastating extreme weather events already affecting millions.

        Environmental champions continue their brave fight against these powerful corporate interests despite being massively outspent. They represent the true will of the people, unlike the bought-and-paid-for politicians who serve only their industry donors while betraying their constituents.

        We cannot surrender to this corrupt alliance between polluters and politicians. The undeniable reality is that sustainable practices and renewable energy represent our only viable future. This obstruction of progress is nothing short of an intergenerational crime against humanity.
        """,
        
        # Technology bias
        "technology": """
        Big Tech monopolies are systematically destroying small businesses and recklessly invading our privacy with their predatory practices. These Silicon Valley giants, run by arrogant billionaires with god complexes, have accumulated unprecedented power over our economy and democracy. Independent experts universally condemn their anti-competitive tactics that crush innovation.

        The blatant disregard for user privacy and data security demonstrates the moral bankruptcy of these digital overlords. They've created addictive platforms deliberately designed to harvest our personal information and manipulate our behavior. The defenders of these companies conveniently ignore the mounting evidence linking social media to serious mental health issues, especially among vulnerable youth.

        A few brave lawmakers continue speaking truth to power despite massive lobbying campaigns from the tech industry. They understand what ordinary citizens truly need, unlike the tech-captured regulators who rotate between government positions and lucrative industry jobs.

        We must break up these dangerous monopolies before they completely undermine our democratic institutions. History has shown that unchecked corporate power inevitably leads to exploitation and abuse. This threat to our fundamental freedoms cannot be overstated.
        """,
        
        # Healthcare bias
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

@app.route('/demo', methods=['GET'])
def demo():
    """Interactive demo page for the BiasDetector API"""
    return """
    <html>
        <head>
            <title>BiasDetector Demo</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                .card {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .tabs {
                    display: flex;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #ddd;
                }
                .tab {
                    padding: 10px 15px;
                    cursor: pointer;
                    margin-right: 5px;
                    border-radius: 4px 4px 0 0;
                }
                .tab.active {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
                }
                .btn {
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    border: none;
                    cursor: pointer;
                }
                .btn:hover {
                    background-color: #2980b9;
                }
                .form-group {
                    margin-bottom: 15px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                select, textarea {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                textarea {
                    min-height: 200px;
                }
                .loader {
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #3498db;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                    display: none;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .bias-meter {
                    width: 100%;
                    height: 30px;
                    background-color: #eee;
                    border-radius: 15px;
                    overflow: hidden;
                    position: relative;
                    margin: 10px 0;
                }
                .bias-fill {
                    height: 100%;
                    background: linear-gradient(to right, #27ae60, #f39c12, #e74c3c);
                    width: 0%;
                    transition: width 1s;
                }
                .bias-marker {
                    position: absolute;
                    top: 0;
                    height: 100%;
                    width: 3px;
                    background-color: black;
                }
                .bias-label {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 5px;
                }
                .bias-instance {
                    padding: 10px;
                    margin: 5px 0;
                    background-color: #f8f9fa;
                    border-left: 4px solid #e74c3c;
                    border-radius: 3px;
                }
                .severity-high {
                    border-color: #e74c3c;
                }
                .severity-medium {
                    border-color: #f39c12;
                }
                .severity-low {
                    border-color: #27ae60;
                }
                .diff-view {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 3px;
                    white-space: pre-wrap;
                    font-family: monospace;
                }
                .diff-add {
                    background-color: #d4edda;
                    color: #155724;
                }
                .diff-remove {
                    background-color: #f8d7da;
                    color: #721c24;
                    text-decoration: line-through;
                }
                .analysis-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .analysis-score {
                    font-size: 2em;
                    font-weight: bold;
                    color: #e74c3c;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>BiasDetector Interactive Demo</h1>
                <p>Try out the BiasDetector API with a sample biased article or enter your own text for analysis.</p>
            </div>
            
            <div class="card">
                <h2>Select Article Type</h2>
                <div class="form-group">
                    <label for="bias-type">Bias Type:</label>
                    <select id="bias-type">
                        <option value="left">Left-Leaning Political Bias</option>
                        <option value="right">Right-Leaning Political Bias</option>
                        <option value="environmental">Environmental Bias</option>
                        <option value="technology">Technology Bias</option>
                        <option value="healthcare">Healthcare Bias</option>
                    </select>
                </div>
                <button id="load-article" class="btn">Load Sample Article</button>
                <span> or </span>
                <button id="clear-article" class="btn">Enter Your Own</button>
            </div>
            
            <div class="card">
                <h2>Article Text</h2>
                <div class="form-group">
                    <textarea id="article-text" placeholder="Enter or paste article text here..."></textarea>
                </div>
                <button id="analyze-btn" class="btn">Analyze & Rewrite</button>
                <div id="loader" class="loader"></div>
            </div>
            
            <div id="results" style="display: none;">
                <div class="card">
                    <div class="tabs">
                        <div class="tab active" data-tab="analysis">Bias Analysis</div>
                        <div class="tab" data-tab="rewritten">Rewritten</div>
                        <div class="tab" data-tab="comparison">Comparison</div>
                    </div>
                    
                    <div id="analysis-tab" class="tab-content active">
                        <div class="analysis-header">
                            <h2>Bias Analysis</h2>
                            <div class="analysis-score" id="bias-score">0</div>
                        </div>
                        
                        <h3>Overall Bias Level</h3>
                        <div class="bias-meter">
                            <div class="bias-fill" id="bias-meter-fill"></div>
                        </div>
                        <div class="bias-label">
                            <span>Neutral</span>
                            <span>Moderate</span>
                            <span>Strong</span>
                        </div>
                        
                        <h3>Bias Categories</h3>
                        <div id="bias-categories"></div>
                        
                        <h3>Bias Instances</h3>
                        <div id="bias-instances"></div>
                    </div>
                    
                    <div id="rewritten-tab" class="tab-content">
                        <h2>Balanced Version</h2>
                        <p>This is a rewritten version of the article with reduced bias:</p>
                        <div id="rewritten-content"></div>
                    </div>
                    
                    <div id="comparison-tab" class="tab-content">
                        <h2>Side-by-Side Comparison</h2>
                        <p>Changes shown with additions in green and removals in red:</p>
                        <div id="comparison-content" class="diff-view"></div>
                    </div>
                </div>
            </div>
            
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Elements
                    const biasTypeSelect = document.getElementById('bias-type');
                    const loadArticleBtn = document.getElementById('load-article');
                    const clearArticleBtn = document.getElementById('clear-article');
                    const articleTextArea = document.getElementById('article-text');
                    const analyzeBtn = document.getElementById('analyze-btn');
                    const loader = document.getElementById('loader');
                    const resultsDiv = document.getElementById('results');
                    const tabs = document.querySelectorAll('.tab');
                    const tabContents = document.querySelectorAll('.tab-content');
                    const biasScore = document.getElementById('bias-score');
                    const biasMeterFill = document.getElementById('bias-meter-fill');
                    const biasCategories = document.getElementById('bias-categories');
                    const biasInstances = document.getElementById('bias-instances');
                    const rewrittenContent = document.getElementById('rewritten-content');
                    const comparisonContent = document.getElementById('comparison-content');
                    
                    // Load sample article
                    loadArticleBtn.addEventListener('click', function() {
                        const biasType = biasTypeSelect.value;
                        loader.style.display = 'block';
                        
                        fetch(`/generate_article?bias_type=${biasType}`)
                            .then(response => response.json())
                            .then(data => {
                                articleTextArea.value = data.content;
                                loader.style.display = 'none';
                            })
                            .catch(error => {
                                console.error('Error loading article:', error);
                                loader.style.display = 'none';
                                alert('Error loading sample article. Please try again.');
                            });
                    });
                    
                    // Clear article
                    clearArticleBtn.addEventListener('click', function() {
                        articleTextArea.value = '';
                        articleTextArea.focus();
                    });
                    
                    // Analyze article
                    analyzeBtn.addEventListener('click', function() {
                        const articleText = articleTextArea.value.trim();
                        
                        if (!articleText) {
                            alert('Please enter or load an article first.');
                            return;
                        }
                        
                        loader.style.display = 'block';
                        resultsDiv.style.display = 'none';
                        
                        fetch('/analyze_and_rewrite', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                content: articleText,
                                url: window.location.href
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            
                            displayResults(data);
                            loader.style.display = 'none';
                            resultsDiv.style.display = 'block';
                        })
                        .catch(error => {
                            console.error('Error analyzing article:', error);
                            loader.style.display = 'none';
                            alert('Error analyzing article: ' + error.message);
                        });
                    });
                    
                    // Tab switching
                    tabs.forEach(tab => {
                        tab.addEventListener('click', () => {
                            const tabId = tab.getAttribute('data-tab');
                            
                            // Update active tab
                            tabs.forEach(t => t.classList.remove('active'));
                            tab.classList.add('active');
                            
                            // Show active content
                            tabContents.forEach(content => {
                                content.classList.remove('active');
                            });
                            document.getElementById(tabId + '-tab').classList.add('active');
                        });
                    });
                    
                    // Display analysis results
                    function displayResults(data) {
                        const analysis = data.bias_analysis;
                        
                        // Display bias score
                        const score = analysis.bias_score;
                        biasScore.textContent = score;
                        biasMeterFill.style.width = `${score}%`;
                        
                        // Display bias categories
                        biasCategories.innerHTML = '';
                        for (const [category, value] of Object.entries(analysis.bias_categories)) {
                            const percent = Math.round(value * 100);
                            biasCategories.innerHTML += `
                                <div>
                                    <strong>${formatCategoryName(category)}:</strong> ${percent}%
                                    <div class="bias-meter">
                                        <div class="bias-fill" style="width: ${percent}%"></div>
                                    </div>
                                </div>
                            `;
                        }
                        
                        // Display bias instances
                        biasInstances.innerHTML = '';
                        if (analysis.bias_instances.length === 0) {
                            biasInstances.innerHTML = '<p>No specific bias instances detected.</p>';
                        } else {
                            analysis.bias_instances.forEach(instance => {
                                const severityClass = getSeverityClass(instance.severity);
                                biasInstances.innerHTML += `
                                    <div class="bias-instance ${severityClass}">
                                        <strong>${formatCategoryName(instance.category)}:</strong>
                                        <p>"${instance.text}"</p>
                                        <small>Severity: ${Math.round(instance.severity * 100)}%</small>
                                    </div>
                                `;
                            });
                        }
                        
                        // Display rewritten content
                        rewrittenContent.innerHTML = `<p>${data.rewritten.replace(/\\n/g, '<br>')}</p>`;
                        
                        // Display comparison
                        comparisonContent.innerHTML = '';
                        data.comparison.diff.forEach(part => {
                            let className = '';
                            if (part.added) className = 'diff-add';
                            if (part.removed) className = 'diff-remove';
                            
                            comparisonContent.innerHTML += `<span class="${className}">${part.value}</span>`;
                        });
                    }
                    
                    // Helper functions
                    function formatCategoryName(name) {
                        return name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
                    }
                    
                    function getSeverityClass(severity) {
                        if (severity > 0.7) return 'severity-high';
                        if (severity > 0.4) return 'severity-medium';
                        return 'severity-low';
                    }
                    
                    // Load a sample article on page load
                    loadArticleBtn.click();
                });
            </script>
        </body>
    </html>
    """

@app.route('/api/v2/analyze', methods=['POST'])
def analyze_v2():
    """
    Enhanced analyze endpoint with advanced bias detection features
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({
                'error': 'No text provided',
                'status': 'error'
            }), 400
            
        text = data['text']
        url = data.get('url')  # Optional URL for source credibility
        
        # Perform enhanced analysis
        analysis_results = analyze_article(text, url)
        
        return jsonify({
            'status': 'success',
            'data': analysis_results
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_v2: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/v2/comparative-analysis', methods=['POST'])
def comparative_analysis():
    """
    Compare multiple articles for bias analysis
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('articles'):
            return jsonify({
                'error': 'No articles provided',
                'status': 'error'
            }), 400
            
        articles = data['articles']
        if not isinstance(articles, list) or len(articles) < 2:
            return jsonify({
                'error': 'At least two articles are required for comparison',
                'status': 'error'
            }), 400
            
        # Analyze each article
        results = []
        for article in articles:
            text = article.get('text', '')
            url = article.get('url')
            analysis = analyze_article(text, url)
            results.append(analysis)
            
        # Compare results
        comparison = {
            'sentiment_variance': calculate_variance([r['metrics']['sentiment'] for r in results]),
            'bias_similarity': calculate_bias_similarity([r['categories'] for r in results]),
            'context_overlap': analyze_context_overlap([r['context'] for r in results]),
            'individual_results': results
        }
        
        return jsonify({
            'status': 'success',
            'data': comparison
        })
        
    except Exception as e:
        logger.error(f"Error in comparative_analysis: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/v2/source-credibility', methods=['GET'])
def check_source_credibility():
    """
    Check the credibility of a news source
    """
    try:
        url = request.args.get('url')
        
        if not url:
            return jsonify({
                'error': 'No URL provided',
                'status': 'error'
            }), 400
              from backend.bias_detector import SourceCredibility
        source_checker = SourceCredibility()
        credibility_score = source_checker.get_source_credibility(url)
        
        return jsonify({
            'status': 'success',
            'data': {
                'url': url,
                'credibility_score': credibility_score
            }
        })
        
    except Exception as e:
        logger.error(f"Error in check_source_credibility: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def calculate_variance(values):
    """Calculate the statistical variance of a list of values"""
    if not values:
        return 0
    mean = sum(values) / len(values)
    squared_diff_sum = sum((x - mean) ** 2 for x in values)
    return squared_diff_sum / len(values)

def calculate_bias_similarity(category_lists):
    """Calculate similarity between bias category distributions"""
    # Convert category lists to vectors and calculate cosine similarity
    all_categories = set()
    for cats in category_lists:
        all_categories.update(cats.keys())
        
    vectors = []
    for cats in category_lists:
        vector = [cats.get(cat, 0) for cat in all_categories]
        vectors.append(vector)
        
    # Calculate average pairwise similarity
    similarities = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            similarity = cosine_similarity(vectors[i], vectors[j])
            similarities.append(similarity)
            
    return sum(similarities) / len(similarities) if similarities else 0

def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    return dot_product / (norm1 * norm2) if norm1 * norm2 != 0 else 0

def analyze_context_overlap(context_lists):
    """Analyze how much context overlaps between articles"""
    # Extract all related events and missing context
    all_events = set()
    all_missing = set();
    
    for ctx in context_lists:
        all_events.update(ctx['related_events']);
        all_missing.update(ctx['missing_context']);
    
    # Calculate overlap ratios    events_sum = sum(len(ctx['related_events']) for ctx in context_lists)
    missing_sum = sum(len(ctx['missing_context']) for ctx in context_lists)
    
    event_overlap = len(all_events) / (events_sum if events_sum > 0 else 1)
    missing_overlap = len(all_missing) / (missing_sum if missing_sum > 0 else 1)
    
    return {
        'event_overlap': event_overlap,
        'missing_context_overlap': missing_overlap
    }
