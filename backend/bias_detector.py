import logging
import re
import difflib
import nltk
import os

# Setup logging before anything else
logging.basicConfig(level=logging.DEBUG)

# Create a directory for NLTK data in the current project folder
nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.insert(0, nltk_data_dir)

# Download NLTK data if it's not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
    logging.info("NLTK punkt data found.")
except LookupError as e:
    logging.warning(f"NLTK punkt data not found: {e}")
    try:
        logging.info(f"Attempting to download NLTK punkt data to {nltk_data_dir}...")
        nltk.download('punkt', download_dir=nltk_data_dir)
        logging.info("NLTK punkt data successfully downloaded.")
    except Exception as download_error:
        logging.error(f"Failed to download NLTK data: {download_error}")
        logging.warning("Will use fallback tokenization methods.")

from nltk.tokenize import sent_tokenize
from backend.ai_processor import detect_bias, rewrite_for_balance, detect_missing_context

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def clean_text(text):
    """
    Clean article text by removing extra whitespace and normalizing text
    """
    # Remove extra spaces, newlines, and tabs
    text = re.sub(r'\s+', ' ', text)
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_main_content(text):
    """
    Extract the main content from article text, removing ads, navigation, etc.
    """
    # Basic implementation - more sophisticated content extraction would be needed
    # for production but this gives a starting point
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    # Filter out likely non-content paragraphs (too short, or containing common ad phrases)
    content_paragraphs = [p for p in paragraphs if len(p) > 50 and not re.search(r'(advertisement|subscribe|sign up)', p, re.IGNORECASE)]
    
    return '\n\n'.join(content_paragraphs)

def split_into_sections(text, max_length=1000):
    """
    Split large articles into manageable sections for analysis
    """
    try:
        # Try to use NLTK for sentence tokenization
        sentences = sent_tokenize(text)
    except Exception as e:
        logging.warning(f"NLTK sentence tokenization failed in split_into_sections: {str(e)}. Using fallback method.")
        # Fallback to enhanced regex-based method
        def fallback_sentence_tokenize(text):
            if not text:
                return []
                
            # First, normalize line breaks
            text = re.sub(r'\r\n|\r', '\n', text)
            
            # Handle common abbreviations to avoid splitting them (Mr., Dr., etc.)
            text = re.sub(r'(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|St\.|etc\.|i\.e\.|e\.g\.)', lambda m: m.group().replace('.', '<POINT>'), text)
            
            # Try multiple matching patterns for robustness
            try:
                # Approach 1: Match standard sentence endings
                sentences = re.split(r'(?<=[.!?])\s+', text)
                if len(sentences) <= 1 and len(text) > 100:
                    # If first approach didn't work well, try another
                    sentences = re.split(r'(?<=[.!?:])\s+|(?<=\n)\s*', text)
            except Exception as regex_error:
                logging.warning(f"Regex-based sentence split failed: {regex_error}")
                # Emergency fallback: split by paragraphs
                sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
                if not sentences:
                    # Last resort: return the whole text
                    sentences = [text]
            
            # Restore abbreviation periods and clean up sentences
            sentences = [s.replace('<POINT>', '.').strip() for s in sentences if s.strip()]
            
            return sentences
            
        sentences = fallback_sentence_tokenize(text)
    
    sections = []
    current_section = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) > max_length and current_section:
            sections.append(' '.join(current_section))
            current_section = [sentence]
            current_length = len(sentence)
        else:
            current_section.append(sentence)
            current_length += len(sentence)
    
    if current_section:
        sections.append(' '.join(current_section))
    
    # If sections couldn't be created, split text by character length as last resort
    if not sections and text:
        logging.warning("Sentence tokenization failed. Splitting by character length.")
        text_length = len(text)
        for i in range(0, text_length, max_length):
            end = min(i + max_length, text_length)
            sections.append(text[i:end])
    
    return sections

def analyze_article(content, url=None, api_key=None):
    """
    Analyze an article for bias, categorizing and quantifying different types
    
    Args:
        content (str): The article content
        url (str, optional): The URL of the article
        api_key (str, optional): The OpenAI API key to use
        
    Returns:
        dict: Analysis results including bias scores, bias instances, and overall assessment
    """
    try:
        # Clean and extract the main content
        cleaned_content = clean_text(content)
        main_content = extract_main_content(cleaned_content)
        
        # Split into manageable sections if long
        if len(main_content) > 2000:
            sections = split_into_sections(main_content)
        else:
            sections = [main_content]
        
        # Process each section
        section_analyses = []
        for section in sections:
            section_analysis = detect_bias(section, api_key)
            section_analyses.append(section_analysis)
        
        # Combine section analyses
        bias_instances = []
        bias_categories = {
            "political": 0,
            "emotional": 0,
            "framing": 0,
            "source": 0,
            "factual": 0,
            "omission": 0
        }
        
        total_sections = len(section_analyses)
        
        for analysis in section_analyses:
            for instance in analysis.get("bias_instances", []):
                bias_instances.append(instance)
                # Increment category count
                category = instance.get("category", "other")
                if category in bias_categories:
                    bias_categories[category] += 1
        
        # Calculate overall bias score (0-100)
        total_bias_instances = len(bias_instances)
        bias_severity_sum = sum(instance.get("severity", 0) for instance in bias_instances)
        
        # Avoid division by zero
        overall_bias_score = 0
        if total_bias_instances > 0:
            overall_bias_score = min(100, (bias_severity_sum / total_bias_instances) * 20)
        
        # Determine missing context
        missing_context = detect_missing_context(main_content, api_key)
        
        result = {
            "bias_score": overall_bias_score,
            "bias_categories": bias_categories,
            "bias_instances": bias_instances,
            "missing_context": missing_context,
            "total_bias_instances": total_bias_instances
        }
        
        if url:
            result["url"] = url
            
        return result
            
    except Exception as e:
        logging.error(f"Error analyzing article: {str(e)}")
        raise

