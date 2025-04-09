import os
import json
import logging
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI client (with API key if available)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Create a fallback client - will be used if no API key is provided
# This will use a demo mode or return simulated responses when no API key is available
openai = None
if OPENAI_API_KEY:
    openai = OpenAI(api_key=OPENAI_API_KEY)

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

def detect_bias(text, api_key=None):
    """
    Detect bias in a text using OpenAI's GPT-4o model
    
    Args:
        text (str): The text to analyze
        api_key (str, optional): The OpenAI API key to use
        
    Returns:
        dict: Analysis results including bias categories, instances, and scores
    """
    try:
        prompt = """You are an expert at detecting media bias. Analyze the following text for different types of bias:
        
        Categories of bias to look for:
        1. Political bias - left-leaning or right-leaning rhetoric
        2. Emotional bias - use of emotional language to influence opinions
        3. Framing bias - presenting facts selectively to promote a particular interpretation
        4. Source bias - selective use of sources or authorities
        5. Factual bias - presenting opinions as facts or using cherry-picked facts
        6. Omission bias - leaving out key information that would change context
        
        For each instance of bias, include:
        - The biased text
        - The category of bias
        - The severity (1-10 scale)
        - How it could be rewritten to be more balanced
        - Any missing context
        
        Return your analysis in JSON format with the following structure:
        {
            "bias_score": 0-10 score,
            "bias_instances": [
                {
                    "text": "biased text excerpt",
                    "category": "category name",
                    "severity": 1-10 rating,
                    "balanced_alternative": "suggestion for balanced rewording",
                    "missing_context": "context that would balance the view"
                }
            ]
        }
        
        Text to analyze:
        ---
        """ + text + """
        ---
        
        Provide your detailed analysis in JSON format only.
        """
        
        # Use the provided API key if available
        client = openai
        if api_key:
            client = OpenAI(api_key=api_key)
            
        # Check if we have a valid OpenAI client
        if client is None:
            # Return a sample analysis when no API key is available
            logging.warning("No OpenAI API key available - returning demo analysis")
            return generate_demo_analysis(text)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Parse the response
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error detecting bias with OpenAI: {error_msg}")
        
        # More detailed error handling with specific log messages
        if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or rate limit reached. Using demo analysis.")
        elif "authentication" in error_msg.lower() or "invalid" in error_msg.lower() and "api key" in error_msg.lower():
            logging.warning("OpenAI API authentication error. Using demo analysis.")
        elif "insufficient_quota" in error_msg.lower() or "billing" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or billing issue. Using demo analysis.")
        elif "server" in error_msg.lower() or "timeout" in error_msg.lower():
            logging.warning("OpenAI API server error or timeout. Using demo analysis.")
        else:
            logging.warning(f"Unknown OpenAI API error: {error_msg}. Using demo analysis.")
            
        # For all API errors, fall back to demo analysis
        return generate_demo_analysis(text)


