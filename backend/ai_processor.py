"""AI processing module for bias detection and rewriting"""
from typing import List, Dict, Any, Tuple, Optional
import re
from textblob import TextBlob  # type: ignore
from backend.models import BiasMetrics
from backend.text_utils import clean_text, split_into_sections, compare_texts

def analyze_text(text: str) -> BiasMetrics:
    """
    Analyze text for bias and sentiment.
    """
    metrics = BiasMetrics()
    
    # Preprocess text
    text = clean_text(text)
    if not text:
        return metrics

    # Split text into manageable sections
    sections = split_into_sections(text)
    
    # Process each section
    section_sentiments: List[float] = []
    section_subjectivities: List[float] = []

    for section in sections:
        try:
            sentiment, subjectivity = _analyze_sentiment(section)
            section_sentiments.append(sentiment)
            section_subjectivities.append(subjectivity)
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            continue

    # Calculate average scores if we have any valid sections
    if section_sentiments:
        metrics.sentiment_score = sum(section_sentiments) / len(section_sentiments)
        metrics.subjectivity_score = sum(section_subjectivities) / len(section_subjectivities)

    return metrics

def _analyze_sentiment(text: str) -> Tuple[float, float]:
    """
    Analyze sentiment of text using TextBlob.
    Returns a tuple of (polarity, subjectivity).
    """
    blob = TextBlob(text)
    
    # TextBlob doesn't provide proper type hints, so we need to ignore type checks here
    sentiment = float(blob.sentiment.polarity)  # type: ignore
    subjectivity = float(blob.sentiment.subjectivity)  # type: ignore
    
    return sentiment, subjectivity

def detect_bias(text: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect bias in text and provide context.
    """
    context_results: Dict[str, Any] = {
        'bias_indicators': _find_bias_indicators(text),
        'emotional_language': _detect_emotional_language(text),
        'source_credibility': _check_source_credibility(source_url) if source_url else None,
        'perspective': _analyze_perspective(text)
    }
    return context_results

def find_similar_articles(text: str, url: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Find articles similar to the input text.
    """
    # This is a placeholder for future implementation
    # Would typically integrate with a search API or article database
    return []

def _find_bias_indicators(text: str) -> List[str]:
    """
    Find common indicators of bias in text.
    """
    bias_patterns = [
        r'\b(always|never|everyone|nobody)\b',
        r'\b(must|should|ought to)\b',
        r'\b(obviously|clearly|undoubtedly)\b'
    ]
    
    indicators: List[str] = []
    for pattern in bias_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        indicators.extend(match.group() for match in matches)
    
    return indicators

def _detect_emotional_language(text: str) -> List[str]:
    """
    Detect emotional language in text.
    """
    # Placeholder for more sophisticated emotional language detection
    emotional_words = [
        r'\b(hate|love|angry|happy|sad|furious|delighted)\b',
        r'\b(terrible|amazing|awful|wonderful|horrible)\b'
    ]
    
    detected: List[str] = []
    for pattern in emotional_words:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        detected.extend(match.group() for match in matches)
    
    return detected

def _check_source_credibility(url: Optional[str]) -> Dict[str, Any]:
    """
    Check credibility of the source URL.
    """
    if not url:
        return {'score': 0.0, 'reasons': ['No URL provided']}
    
    # Placeholder for more sophisticated source checking
    return {
        'score': 0.5,
        'reasons': ['Generic credibility check - actual implementation needed']
    }

def _analyze_perspective(text: str) -> Dict[str, Any]:
    """
    Analyze the perspective and balance of the text.
    """
    # Placeholder for more sophisticated perspective analysis
    return {
        'multiple_viewpoints': False,
        'balance_score': 0.5,
        'reasons': ['Generic perspective analysis - actual implementation needed']
    }

def rewrite_text(text: str, target_metrics: Optional[Dict[str, float]] = None) -> str:
    """
    Rewrite text to reduce bias while maintaining meaning.
    """
    # Placeholder for actual rewriting implementation
    return text

def analyze_and_rewrite(text: str) -> Dict[str, Any]:
    """
    Analyze text for bias and provide a rewritten version.
    """
    # Analyze original text
    metrics = analyze_text(text)
    
    # Get bias detection results
    bias_results = detect_bias(text)
    
    # Attempt to rewrite if significant bias is detected
    rewritten_text = text
    if metrics.bias_score > 0.6 or metrics.subjectivity_score > 0.7:
        rewritten_text = rewrite_text(text)
    
    # Compare original and rewritten text
    diff = compare_texts(text, rewritten_text)
    
    return {
        'original_metrics': metrics.to_dict(),
        'bias_detection': bias_results,
        'rewritten_text': rewritten_text,
        'diff': diff
    }
