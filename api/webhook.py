import json
from datetime import datetime

def main(request):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'ok', 
            'timestamp': datetime.utcnow().isoformat()
        })
    }