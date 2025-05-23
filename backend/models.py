"""Data models for the BiasDetector application"""
from typing import Dict, Any
from collections import defaultdict
import json
import os

class BiasMetrics:
    def __init__(self) -> None:
        self.sentiment_score: float = 0.0
        self.subjectivity_score: float = 0.0
        self.bias_score: float = 0.0
        self.bias_categories: Dict[str, float] = defaultdict(float)
        self.reliable_source: bool = False
        self.source_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sentiment_score': self.sentiment_score,
            'subjectivity_score': self.subjectivity_score,
            'bias_score': self.bias_score,
            'bias_categories': dict(self.bias_categories),
            'reliable_source': self.reliable_source,
            'source_score': self.source_score
        }

class SourceCredibility:
    def __init__(self, cache_file: str = 'credibility_cache.json') -> None:
        self.cache_file = cache_file
        self.credibility_cache: Dict[str, float] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.credibility_cache = json.load(f)

    def _save_cache(self) -> None:
        with open(self.cache_file, 'w') as f:
            json.dump(self.credibility_cache, f)

    def get_credibility(self, domain: str) -> float:
        if domain in self.credibility_cache:
            return self.credibility_cache[domain]
        # Default score for unknown domains
        score = 0.5
        self.credibility_cache[domain] = score
        self._save_cache()
        return score
