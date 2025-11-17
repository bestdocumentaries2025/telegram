import os
import json
import requests
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def send_telegram_message(chat_id, text):
    """Send message to Telegram"""
    try:
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json={'chat_id': chat_id, 'text': text}
        )
    except Exception as e:
        print(f"Send message error: {e}")

def process_video(message, chat_id):
    """Process video to 720p and upload to Cloudinary"""
    try:
        send_telegram_message(chat_id, 'File processing.....wait till the link is provided')
        
        # Get file information
        if 'video' in message:
            file_id = message['video']['file_id']
        else:
            file_id = message['document']['file_id']
        
        # Get file from Telegram
        file_response = requests.get(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}'
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

def main(request):
    """Main Telegram webhook handler"""
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'Telegram webhook is running'})
        }
    
    try:
        body = json.loads(request.body)
        
        if 'message' in body:
            chat_id = body['message']['chat']['id']
            message = body['message']
            
            # Handle /start command
            if 'text' in message and message['text'] == '/start':
                send_telegram_message(chat_id, '🎬 Welcome! Send me a video file and I will process it to 720p.')
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'status': 'ok'})
                }
            
            # Handle video files
            if 'video' in message or ('document' in message and message['document'].get('mime_type', '').startswith('video/')):
                process_video(message, chat_id)
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'status': 'ok'})
                }
            
            # Handle text messages
            if 'text' in message:
                send_telegram_message(chat_id, '📹 Send me a video file to process to 720p!')
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'status': 'ok'})
                }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'error'})
        }