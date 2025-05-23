"""Text processing utilities for BiasDetector"""
import re
import logging
import difflib
from typing import List, Dict, cast
from nltk.tokenize import sent_tokenize as nltk_sent_tokenize  # type: ignore

logger = logging.getLogger(__name__)

def sent_tokenize(text: str) -> List[str]:
    """Wrapper around NLTK's sent_tokenize with proper type hints."""
    return cast(List[str], nltk_sent_tokenize(text))

def clean_text(text: str) -> str:
    """Clean article text by removing extra whitespace and normalizing text"""
    # Remove extra spaces, newlines, and tabs
    text = re.sub(r'\s+', ' ', text)
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_main_content(text: str) -> str:
    """Extract the main content from article text, removing ads, navigation, etc."""
    # Basic implementation - more sophisticated content extraction would be needed
    # for production but this gives a starting point
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    # Filter out likely non-content paragraphs (too short, or containing common ad phrases)
    content_paragraphs = [p for p in paragraphs if len(p) > 50 and not re.search(r'(advertisement|subscribe|sign up)', p, re.IGNORECASE)]
    
    return '\n\n'.join(content_paragraphs)

def split_into_sections(text: str, max_length: int = 1000) -> List[str]:
    """Split large articles into manageable sections for analysis"""
    sections: List[str] = []
    
    try:
        # Try to split by sentences first
        sentences: List[str] = sent_tokenize(text)
        current_section: List[str] = []
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
    except Exception:
        # Fallback: split by character count if sentence tokenization fails
        text_length = len(text)
        for i in range(0, text_length, max_length):
            end = min(i + max_length, text_length)
            sections.append(text[i:end])
    
    return sections

def compare_texts(original: str, rewritten: str) -> List[Dict[str, str]]:
    """
    Compare original and rewritten texts and return a structured diff.
    Returns a list of dicts with 'type' ('unchanged', 'removed', or 'added') and 'text'.
    """
    if not original or not rewritten:
        return []

    try:
        original_sentences = list(sent_tokenize(original))
        rewritten_sentences = list(sent_tokenize(rewritten))

        # If sentence tokenization fails, fall back to line-by-line
        if not original_sentences or not rewritten_sentences:
            original_sentences = original.splitlines()
            rewritten_sentences = rewritten.splitlines()

        differ = difflib.Differ()
        diff = list(differ.compare(original_sentences, rewritten_sentences))
        
        formatted_diff: List[Dict[str, str]] = []
        for line in diff:
            if line.startswith('  '):
                formatted_diff.append({"type": "unchanged", "text": line[2:]})
            elif line.startswith('- '):
                formatted_diff.append({"type": "removed", "text": line[2:]})
            elif line.startswith('+ '):
                formatted_diff.append({"type": "added", "text": line[2:]})
        
        return formatted_diff
    except Exception as e:
        print(f"Error comparing texts: {str(e)}")
        return []
