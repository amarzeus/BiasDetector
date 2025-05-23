"""Error handling for the BiasDetector API"""
from typing import Dict, Any, Optional
from flask import jsonify
from werkzeug.exceptions import HTTPException

class BiasDetectorError(Exception):
    """Base error class for BiasDetector"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(BiasDetectorError):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class APIError(BiasDetectorError):
    """Raised when an external API (like OpenAI) fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)

def handle_error(error: Exception) -> tuple[Dict[str, Any], int]:
    """Convert exceptions to JSON responses"""
    if isinstance(error, BiasDetectorError):
        response = {
            'error': error.message,
            'status': 'error',
            'details': error.details
        }
        return jsonify(response), error.status_code
    
    if isinstance(error, HTTPException):
        response = {
            'error': error.description,
            'status': 'error'
        }
        return jsonify(response), error.code
    
    # Handle unexpected errors
    response = {
        'error': 'An unexpected error occurred',
        'status': 'error',
        'details': {'message': str(error)} if str(error) else {}
    }
    return jsonify(response), 500