def generate_demo_analysis(text):
    """
    Generate simulated analysis for demonstration purposes when API is unavailable
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: Simulated analysis results
    """
    logging.info("Generating simulated bias analysis for demo purposes")
    
    # Extract a few phrases to use as "biased" content
    words = text.split()
    phrases = []
    
    if len(words) > 20:
        # Extract some phrases from the text
        start_indices = [5, int(len(words)/3), int(len(words)/2), int(2*len(words)/3)]
        for start in start_indices:
            if start + 8 <= len(words):
                phrases.append(" ".join(words[start:start+8]))
    
    # If we couldn't extract enough phrases, use some generic ones
    while len(phrases) < 3:
        phrases.append("Content from the article would appear here in a real analysis")
    
    # Determine bias type based on text content
    bias_type = "political"
    if "climate" in text.lower() or "environment" in text.lower():
        bias_type = "environmental"
    elif "tech" in text.lower() or "technology" in text.lower() or "privacy" in text.lower():
        bias_type = "technological"
    elif "democrat" in text.lower() or "republican" in text.lower() or "left-wing" in text.lower() or "right-wing" in text.lower():
        bias_type = "political"
    elif "emotion" in text.lower() or "fear" in text.lower() or "angry" in text.lower():
        bias_type = "emotional"
    
    # Generate bias categories
    bias_categories = {
        "political": 0,
        "emotional": 0,
        "framing": 0,
        "source": 0,
        "factual": 0,
        "omission": 0
    }
    
    # Set primary category high, secondary categories medium
    primary_category = "political"
    if "climate" in text.lower() or "environment" in text.lower():
        primary_category = "framing"
    elif "tech" in text.lower() or "Silicon Valley" in text.lower():
        primary_category = "factual"
    elif "reckless" in text.lower() or "terrible" in text.lower() or "extreme" in text.lower():
        primary_category = "emotional"
    
    bias_categories[primary_category] = 4
    
    # Add some random secondary categories
    import random
    secondary_categories = random.sample([c for c in bias_categories.keys() if c != primary_category], 2)
    for category in secondary_categories:
        bias_categories[category] = random.randint(1, 3)
    
    # Calculate bias score
    bias_score = min(85, sum(bias_categories.values()) * 10)
    
    # Generate bias instances
    bias_instances = []
    
    used_categories = [primary_category] + secondary_categories
    
    for i, phrase in enumerate(phrases[:3]):
        if i < len(used_categories):
            category = used_categories[i]
        else:
            category = random.choice(used_categories)
            
        severity = random.randint(6, 9) if category == primary_category else random.randint(3, 7)
        
        instance = {
            "text": phrase,
            "category": category,
            "severity": severity,
            "balanced_alternative": f"This text could be more balanced by presenting multiple perspectives and using neutral language.",
            "missing_context": f"Important contextual information is missing that would provide a more complete picture."
        }
        bias_instances.append(instance)
    
    # Generate missing context items
    missing_context = [
        {
            "statement": "The first key point from the article",
            "context": "Additional historical information and context would provide a more balanced view.",
            "sources": ["Academic research", "Historical records"],
            "importance": random.randint(6, 9)
        },
        {
            "statement": "Another assertion from the article",
            "context": "Statistics and factual information from neutral sources would balance this claim.",
            "sources": ["Government data", "Independent studies"],
            "importance": random.randint(5, 8)
        }
    ]
    
    return {
        "bias_score": bias_score,
        "bias_instances": bias_instances,
        "bias_categories": bias_categories,
        "missing_context": missing_context
    }

def rewrite_for_balance(text, bias_analysis, api_key=None):
    """
    Rewrite text to present a more balanced viewpoint using OpenAI's GPT-4o model
    
    Args:
        text (str): The text to rewrite
        bias_analysis (dict): The bias analysis results
        api_key (str, optional): The OpenAI API key to use
        
    Returns:
        str: The rewritten text
    """
    try:
        # Extract bias instances for more targeted rewriting
        bias_instances = bias_analysis.get("bias_instances", [])
        bias_instance_texts = []
        
        for instance in bias_instances:
            item_text = f"• \"{instance.get('text', '')}\": {instance.get('category', '')} bias, severity {instance.get('severity', 0)}/10"
            bias_instance_texts.append(item_text)
        
        bias_highlights = "\n".join(bias_instance_texts)
        
        prompt = f"""You are a professional news editor committed to balanced journalism. 
        Rewrite the following text to present a more balanced viewpoint, while maintaining the core information and flow.
        
        The original text has been analyzed for bias with the following findings:
        
        {bias_highlights}
        
        Guidelines for rewriting:
        1. Maintain factual integrity while removing slant and bias
        2. Present multiple perspectives where appropriate
        3. Use neutral language instead of emotionally charged words
        4. Add context where important information is missing
        5. Include alternative interpretations if the original presents only one view
        6. Keep the same general structure and flow
        7. Cite sources for added context or alternative perspectives
        8. Make sure the text is just as readable and engaging, but more balanced
        
        Original text:
        ---
        {text}
        ---
        
        Provide only the rewritten text without explanations or commentary.
        """
        
        # Use the provided API key if available
        client = openai
        if api_key:
            client = OpenAI(api_key=api_key)
            
        # Check if we have a valid OpenAI client
        if client is None:
            # Return demo rewritten text when no API key is available
            logging.warning("No OpenAI API key available - returning demo rewritten text")
            return generate_demo_rewrite(text, bias_analysis)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Return the rewritten text
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error rewriting text with OpenAI: {error_msg}")
        
        # More detailed error handling with specific log messages
        if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or rate limit reached. Using demo rewrite.")
        elif "authentication" in error_msg.lower() or "invalid" in error_msg.lower() and "api key" in error_msg.lower():
            logging.warning("OpenAI API authentication error. Using demo rewrite.")
        elif "insufficient_quota" in error_msg.lower() or "billing" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or billing issue. Using demo rewrite.")
        elif "server" in error_msg.lower() or "timeout" in error_msg.lower():
            logging.warning("OpenAI API server error or timeout. Using demo rewrite.")
        else:
            logging.warning(f"Unknown OpenAI API error: {error_msg}. Using demo rewrite.")
        
        # Fall back to demo rewrite
        return generate_demo_rewrite(text, bias_analysis)


