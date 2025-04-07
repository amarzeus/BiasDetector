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
        The heartless opponents of universal healthcare have once again blocked vital reforms that would save countless lives, proving they value corporate profits over human suffering. This cruel obstruction, orchestrated by pharmaceutical and insurance lobbyists, condemns millions of Americans to bankruptcy and preventable deaths. Every reputable medical organization has endorsed a universal system as the only humane solution.

        The complete dismissal of medical expertise in this debate exposes the moral failure of those who oppose reform. It's nothing but a desperate attempt to preserve an exploitative system that generates massive profits for shareholders. The defenders of the status quo callously ignore the overwhelming evidence that our current healthcare model is both inefficient and deadly.

        Healthcare advocates heroically continue fighting for the right to healthcare despite massive industry opposition. They understand what patients truly need, unlike the politicians who receive millions in campaign contributions from the very companies profiting from human suffering.

        We cannot allow this injustice to continue. The undeniable truth is that every other developed nation provides universal healthcare to its citizens at a fraction of our costs. This obstruction of progress is nothing short of a human rights violation.
        """
    }
    
    # Get the article type from request parameters
    article_type = request.args.get('type', 'random')
    
    # If random or invalid type, pick a random article
    import random
    if article_type == 'random' or article_type not in article_templates:
        article_type = random.choice(list(article_templates.keys()))
    
    selected_article = article_templates[article_type]
    
    return jsonify({
        "article": selected_article.strip(),
        "type": article_type
    })

@app.route('/demo', methods=['GET'])
def demo():
    """Interactive demo page for BiasDetector"""
    
    # Sample biased article text
    sample_article = """
    The radical left-wing Democrats have once again pushed their extreme agenda on hardworking Americans with their latest legislative disaster. This bill, crafted by out-of-touch coastal elites, will surely destroy jobs and wreck our economy. Experts who have actually studied economics, unlike these politicians, agree that these policies always fail.

    The reckless spending in this legislation will bankrupt our nation while doing nothing to help ordinary citizens. It's simply a power grab designed to control more aspects of Americans' lives through big government programs. The bill's supporters ignore the catastrophic consequences we've seen time and again from similar socialist experiments in other countries.

    Conservative lawmakers courageously fought against this terrible bill, standing up for freedom and fiscal responsibility. They understand what everyday Americans truly need, unlike the liberal politicians who only listen to special interest groups and their radical base.

    We must reject this destructive ideology before it's too late. Real Americans know that the free market, not government intervention, is the path to prosperity. This bill is nothing short of an attack on our values and way of life.
    """
    
    # Return the demo page with the sample article
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BiasDetector Demo</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
                background-color: #f5f5f5;
                color: #333;
            }
            .card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .btn-primary {
                background-color: #3498db;
                border-color: #3498db;
            }
            .btn-primary:hover {
                background-color: #2980b9;
                border-color: #2980b9;
            }
            .navbar {
                background-color: #2c3e50;
                margin-bottom: 20px;
            }
            .navbar-brand {
                font-weight: bold;
                color: white !important;
            }
            .bias-score {
                font-size: 2rem;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 15px;
                color: white;
            }
            .bg-low { background-color: #27ae60; }
            .bg-medium { background-color: #f39c12; }
            .bg-high { background-color: #e74c3c; }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            .tab-content {
                padding: 15px 0;
            }
            .result-section {
                display: none;
            }
            .diff-removed {
                background-color: rgba(231, 76, 60, 0.2);
                text-decoration: line-through;
                padding: 2px 0;
            }
            .diff-added {
                background-color: rgba(39, 174, 96, 0.2);
                padding: 2px 0;
            }
            #apiKeySection {
                margin-bottom: 20px;
            }
            .bias-instance {
                border-left: 4px solid #f39c12;
                padding: 10px 15px;
                margin-bottom: 10px;
                background-color: rgba(243, 156, 18, 0.1);
            }
            .instance-text {
                font-weight: bold;
            }
            .instance-severity {
                float: right;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                color: white;
            }
            .severity-low { background-color: #27ae60; }
            .severity-medium { background-color: #f39c12; }
            .severity-high { background-color: #e74c3c; }
            .context-item {
                border-left: 4px solid #3498db;
                padding: 10px 15px;
                margin-bottom: 10px;
                background-color: rgba(52, 152, 219, 0.1);
            }
            .toggle-view-btn {
                cursor: pointer;
                color: #3498db;
            }
            .accordion-body {
                border-top: 1px solid rgba(0,0,0,0.1);
                padding-top: 10px;
            }
            /* Override bootstrap dark theme for demo */
            [data-bs-theme=dark] {
                --bs-body-color: #333;
                --bs-body-bg: #f5f5f5;
            }
            .navbar-dark {
                background-color: #2c3e50 !important;
            }
            .card {
                --bs-card-bg: white;
                --bs-card-color: #333;
            }
            h1, h2, h3, h4, h5, h6, p {
                color: #333 !important;
            }
            .text-muted {
                color: #777 !important;
            }
            .nav-tabs .nav-link {
                color: #555 !important;
            }
            .nav-tabs .nav-link.active {
                color: #3498db !important;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">
                    <i class="bi bi-exclamation-circle me-2"></i>
                    BiasDetector
                </a>
                <span class="navbar-text">
                    v1.0.0
                </span>
            </div>
        </nav>

        <div class="container">
            <div class="card">
                <h2>BiasDetector Demo</h2>
                <p>This demo shows how the BiasDetector analyzes and rewrites biased news articles. You can provide your OpenAI API key for full functionality or use the demo mode.</p>
                
                <div id="apiKeySection">
                    <div class="form-group mb-3">
                        <label for="apiKey">OpenAI API Key (Optional)</label>
                        <div class="input-group">
                            <input type="password" class="form-control" id="apiKey" placeholder="sk-...">
                            <button class="btn btn-outline-secondary" type="button" id="toggleApiKey">
                                <i class="bi bi-eye"></i>
                            </button>
                        </div>
                        <small class="form-text text-muted">Your API key stays in your browser and is sent directly to OpenAI</small>
                    </div>
                </div>
                
                <div class="form-group mb-3">
                    <label for="articleType">Article Type</label>
                    <select class="form-select" id="articleType">
                        <option value="random">Random</option>
                        <option value="left">Left-Leaning Political</option>
                        <option value="right">Right-Leaning Political</option>
                        <option value="environmental">Environmental</option>
                        <option value="technology">Technology</option>
                        <option value="healthcare">Healthcare</option>
                    </select>
                    <small class="form-text text-muted">Select the type of biased article you want to generate</small>
                </div>
                
                <div class="form-group mb-3">
                    <label for="articleText">Article Text</label>
                    <textarea class="form-control" id="articleText" rows="10">""" + sample_article.strip() + """</textarea>
                </div>
                
                <div class="d-flex gap-2">
                    <button id="generateBtn" class="btn btn-secondary">
                        <i class="bi bi-arrow-repeat me-1"></i> Generate New Article
                    </button>
                    <button id="analyzeBtn" class="btn btn-primary">
                        <i class="bi bi-search me-1"></i> Analyze Article
                    </button>
                </div>
            </div>
            
            <div id="loadingSection" class="loading card">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Analyzing article for bias...</p>
            </div>
            
            <div id="resultSection" class="result-section">
                <div class="card mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h3 class="mb-0">Analysis Results</h3>
                        <div id="biasScoreBadge" class="bias-score bg-medium">75</div>
                    </div>
                    
                    <p id="biasAssessment" class="text-center">This article shows significant bias. It presents a one-sided viewpoint with emotional language and missing context.</p>
                    
                    <ul class="nav nav-tabs" id="resultTabs" role="tablist" style="border-bottom: 2px solid #dee2e6;">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="analysis-tab" data-bs-toggle="tab" data-bs-target="#analysis" type="button" role="tab" style="color: #333; font-weight: bold; border: 1px solid #dee2e6; border-bottom: none; padding: 10px 15px;">Analysis</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="rewritten-tab" data-bs-toggle="tab" data-bs-target="#rewritten" type="button" role="tab" style="color: #333; border: 1px solid #dee2e6; border-bottom: none; padding: 10px 15px;">Rewritten</button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="compare-tab" data-bs-toggle="tab" data-bs-target="#compare" type="button" role="tab" style="color: #333; border: 1px solid #dee2e6; border-bottom: none; padding: 10px 15px;">Compare</button>
                        </li>
                    </ul>
                    
                    <div class="tab-content" id="resultTabsContent">
                        <!-- Analysis Tab -->
                        <div class="tab-pane fade show active" id="analysis" role="tabpanel">
                            <div class="mb-4">
                                <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;">Bias Categories</h4>
                                <div id="biasCategories" class="row"></div>
                            </div>
                            
                            <div class="mb-4">
                                <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;">Bias Instances</h4>
                                <div id="biasInstances"></div>
                            </div>
                            
                            <div>
                                <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;">Missing Context</h4>
                                <div id="missingContext"></div>
                            </div>
                        </div>
                        
                        <!-- Rewritten Tab -->
                        <div class="tab-pane fade" id="rewritten" role="tabpanel">
                            <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;">Balanced Article</h4>
                            <p class="text-muted">The article has been rewritten to present a more balanced viewpoint.</p>
                            <div id="rewrittenContent" class="mt-3"></div>
                        </div>
                        
                        <!-- Compare Tab -->
                        <div class="tab-pane fade" id="compare" role="tabpanel">
                            <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;">Side-by-Side Comparison</h4>
                            <p class="text-muted">See the differences between the original and rewritten article.</p>
                            
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <h5 style="color: #333; font-weight: bold; margin-bottom: 15px;">Original</h5>
                                    <div id="originalContent"></div>
                                </div>
                                <div class="col-md-6">
                                    <h5 style="color: #333; font-weight: bold; margin-bottom: 15px;">Rewritten</h5>
                                    <div id="compareRewrittenContent"></div>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <h4 style="color: #333; margin-bottom: 15px; font-weight: bold;" class="mt-4">Inline Differences</h4>
                            <p class="text-muted">
                                <span class="diff-removed">Removed text</span>
                                <span class="diff-added">Added text</span>
                            </p>
                            <div id="diffContent" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const apiKeyInput = document.getElementById('apiKey');
                const toggleApiKeyBtn = document.getElementById('toggleApiKey');
                const articleTextInput = document.getElementById('articleText');
                const generateBtn = document.getElementById('generateBtn');
                const analyzeBtn = document.getElementById('analyzeBtn');
                const loadingSection = document.getElementById('loadingSection');
                const resultSection = document.getElementById('resultSection');
                
                // Toggle API key visibility
                toggleApiKeyBtn.addEventListener('click', () => {
                    if (apiKeyInput.type === 'password') {
                        apiKeyInput.type = 'text';
                        toggleApiKeyBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
                    } else {
                        apiKeyInput.type = 'password';
                        toggleApiKeyBtn.innerHTML = '<i class="bi bi-eye"></i>';
                    }
                });
                
                // Generate new article button click
                generateBtn.addEventListener('click', () => {
                    // Show a loading spinner inside the button
                    const originalBtnHtml = generateBtn.innerHTML;
                    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
                    generateBtn.disabled = true;
                    
                    // Get the selected article type
                    const articleType = document.getElementById('articleType').value;
                    
                    // Fetch a new article with the selected type
                    fetch(`/generate_article?type=${articleType}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            // Put the new article in the textarea
                            articleTextInput.value = data.article;
                            // Reset the button
                            generateBtn.innerHTML = originalBtnHtml;
                            generateBtn.disabled = false;
                            // Hide the results section if it's visible
                            resultSection.style.display = 'none';
                            // Update the article type dropdown to match the generated article
                            document.getElementById('articleType').value = data.type;
                        })
                        .catch(error => {
                            alert(`Error generating article: ${error.message}`);
                            generateBtn.innerHTML = originalBtnHtml;
                            generateBtn.disabled = false;
                        });
                });
                
                // Analyze article button click
                analyzeBtn.addEventListener('click', () => {
                    const articleText = articleTextInput.value.trim();
                    if (!articleText) {
                        alert('Please enter article text to analyze');
                        return;
                    }
                    
                    // Show loading section
                    loadingSection.style.display = 'block';
                    resultSection.style.display = 'none';
                    
                    // Prepare the request
                    const apiKey = apiKeyInput.value.trim();
                    const headers = {
                        'Content-Type': 'application/json'
                    };
                    
                    if (apiKey) {
                        headers['X-OpenAI-Key'] = apiKey;
                    }
                    
                    // Send the analysis request
                    fetch('/analyze_and_rewrite', {
                        method: 'POST',
                        headers: headers,
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
                        
                        // Hide loading and show results
                        loadingSection.style.display = 'none';
                        resultSection.style.display = 'block';
                        
                        // Display the results
                        displayAnalysisResults(data);
                    })
                    .catch(error => {
                        loadingSection.style.display = 'none';
                        alert(`Error: ${error.message}`);
                    });
                });
                
                // Display analysis results
                function displayAnalysisResults(data) {
                    const biasAnalysis = data.bias_analysis;
                    const score = Math.round(biasAnalysis.bias_score);
                    
                    // Update bias score and assessment
                    document.getElementById('biasScoreBadge').textContent = score;
                    
                    // Set bias score color
                    let biasScoreClass = 'bg-low';
                    if (score > 30 && score <= 70) {
                        biasScoreClass = 'bg-medium';
                    } else if (score > 70) {
                        biasScoreClass = 'bg-high';
                    }
                    document.getElementById('biasScoreBadge').className = `bias-score ${biasScoreClass}`;
                    
                    // Set bias assessment text
                    document.getElementById('biasAssessment').textContent = getBiasAssessment(score);
                    
                    // Display bias categories
                    const categories = biasAnalysis.bias_categories;
                    if (categories) {
                        let categoriesHtml = '';
                        
                        const categoryLabels = {
                            political: 'Political',
                            emotional: 'Emotional',
                            framing: 'Framing',
                            source: 'Source',
                            factual: 'Factual',
                            omission: 'Omission'
                        };
                        
                        for (const [category, count] of Object.entries(categories)) {
                            if (count > 0) {
                                const label = categoryLabels[category] || category;
                                categoriesHtml += `
                                    <div class="col-md-4 col-sm-6 mb-3">
                                        <div class="d-flex justify-content-between">
                                            <span style="color: #333; font-weight: bold;">${label}</span>
                                            <span class="badge bg-primary">${count}</span>
                                        </div>
                                        <div class="progress" style="height: 8px; margin-top: 5px; background-color: #e9ecef;">
                                            <div class="progress-bar bg-primary" role="progressbar" style="width: ${Math.min(count * 10, 100)}%;" aria-valuenow="${count}" aria-valuemin="0" aria-valuemax="10"></div>
                                        </div>
                                    </div>
                                `;
                            }
                        }
                        
                        document.getElementById('biasCategories').innerHTML = categoriesHtml;
                    } else {
                        document.getElementById('biasCategories').innerHTML = '<p class="text-center text-muted">No categories data available</p>';
                    }
                    
                    // Display bias instances
                    const instances = biasAnalysis.bias_instances;
                    if (instances && instances.length > 0) {
                        let instancesHtml = '';
                        
                        instances.forEach((instance, index) => {
                            const severityClass = instance.severity <= 3 ? 'severity-low' : instance.severity <= 7 ? 'severity-medium' : 'severity-high';
                            
                            instancesHtml += `
                                <div class="bias-instance">
                                    <div class="d-flex justify-content-between mb-2">
                                        <span class="instance-text">${instance.text}</span>
                                        <span class="instance-severity ${severityClass}">${instance.category}</span>
                                    </div>
                                    <div>
                                        <p class="mb-1"><strong>Severity:</strong> ${instance.severity}/10</p>
                                        <p class="mb-1"><strong>Balanced alternative:</strong> ${instance.balanced_alternative}</p>
                                        ${instance.missing_context ? `<p class="mb-0"><strong>Missing context:</strong> ${instance.missing_context}</p>` : ''}
                                    </div>
                                </div>
                            `;
                        });
                        
                        document.getElementById('biasInstances').innerHTML = instancesHtml;
                    } else {
                        document.getElementById('biasInstances').innerHTML = '<p class="text-center text-muted">No bias instances detected</p>';
                    }
                    
                    // Display missing context
                    const missingContextItems = biasAnalysis.missing_context;
                    if (missingContextItems && missingContextItems.length > 0) {
                        let missingContextHtml = '';
                        
                        missingContextItems.forEach((item, index) => {
                            missingContextHtml += `
                                <div class="context-item">
                                    <p class="mb-1"><strong>${item.statement}</strong></p>
                                    <p class="mb-1"><strong>Missing context:</strong> ${item.context}</p>
                                    <p class="mb-0"><strong>Importance:</strong> ${item.importance}/10</p>
                                </div>
                            `;
                        });
                        
                        document.getElementById('missingContext').innerHTML = missingContextHtml;
                    } else {
                        document.getElementById('missingContext').innerHTML = '<p class="text-center text-muted">No missing context detected</p>';
                    }
                    
                    // Display original and rewritten content
                    document.getElementById('rewrittenContent').innerHTML = formatContent(data.rewritten);
                    document.getElementById('originalContent').innerHTML = formatContent(data.original);
                    document.getElementById('compareRewrittenContent').innerHTML = formatContent(data.rewritten);
                    
                    // Display diff
                    displayDiff(data.comparison);
                }
                
                // Format article content for display
                function formatContent(content) {
                    if (!content) return '<p>No content available</p>';
                    
                    return content
                        .split('\\n\\n')
                        .map(paragraph => `<p>${paragraph.trim()}</p>`)
                        .join('');
                }
                
                // Display diff between original and rewritten text
                function displayDiff(comparison) {
                    if (!comparison || !comparison.diff) {
                        document.getElementById('diffContent').innerHTML = '<p>No comparison data available</p>';
                        return;
                    }
                    
                    let diffHtml = '';
                    
                    comparison.diff.forEach(diff => {
                        if (diff.type === 'unchanged') {
                            diffHtml += `<p>${diff.text}</p>`;
                        } else if (diff.type === 'removed') {
                            diffHtml += `<p class="diff-removed">${diff.text}</p>`;
                        } else if (diff.type === 'added') {
                            diffHtml += `<p class="diff-added">${diff.text}</p>`;
                        }
                    });
                    
                    document.getElementById('diffContent').innerHTML = diffHtml;
                }
                
                // Get bias assessment text based on score
                function getBiasAssessment(score) {
                    if (score <= 30) {
                        return 'This article shows low levels of bias and presents a relatively balanced viewpoint.';
                    } else if (score <= 70) {
                        return 'This article contains moderate bias. Some statements may lack context or present a particular viewpoint.';
                    } else {
                        return 'This article shows significant bias. It presents a one-sided viewpoint with emotional language or missing context.';
                    }
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
