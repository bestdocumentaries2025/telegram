import os
import json
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def main(request):
    """Set Telegram webhook"""
    try:
        domain = request.headers.get('host', 'your-domain.vercel.app')
        webhook_url = f"https://{domain}/api"
        
        result = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={'url': webhook_url}
        ).json()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': result.get('ok', False),
                'webhook_url': webhook_url,
                'telegram_response': result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }