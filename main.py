from fasthtml.common import *
import os
import requests
import json

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') 
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

app = FastHTML()

def set_webhook():
    """Set Telegram webhook"""
    webhook_url = f"https://{os.environ.get('VERCEL_URL')}/api/webhook"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return response.json()

def get_webhook_info():
    """Get Telegram webhook info"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    response = requests.get(url)
    return response.json()

@app.get("/")
def home():
    return Titled(
        "Telegram Video Processor",
        Div(
            H1("🎬 Telegram Video to 720p Processor"),
            Div(id="status", cls="status success", text="✅ Ready to set up your Telegram bot"),
            
            Div(
                H2("1. Setup Telegram Webhook"),
                Button("Set Telegram Webhook", onclick="setWebhook()", id="webhook-btn"),
                Button("Check Webhook Status", onclick="checkWebhook()", id="check-btn"),
                Div(id="webhook-result"),
                cls="section"
            ),
            
            Div(
                H2("2. Test Your Bot"),
                P("Go to your bot and send a video file:"),
                Code("https://t.me/MP4LINKGENBOT"),
                Ul(
                    Li("Send video file to bot"),
                    Li("Bot: 'File processing.....wait till the link is provided'"),
                    Li("Bot processes to 720p"),
                    Li("Bot sends: '✅ Your 720p video is ready!' + Download URL")
                ),
                cls="section"
            ),
            
            Script("""
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
                                '<div class="status success"><strong>Webhook URL:</strong><br><code>' + 
                                data.webhook_url + '</code></div>';
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
            """)
        ),
        style="""
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .status { 
                padding: 15px; 
                margin: 15px 0; 
                border-radius: 5px; 
                border-left: 4px solid;
            }
            .success { 
                background: #d4edda; 
                color: #155724; 
                border-left-color: #28a745;
            }
            .error { 
                background: #f8d7da; 
                color: #721c24; 
                border-left-color: #dc3545;
            }
            .processing { 
                background: #fff3cd; 
                color: #856404; 
                border-left-color: #ffc107;
            }
            button { 
                padding: 12px 25px; 
                background: #007bff; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                margin: 10px 5px;
                font-size: 16px;
            }
            button:hover { 
                background: #0056b3; 
            }
            button:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            code {
                background: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                display: block;
                word-break: break-all;
                font-family: monospace;
            }
        """
    )

# API Routes
@app.post("/api/set-webhook")
async def api_set_webhook():
    try:
        result = set_webhook()
        return {"success": True, "webhook_url": f"https://{os.environ.get('VERCEL_URL')}/api/webhook", "telegram_response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/webhook-info")
async def api_webhook_info():
    try:
        result = get_webhook_info()
        return {"success": True, "webhook_info": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "timestamp": "2024-01-01T00:00:00Z"}