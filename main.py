from flask import Flask, request, jsonify, render_template_string
import requests
import cloudinary
import cloudinary.uploader
import os
import json

app = Flask(__name__)

# Configuration from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Video Processor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid; }
        .success { background: #d4edda; color: #155724; border-left-color: #28a745; }
        .error { background: #f8d7da; color: #721c24; border-left-color: #dc3545; }
        .processing { background: #fff3cd; color: #856404; border-left-color: #ffc107; }
        button { padding: 12px 25px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; font-size: 16px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .url-box { background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0; word-break: break-all; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Telegram Video to 720p Processor</h1>
        <div id="status" class="status success">✅ Ready to set up your Telegram bot</div>
        
        <div class="section">
            <h2>1. Setup Telegram Webhook</h2>
            <button onclick="setWebhook()" id="webhook-btn">Set Telegram Webhook</button>
            <button onclick="checkWebhook()" id="check-btn">Check Webhook Status</button>
            <div id="webhook-result"></div>
        </div>

        <div class="section">
            <h2>2. Test Your Bot</h2>
            <p>Go to your bot and send a video file:</p>
            <div class="url-box">https://t.me/MP4LINKGENBOT</div>
            <p><strong>Workflow:</strong></p>
            <ol>
                <li>Send video file to bot</li>
                <li>Bot: "File processing.....wait till the link is provided"</li>
                <li>Bot processes to 720p</li>
                <li>Bot sends: "✅ Your 720p video is ready!" + Download URL</li>
            </ol>
        </div>
    </div>

    <script>
        async function setWebhook() {
            const btn = document.getElementById('webhook-btn');
            btn.disabled = true;
            btn.textContent = 'Setting...';
            
            document.getElementById('status').className = 'status processing';
            document.getElementById('status').textContent = 'Setting up Telegram webhook...';
            
            try {
                const response = await fetch('/api/set-webhook', {method: 'POST'});
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('status').className = 'status success';
                    document.getElementById('status').textContent = '✅ Webhook set successfully! Your bot is now ready.';
                    document.getElementById('webhook-result').innerHTML = 
                        '<div class="status success"><strong>Webhook URL:</strong><br><div class="url-box">' + 
                        data.webhook_url + '</div></div>';
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            } catch (error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = '❌ Failed to set webhook: ' + error.message;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Set Telegram Webhook';
            }
        }
        
        async function checkWebhook() {
            const btn = document.getElementById('check-btn');
            btn.disabled = true;
            btn.textContent = 'Checking...';
            
            document.getElementById('status').className = 'status processing';
            document.getElementById('status').textContent = 'Checking webhook status...';
            
            try {
                const response = await fetch('/api/webhook-info');
                const data = await response.json();
                
                if (data.success) {
                    const info = data.webhook_info.result;
                    let statusHtml = '<div class="status ' + (info.url ? 'success' : 'error') + '">' +
                        '<strong>Webhook URL:</strong> ' + (info.url || 'Not set') + '<br>' +
                        '<strong>Pending Updates:</strong> ' + info.pending_update_count + '<br>' +
                        '<strong>Last Error:</strong> ' + (info.last_error_message || 'None') + '</div>';
                    
                    document.getElementById('webhook-result').innerHTML = statusHtml;
                    
                    if (info.url) {
                        document.getElementById('status').className = 'status success';
                        document.getElementById('status').textContent = '✅ Webhook is active and configured.';
                    } else {
                        document.getElementById('status').className = 'status error';
                        document.getElementById('status').textContent = '❌ Webhook is not set.';
                    }
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            } catch (error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = '❌ Failed to check webhook: ' + error.message;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Check Webhook Status';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/set-webhook', methods=['POST'])
def api_set_webhook():
    try:
        domain = request.headers.get('Host', 'your-domain.vercel.app')
        webhook_url = f"https://{domain}/api/webhook"
        
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={'url': webhook_url}
        )
        
        data = response.json()
        return jsonify({
            'success': data.get('ok', False),
            'webhook_url': webhook_url,
            'telegram_response': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/webhook-info', methods=['GET'])
def api_webhook_info():
    try:
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo")
        data = response.json()
        return jsonify({'success': data.get('ok', False), 'webhook_info': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'ok', 'timestamp': '2024-01-01T00:00:00Z'})

# Telegram webhook handler
@app.route('/api/webhook', methods=['POST', 'GET'])
def telegram_webhook():
    if request.method == 'GET':
        return jsonify({'status': 'Telegram webhook is running'})
    
    try:
        data = request.get_json()
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            message = data['message']
            
            # Handle /start command
            if 'text' in message and message['text'] == '/start':
                send_telegram_message(chat_id, '🎬 Welcome! Send me a video file and I will process it to 720p.')
                return jsonify({'status': 'ok'})
            
            # Handle video files
            if 'video' in message or ('document' in message and message['document'].get('mime_type', '').startswith('video/')):
                process_video_message(message, chat_id)
                return jsonify({'status': 'ok'})
            
            # Handle text messages
            if 'text' in message:
                send_telegram_message(chat_id, '📹 Send me a video file to process to 720p!')
                return jsonify({'status': 'ok'})
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

def process_video_message(message, chat_id):
    try:
        send_telegram_message(chat_id, 'File processing.....wait till the link is provided')
        
        # Get file information
        if 'video' in message:
            file_id = message['video']['file_id']
        else:
            file_id = message['document']['file_id']
        
        # Get file path from Telegram
        file_response = requests.get(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile',
            params={'file_id': file_id}
        )
        file_data = file_response.json()
        file_path = file_data['result']['file_path']
        file_url = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}'
        
        # Upload to Cloudinary with 720p processing
        upload_result = cloudinary.uploader.upload(
            file_url,
            resource_type="video",
            folder="telegram_videos",
            transformation=[
                {"width": 1280, "height": 720, "crop": "scale"},
                {"video_codec": "h264"},
                {"audio_codec": "aac"},
                {"bit_rate": "1500k"},
                {"quality": "auto"},
                {"format": "mp4"}
            ]
        )
        
        send_telegram_message(chat_id, f'✅ Your 720p video is ready!\n\n🔗 {upload_result["secure_url"]}')
        
    except Exception as e:
        print(f"Video processing error: {e}")
        send_telegram_message(chat_id, '❌ Error processing video')

def send_telegram_message(chat_id, text):
    try:
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': text
            }
        )
    except Exception as e:
        print(f"Send message error: {e}")

if __name__ == '__main__':
    app.run(debug=True)