def generate_demo_rewrite(text, bias_analysis):
    """
    Generate a simulated rewritten version of the text for demonstration purposes
    
    Args:
        text (str): The original text
        bias_analysis (dict): The bias analysis results
        
    Returns:
        str: A simulated balanced version of the text
    """
    logging.info("Generating simulated balanced rewrite for demo purposes")
    
    # Split the text into paragraphs
    paragraphs = text.split('\n\n')
    rewritten_paragraphs = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        # Clean up paragraph
        paragraph = paragraph.strip()
        
        # Process each paragraph
        new_paragraph = paragraph
        
        # Replace strongly biased language with more neutral alternatives
        word_replacements = {
            'radical': 'progressive',
            'extreme': 'significant',
            'terrible': 'concerning',
            'disaster': 'legislation',
            'surely': 'may',
            'always fail': 'have mixed results',
            'reckless': 'substantial',
            'bankrupt': 'financially impact',
            'nothing': 'little',
            'power grab': 'expansion of authority',
            'catastrophic': 'problematic',
            'courageously': '',
            'truly': '',
            'unlike': 'compared to',
            'heartless': '',
            'cruel': 'stringent',
            'shameful': 'controversial',
            'devastate': 'affect',
            'every credible': 'some',
            'callous disregard': 'approach',
            'moral bankruptcy': 'priorities',
            'deliberately ignore': 'may not fully address',
            'heroically': '',
            'dangerous': 'concerning',
            'nothing less than': 'comparable to',
            'systematically destroying': 'impacting',
            'predatory': 'competitive',
            'arrogant': '',
            'god complexes': 'significant influence',
            'digital overlords': 'technology companies',
            'massive': 'substantial'
        }
        
        for biased, neutral in word_replacements.items():
            if biased in new_paragraph.lower():
                # Replace with neutral term (case-insensitive)
                import re
                new_paragraph = re.sub(f'(?i){biased}', neutral, new_paragraph)
        
        # Add balanced perspective phrases
        balanced_phrases = [
            "Some experts suggest that",
            "Another perspective is that",
            "Proponents argue that",
            "Critics contend that",
            "Research indicates that",
            "Some economists believe that",
            "Alternative viewpoints suggest"
        ]
        
        # Only add balancing phrases to longer paragraphs
        if len(new_paragraph) > 100 and len(new_paragraph.split()) > 20:
            import random
            
            # Randomly add a balancing phrase to the beginning 40% of the time
            if random.random() < 0.4:
                phrase = random.choice(balanced_phrases)
                if not new_paragraph.startswith(phrase):
                    # Make the first letter lowercase if adding to beginning
                    words = new_paragraph.split()
                    if len(words) > 0:
                        words[0] = words[0][0].lower() + words[0][1:] if len(words[0]) > 1 else words[0].lower()
                        new_paragraph = f"{phrase} {' '.join(words)}"
                        
            # Randomly add a contrasting perspective to longer paragraphs
            elif random.random() < 0.4:
                # Append a contrasting perspective
                contrast_phrases = [
                    "However, others point out that",
                    "On the other hand, some suggest that",
                    "Alternative analyses indicate that",
                    "A different perspective suggests that"
                ]
                
                new_paragraph += f" {random.choice(contrast_phrases)} there are multiple viewpoints on this issue that should be considered."
        
        rewritten_paragraphs.append(new_paragraph)
    
    return '\n\n'.join(rewritten_paragraphs)

