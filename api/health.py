import json
from datetime import datetime

def handler(request, response):
    """Health check endpoint"""
    return response.json({
        'status': 'ok', 
        'timestamp': datetime.utcnow().isoformat()
    })