import os
import json
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def main(request):
    """Get webhook info"""
    try:
        result = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
        ).json()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': result.get('ok', False),
                'webhook_info': result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }