# @license
# Copyright 2024 Amar Kumar
# SPDX-License-Identifier: MIT

import os
import re
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Initialize
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app, resources={
    r"/analyze": {
        "origins": ["chrome-extension://*"],
        "methods": ["POST"]
    }
})

# Load models
try:
    # Sentiment analysis
    sentiment_tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
    sentiment_model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
    
    # Bias detection
    bias_tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
    bias_model = AutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
    
    logging.info("✅ Models loaded successfully")
except Exception as e:
    logging.error(f"❌ Model loading failed: {e}")
    raise

def get_inflation_adjusted(amount, year):
    """Mock function - replace with BLS API"""
    current_year = 2024
    inflation_rates = {
        2020: 1.15,
        2010: 1.32,
        2000: 1.65
    }
    return round(amount * inflation_rates.get(year, 1.0), 2)

def add_economic_context(text):
    contexts = []
    
    # Inflation adjustment
    money_matches = re.finditer(r'\$(\d+)\s+in\s+(\d{4})', text)
    for match in money_matches:
        amount = float(match.group(1))
        year = int(match.group(2))
        adjusted = get_inflation_adjusted(amount, year)
        text = text.replace(match.group(0), f"{match.group(0)} (≈${adjusted} today)")
        contexts.append(f"Inflation adjustment: {match.group(0)} → ${adjusted} today")

    # GDP/Household context
    if re.search(r'\b(income|GDP|economy)\b', text, re.IGNORECASE):
        contexts.append("Context: US household size decreased 12% 2000-2020 (Census Bureau)")

    return text, contexts

def detect_bias_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    biased = []
    for sent in sentences:
        inputs = bias_tokenizer(sent, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = bias_model(**inputs)
        prob = torch.softmax(outputs.logits, dim=1)[0][1].item()
        if prob > 0.7:
            biased.append(sent)
    return biased

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get('text', '')[:2000]
        
        # Detect biased sentences
        biased_phrases = detect_bias_sentences(text)
        
        # Neutralize and add context
        neutralized = neutralize_text(text)
        neutralized, context_data = add_economic_context(neutralized)
        
        return jsonify({
            "biased_phrases": biased_phrases,
            "neutralized": neutralized,
            "context": context_data,
            "status": "success"
        })
        
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

def neutralize_text(text):
    replacements = {
        r'\bwar\b': 'conflict',
        r'\bcollaps(e|ing|ed)\b': 'decline',
        r'\bdisaster\b': 'challenge',
        r'\bfailed\b': 'did not meet expectations',
        r'\bcrisis\b': 'situation',
        r'\bcorrupt\b': 'controversial'
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)