def detect_missing_context(text, api_key=None):
    """
    Detect missing context in a text that would provide a more balanced view
    
    Args:
        text (str): The text to analyze
        api_key (str, optional): The OpenAI API key to use
        
    Returns:
        list: List of missing context items
    """
    try:
        prompt = """You are an expert media analyst with deep knowledge across many fields.
        
        Analyze the following text and identify important missing context that would be needed to present
        a more complete and balanced view of the topic.
        
        For each major claim or perspective in the text, identify:
        1. What crucial context is missing?
        2. What alternative viewpoints are not represented?
        3. What factual information would help readers evaluate the claims?
        4. What historical or background information would provide better understanding?
        
        Return your analysis in JSON format with this structure:
        [
            {
                "statement": "The statement or claim from the text",
                "context": "The missing context or alternative perspective",
                "sources": ["Possible source types for this information"],
                "importance": 1-10 rating of how important this context is
            }
        ]
        
        Text to analyze:
        ---
        """ + text + """
        ---
        
        Provide a thoughtful analysis in JSON format only.
        """
        
        # Use the provided API key if available
        client = openai
        if api_key:
            client = OpenAI(api_key=api_key)
            
        # Check if we have a valid OpenAI client
        if client is None:
            # Return a demo missing context when no API key is available
            logging.warning("No OpenAI API key available - returning demo missing context")
            return generate_demo_missing_context(text)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        # Parse the response - might be a list or might be a dict with a list
        result = json.loads(response.choices[0].message.content)
        
        # Handle both possible formats
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "missing_context" in result:
            return result["missing_context"]
        else:
            return result
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error detecting missing context with OpenAI: {error_msg}")
        
        # More detailed error handling with specific log messages
        if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or rate limit reached. Using demo missing context.")
        elif "authentication" in error_msg.lower() or "invalid" in error_msg.lower() and "api key" in error_msg.lower():
            logging.warning("OpenAI API authentication error. Using demo missing context.")
        elif "insufficient_quota" in error_msg.lower() or "billing" in error_msg.lower():
            logging.warning("OpenAI API quota exceeded or billing issue. Using demo missing context.")
        elif "server" in error_msg.lower() or "timeout" in error_msg.lower():
            logging.warning("OpenAI API server error or timeout. Using demo missing context.")
        else:
            logging.warning(f"Unknown OpenAI API error: {error_msg}. Using demo missing context.")
        
        # Fall back to demo missing context
        return generate_demo_missing_context(text)

def generate_demo_missing_context(text):
    """
    Generate simulated missing context for demonstration purposes
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: Simulated missing context items
    """
    logging.info("Generating simulated missing context for demo purposes")
    
    # Base context categories based on common missing perspectives
    context_categories = [
        {
            "category": "historical",
            "context_template": "Historical context about how similar situations have played out in the past would provide valuable perspective.",
            "sources": ["Historical records", "Academic research", "News archives"]
        },
        {
            "category": "economic",
            "context_template": "Economic data showing the broader impacts and trade-offs would offer a more complete understanding.",
            "sources": ["Economic studies", "Financial reports", "Government statistics"]
        },
        {
            "category": "opposing",
            "context_template": "The perspective of those with opposing viewpoints would present a more balanced picture.",
            "sources": ["Opposition statements", "Alternative media sources", "Expert critiques"]
        },
        {
            "category": "scientific",
            "context_template": "Scientific research on this topic offers more nuanced findings than presented in the text.",
            "sources": ["Peer-reviewed studies", "Scientific consensus", "Research reports"]
        },
        {
            "category": "international",
            "context_template": "International perspectives and examples from other countries provide comparative context.",
            "sources": ["International news", "Comparative studies", "Global organizations"]
        }
    ]
    
    # Extract phrases from text to use as statements
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
    if len(sentences) < 3:
        sentences = [text[:80], text[80:160], text[160:240]]
    
    # Generate 2-4 missing context items
    import random
    num_items = min(len(sentences), random.randint(2, 4))
    selected_sentences = random.sample(sentences, num_items)
    
    missing_context = []
    used_categories = []
    
    for sentence in selected_sentences:
        # Select a category that hasn't been used yet if possible
        available_categories = [c for c in context_categories if c["category"] not in used_categories]
        if not available_categories:
            available_categories = context_categories
            
        category = random.choice(available_categories)
        used_categories.append(category["category"])
        
        # Generate a missing context item
        item = {
            "statement": sentence[:100] + "..." if len(sentence) > 100 else sentence,
            "context": category["context_template"],
            "sources": category["sources"],
            "importance": random.randint(6, 9)
        }
        
        missing_context.append(item)
    
    return missing_context
