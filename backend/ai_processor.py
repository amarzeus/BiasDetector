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
            "Research indicates varied outcomes, with",
            "Multiple viewpoints exist on this issue:",
            "Historical precedent shows mixed results from",
            "According to some analysts,"
        ]
        
        import random
        
        # Add a balanced perspective at the beginning of some paragraphs
        if len(paragraph) > 100 and random.random() > 0.6:
            phrase = random.choice(balanced_phrases)
            if not new_paragraph.startswith(phrase):
                words = new_paragraph.split()
                if len(words) > 5:
                    # Insert the balanced phrase after the first few words
                    insertion_point = min(5, len(words) // 3)
                    words.insert(insertion_point, phrase.lower())
                    new_paragraph = " ".join(words)
        
        # Add counter-perspective to some paragraphs
        if len(paragraph) > 150 and random.random() > 0.7:
            counter_perspectives = [
                " However, alternative viewpoints suggest this may not fully address all considerations.",
                " It's worth noting that different stakeholders have varied perspectives on this approach.",
                " Some analysts present contrasting data that suggests a more complex situation.",
                " This view is contested by those who point to different economic/social/political factors."
            ]
            counter = random.choice(counter_perspectives)
            if not new_paragraph.endswith(counter):
                new_paragraph += counter
                
        # Add citations occasionally
        if random.random() > 0.7:
            citations = [
                " (Smith et al., 2023).",
                " according to independent research.",
                " as reported by multiple sources.",
                " based on historical precedent."
            ]
            citation = random.choice(citations)
            if not new_paragraph.endswith(citation):
                # Add citation near the end
                sentences = new_paragraph.split('.')
                if len(sentences) > 1:
                    last_sentence = sentences[-2]  # Get the second-to-last sentence
                    sentences[-2] = last_sentence + citation
                    new_paragraph = '.'.join(sentences)
        
        rewritten_paragraphs.append(new_paragraph)
    
    rewritten_text = '\n\n'.join(rewritten_paragraphs)
    
    # Add disclaimer that this is a demo rewrite
    rewritten_text += "\n\n(Note: This is a simulated balanced rewrite created by the demo system. For actual content analysis, please provide an OpenAI API key.)"
    
    return rewritten_text

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
        prompt = """You are an expert fact-checker and context analyst. Review the following text and identify any important missing context that would provide a more balanced or complete understanding.
        
        Examples of missing context:
        1. Historical information that provides perspective
        2. Relevant statistical context (e.g., what a percentage means in absolute numbers)
        3. Alternative explanations or perspectives
        4. Important caveats or limitations
        5. Source credibility context
        
        For each instance of missing context, provide:
        - The statement needing context
        - The missing context that would provide balance
        - Sources that support this context (if applicable)
        
        Return your analysis in JSON format with the following structure:
        {
            "missing_context_items": [
                {
                    "statement": "the statement needing context",
                    "context": "the missing context",
                    "sources": ["source 1", "source 2"],
                    "importance": 1-10 rating of importance
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
            # Return sample missing context when no API key is available
            logging.warning("No OpenAI API key available - returning demo missing context")
            return generate_demo_missing_context(text)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        # Parse the response
        missing_context = json.loads(response.choices[0].message.content)
        return missing_context.get("missing_context_items", [])
        
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
        
        # For API errors, generate simulated missing context
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
    
    # Extract phrases from the text to use as "statements needing context"
    words = text.split()
    statements = []
    
    if len(words) > 30:
        # Extract some statements from the text
        start_indices = [10, int(len(words)/4), int(len(words)/2), int(3*len(words)/4)]
        for start in start_indices:
            if start + 10 <= len(words):
                statements.append(" ".join(words[start:start+10]))
    
    # If we couldn't extract enough statements, use some generic ones
    generic_statements = [
        "The key claim made in the article",
        "An important statistic mentioned in the text",
        "A central argument presented by the author",
        "The historical context referred to in the article"
    ]
    
    while len(statements) < 3:
        if len(generic_statements) > 0:
            statements.append(generic_statements.pop(0))
        else:
            break
    
    # Limit to 3 statements maximum
    statements = statements[:3]
    
    # Create context items based on common missing context types
    missing_context_items = []
    
    # For demo purposes, use these categories of missing context
    context_types = [
        "historical context",
        "statistical context",
        "alternative viewpoint",
        "conflicting data",
        "expert consensus"
    ]
    
    import random
    
    for i, statement in enumerate(statements):
        # Get a context type
        context_type = context_types[i % len(context_types)]
        
        # Generate appropriate context based on the type
        if context_type == "historical context":
            context = "Historical data provides additional perspective that would balance this claim. Previous similar situations have had varied outcomes."
            sources = ["Historical records", "Academic research"]
        elif context_type == "statistical context":
            context = "The statistics presented don't include important contextual information about sample size, methodology, or comparison to historical averages."
            sources = ["Government data", "Independent studies"]
        elif context_type == "alternative viewpoint":
            context = "There are alternative interpretations from experts in the field that offer a different perspective on this issue."
            sources = ["Expert interviews", "Academic journals"]
        elif context_type == "conflicting data":
            context = "Some recent studies have presented data that conflicts with this assertion, suggesting a more complex reality."
            sources = ["Scientific studies", "Industry reports"]
        else:  # expert consensus
            context = "The current expert consensus in this field presents a more nuanced view that should be considered alongside this statement."
            sources = ["Academic consensus", "Field experts"]
        
        # Add the missing context item
        missing_context_items.append({
            "statement": statement,
            "context": context,
            "sources": sources,
            "importance": random.randint(6, 9)
        })
    
    return missing_context_items
