# @license
# Copyright 2024 Amar Kumar
# SPDX-License-Identifier: MIT

import os
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Initialize
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

# Load models - UPDATED WITH from_tf=True
try:
    tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
    model = AutoModelForSequenceClassification.from_pretrained(
        "d4data/bias-detection-model",
        from_tf=True  # Critical fix for TensorFlow models
    )
    logging.info("✅ BiasDetector models loaded successfully")
except Exception as e:
    logging.error(f"❌ Model load failed: {e}")
    raise

@app.route('/analyze', methods=['POST'])
def analyze():
    if not model:
        return jsonify({"error": "Models not loaded"}), 503
        
    try:
        data = request.json
        text = data.get('text', '')[:2000]
        
        # Tokenize and predict
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Process results
        return jsonify({
            "status": "success",
            "bias_score": outputs.logits.softmax(dim=1)[0][1].item()
        })
        
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)