def rewrite_article(content, bias_analysis, api_key=None):
    """
    Rewrite an article to present a more balanced viewpoint
    
    Args:
        content (str): The original article content
        bias_analysis (dict): The bias analysis results
        api_key (str, optional): The OpenAI API key to use
        
    Returns:
        str: The rewritten article
    """
    try:
        # Clean and extract the main content
        cleaned_content = clean_text(content)
        main_content = extract_main_content(cleaned_content)
        
        # Split into manageable sections if long
        if len(main_content) > 2000:
            sections = split_into_sections(main_content)
        else:
            sections = [main_content]
        
        # Rewrite each section
        rewritten_sections = []
        for section in sections:
            rewritten_section = rewrite_for_balance(section, bias_analysis, api_key)
            rewritten_sections.append(rewritten_section)
        
        # Combine rewritten sections
        rewritten_content = ' '.join(rewritten_sections)
        
        return rewritten_content
            
    except Exception as e:
        logging.error(f"Error rewriting article: {str(e)}")
        raise

def compare_texts(original, rewritten):
    """
    Generate a comparison between original and rewritten text
    
    Args:
        original (str): The original text
        rewritten (str): The rewritten text
        
    Returns:
        dict: Comparison information including changes and diff
    """
    try:
        # Split texts into sentences for comparison
        try:
            # Try to use NLTK tokenizer
            original_sentences = sent_tokenize(original)
            rewritten_sentences = sent_tokenize(rewritten)
        except Exception as e:
            logging.warning(f"NLTK sentence tokenization failed: {str(e)}. Using fallback method.")
            # Fallback to a more sophisticated regex-based method that handles common sentence ending patterns
            def fallback_sentence_tokenize(text):
                if not text:
                    return []
                    
                # First, normalize line breaks
                text = re.sub(r'\r\n|\r', '\n', text)
                
                # Handle common abbreviations to avoid splitting them (Mr., Dr., etc.)
                text = re.sub(r'(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|St\.|etc\.|i\.e\.|e\.g\.)', lambda m: m.group().replace('.', '<POINT>'), text)
                
                # Try multiple matching patterns for robustness
                try:
                    # Approach 1: Match standard sentence endings
                    sentences = re.split(r'(?<=[.!?])\s+', text)
                    if len(sentences) <= 1 and len(text) > 100:
                        # If first approach didn't work well, try another
                        sentences = re.split(r'(?<=[.!?:])\s+|(?<=\n)\s*', text)
                except Exception as regex_error:
                    logging.warning(f"Regex-based sentence split failed: {regex_error}")
                    # Emergency fallback: split by paragraphs
                    sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
                    if not sentences:
                        # Last resort: return the whole text
                        sentences = [text]
                
                # Restore abbreviation periods and clean up sentences
                sentences = [s.replace('<POINT>', '.').strip() for s in sentences if s.strip()]
                
                return sentences
                
            original_sentences = fallback_sentence_tokenize(original)
            rewritten_sentences = fallback_sentence_tokenize(rewritten)
        
        # Use difflib to get differences
        differ = difflib.Differ()
        diff = list(differ.compare(original_sentences, rewritten_sentences))
        
        # Calculate statistics
        added = len([line for line in diff if line.startswith('+ ')])
        removed = len([line for line in diff if line.startswith('- ')])
        changed = len([line for line in diff if line.startswith('? ')])
        
        # Format the differences for display
        formatted_diff = []
        for i, line in enumerate(diff):
            if line.startswith('  '):  # unchanged
                formatted_diff.append({"type": "unchanged", "text": line[2:]})
            elif line.startswith('- '):  # removed
                formatted_diff.append({"type": "removed", "text": line[2:]})
            elif line.startswith('+ '):  # added
                formatted_diff.append({"type": "added", "text": line[2:]})
        
        return {
            "changes": {
                "added": added,
                "removed": removed,
                "changed": changed
            },
            "diff": formatted_diff
        }
    except Exception as e:
        logging.error(f"Error comparing texts: {str(e)}")
        # Return a simple diff if all else fails
        return {
            "changes": {
                "added": 0,
                "removed": 0,
                "changed": 0
            },
            "diff": [
                {"type": "unchanged", "text": original},
                {"type": "added", "text": rewritten}
            ]
        }
