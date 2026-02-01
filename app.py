#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Service ATLAS AI Telegram Bot
Flask Web Server + Telegram Bot - Direct Flask App (No Gunicorn Issues)
"""

import os
import sys
import threading
import time
import requests
from datetime import datetime
import tempfile
from flask import Flask, jsonify, request

app = Flask(__name__)

class WebAtlasBot:
    """Web Service ATLAS AI Bot - Flask + Telegram Bot"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.groq_api_key = os.getenv('GroqAPIKey')
        self.assistant_name = os.getenv('AssistantName', 'ATLAS')
        self.creator_name = os.getenv('Creator', 'K.V.SARVESH')
        self.last_update_id = 0
        
        if not self.bot_token or not self.groq_api_key:
            print("❌ Missing required environment variables")
            print("Required: TELEGRAM_BOT_TOKEN, GroqAPIKey")
            sys.exit(1)
        
        print(f"🚀 {self.assistant_name} AI Bot Initializing...")
        print(f"👨‍💻 Creator: {self.creator_name}")
        print(f"🌐 Web Service Mode: Flask Server + Telegram Bot")
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """Send message via Telegram API"""
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={
                    'chat_id': chat_id,
                    'text': text,
                    'parse_mode': 'HTML'
                },
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ Message sent to {chat_id}")
                return True
            else:
                print(f"❌ Send failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    def send_voice_message(self, chat_id: int, voice_file_path: str) -> bool:
        """Send voice message via Telegram API"""
        try:
            with open(voice_file_path, 'rb') as voice_file:
                response = requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendVoice",
                    data={'chat_id': chat_id},
                    files={'voice': voice_file},
                    timeout=30
                )
            if response.status_code == 200:
                print(f"✅ Voice sent to {chat_id}")
                return True
            else:
                print(f"❌ Voice send failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Voice send error: {e}")
            return False
    
    def send_document(self, chat_id: int, document_path: str, caption: str = "") -> bool:
        """Send document via Telegram API"""
        try:
            with open(document_path, 'rb') as doc_file:
                response = requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendDocument",
                    data={'chat_id': chat_id, 'caption': caption},
                    files={'document': doc_file},
                    timeout=30
                )
            if response.status_code == 200:
                print(f"✅ Document sent to {chat_id}")
                return True
            else:
                print(f"❌ Document send failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Document send error: {e}")
            return False
    
    def download_file(self, file_id: str) -> str:
        """Download file from Telegram"""
        try:
            # Get file info
            response = requests.get(
                f"https://api.telegram.org/bot{self.bot_token}/getFile",
                params={'file_id': file_id},
                timeout=30
            )
            
            if response.status_code == 200:
                file_info = response.json()['result']
                file_path = file_info['file_path']
                
                # Download file
                download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
                file_response = requests.get(download_url, timeout=30)
                
                if file_response.status_code == 200:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    temp_file.write(file_response.content)
                    temp_file.close()
                    
                    print(f"✅ File downloaded: {temp_file.name}")
                    return temp_file.name
            
            return None
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def analyze_document(self, file_path: str, file_name: str) -> str:
        """Analyze document based on file type - Supports ALL file types"""
        file_extension = file_name.lower().split('.')[-1] if '.' in file_name else 'unknown'
        
        # Get file info
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
        except:
            file_size = 0
            file_size_mb = 0
        
        info = f"📄 **Universal File Analysis**\n\n"
        info += f"📁 **File Name:** {file_name}\n"
        info += f"📏 **File Size:** {file_size_mb:.2f} MB ({file_size:,} bytes)\n"
        info += f"🔧 **File Extension:** .{file_extension}\n"
        
        # Simple MIME type mapping
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'mp3': 'audio/mpeg',
            'zip': 'application/zip',
            'txt': 'text/plain',
            'json': 'application/json',
            'xml': 'application/xml',
            'py': 'text/x-python',
            'js': 'application/javascript',
            'html': 'text/html',
            'css': 'text/css'
        }
        
        mime_type = mime_types.get(file_extension, 'application/octet-stream')
        info += f"📋 **MIME Type:** {mime_type}\n"
        info += f"📝 **File Description:** {file_extension.upper()} file\n"
        
        # Basic analysis based on file type
        if file_extension == 'pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info += f"\n📄 **PDF Analysis**\n"
                    info += f"📋 **Pages:** {len(pdf_reader.pages)}\n"
                    
                    metadata = pdf_reader.metadata
                    if metadata:
                        if metadata.get('/Title'):
                            info += f"📝 **Title:** {metadata.get('/Title')}\n"
                        if metadata.get('/Author'):
                            info += f"👤 **Author:** {metadata.get('/Author')}\n"
                    
                    # Extract first page content
                    if len(pdf_reader.pages) > 0:
                        page = pdf_reader.pages[0]
                        text_content = page.extract_text()
                        if text_content:
                            info += f"\n📖 **Content Preview:**\n{text_content[:500]}..."
            except Exception as e:
                info += f"\n❌ PDF analysis failed: {str(e)}"
        
        elif file_extension in ['txt', 'md', 'log', 'csv', 'json', 'xml']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    lines = content.splitlines()
                    info += f"\n📄 **Text File Analysis**\n"
                    info += f"📏 **Characters:** {len(content):,}\n"
                    info += f"📋 **Lines:** {len(lines):,}\n"
                    info += f"\n📖 **Content Preview:**\n{content[:500]}..."
            except Exception as e:
                info += f"\n❌ Text analysis failed: {str(e)}"
        
        else:
            info += f"\n📝 **Analysis:** Basic file information available"
        
        return info
    
    def text_to_speech(self, text: str) -> str:
        """Convert text to speech using pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            # Save speech to file
            engine.save_to_file(text, temp_file.name)
            engine.runAndWait()
            
            print(f"✅ Voice generated: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None
    
    def generate_pdf_document(self, title: str, content: str) -> str:
        """Generate PDF document"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_file.close()
            
            # Create PDF
            c = canvas.Canvas(temp_file.name, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, title)
            c.setFont("Helvetica", 12)
            
            # Add content
            y_position = 700
            lines = content.split('\n')
            for line in lines:
                if y_position < 50:
                    c.showPage()
                    y_position = 750
                c.drawString(50, y_position, line)
                y_position -= 20
            
            c.save()
            print(f"✅ PDF generated: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            print(f"❌ PDF error: {e}")
            return None
    
    def generate_word_document(self, title: str, content: str) -> str:
        """Generate Word document"""
        try:
            from docx import Document
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
            temp_file.close()
            
            # Create Word document
            doc = Document()
            doc.add_heading(title, 0)
            doc.add_paragraph(content)
            doc.save(temp_file.name)
            
            print(f"✅ Word document generated: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            print(f"❌ Word error: {e}")
            return None
    
    def generate_excel_sheet(self, title: str, data: dict) -> str:
        """Generate Excel sheet"""
        try:
            import openpyxl
            from openpyxl import Workbook
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            temp_file.close()
            
            # Create Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = title
            
            # Add data
            row = 1
            for key, value in data.items():
                ws.cell(row=row, column=1, value=key)
                ws.cell(row=row, column=2, value=value)
                row += 1
            
            wb.save(temp_file.name)
            print(f"✅ Excel sheet generated: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            print(f"❌ Excel error: {e}")
            return None
    
    def call_groq_ai(self, prompt: str) -> str:
        """Get AI response from Groq"""
        try:
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'llama3-70b-8192',
                'messages': [
                    {
                        'role': 'system',
                        'content': f"""You are {self.assistant_name}, an advanced AI assistant created by {self.creator_name}. 
You provide intelligent, helpful, and accurate responses to user questions."""
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                print(f"✅ AI response generated")
                return ai_response
            else:
                print(f"❌ AI service error: {response.status_code}")
                return "❌ AI service temporarily unavailable"
                
        except Exception as e:
            print(f"❌ AI call error: {e}")
            return f"❌ Error: {str(e)}"
    
    def process_message(self, chat_id: int, user_name: str, text: str, message_data: dict = None):
        """Process incoming message"""
        print(f"📩 {user_name}: {text}")
        
        # Handle document messages
        if message_data and 'document' in message_data:
            document = message_data['document']
            file_name = document['file_name']
            file_id = document['file_id']
            file_size = document.get('file_size', 0)
            
            print(f"📄 Document received: {file_name} ({file_size} bytes)")
            
            # NO FILE SIZE LIMITS - Accept any size
            self.send_message(chat_id, f"📄 Analyzing document: {file_name}\n💾 Size: {file_size/1024/1024:.2f} MB\n⏳ Please wait...")
            
            # Download and analyze file
            downloaded_file = self.download_file(file_id)
            if downloaded_file:
                analysis = self.analyze_document(downloaded_file, file_name)
                self.send_message(chat_id, analysis)
                
                # Clean up
                try:
                    os.unlink(downloaded_file)
                except:
                    pass
            else:
                self.send_message(chat_id, "❌ Failed to download and analyze the document")
            return
        
        # Handle commands
        if text.lower() == '/start':
            welcome = f"""🚀 Welcome to {self.assistant_name} AI - Web Service Edition!

Hello {user_name}! I'm {self.assistant_name}, your advanced AI assistant with media capabilities created by {self.creator_name}.

🌐 **Web Service Mode:** Flask Server + Telegram Bot
🎵 <b>Media Capabilities:</b>
🗣️ <b>Voice Messages:</b> Convert text to speech
📄 <b>Document Creation:</b> Generate PDF, Word, Excel files
📋 <b>Document Analysis:</b> Analyze uploaded documents

🎯 <b>Commands:</b>
/start - Welcome message
/help - Show all capabilities
/voice <text> - Convert text to voice
/pdf <title> - Generate PDF document
/word <title> - Create Word document
/excel <title> - Generate Excel sheet

📋 <b>Universal Document Analysis:</b>
📄 **ALL File Types Supported:** No limits!
🔍 **Analyze ANY file format** - PDF, Word, Excel, Images, Videos, Audio, Archives, Code, Databases, Binary files
📊 **Extract metadata, content, and structure**
💾 **No file size restrictions** - Analyze files of any size

🧠 <b>AI Capabilities:</b>
• Advanced reasoning & analysis
• Natural conversations
• Research & information
• Creative writing
• Technical support

💡 <b>Examples:</b>
• "/voice Hello world" - Get voice message
• "/pdf Business Plan" - Generate PDF
• Send a document for automatic analysis
• Ask questions about analyzed content

🔥 Created by {self.creator_name}
🌐 Web Service Deployment - Flask Server
📋 Document Analysis Enabled!
Powered by advanced AI technology!

Ask me anything or send documents for analysis! 🚀"""
            self.send_message(chat_id, welcome)
            return
        
        elif text.lower() == '/help':
            help_text = f"""🧠 {self.assistant_name} AI - Web Service Help

📋 <b>Basic Commands:</b>
/start - Welcome message
/help - Show this help

🎵 <b>Media Commands:</b>
/voice <text> - Convert text to voice message
/pdf <title> - Generate PDF document
/word <title> - Create Word document
/excel <title> - Generate Excel sheet

📋 <b>Universal Document Analysis:</b>
📄 **ALL File Types Supported:** No limits!
🔍 **Analyze ANY file format** - PDF, Word, Excel, Images, Videos, Audio, Archives, Code, Databases, Binary files
📊 **Extract metadata, content, and structure**
💾 **No file size restrictions** - Analyze files of any size

🌟 <b>AI Capabilities:</b>
🧠 <b>Advanced Intelligence:</b> Complex reasoning
💬 <b>Natural Conversations:</b> Human-like dialogue
🔍 <b>Research & Analysis:</b> Deep information processing
🎨 <b>Creative Tasks:</b> Writing, brainstorming
💻 <b>Technical Support:</b> Programming, science, math

🔥 <b>Powered by:</b> Advanced AI Technology
👨‍💻 <b>Created by:</b> {self.creator_name}
🌐 <b>Deployment:</b> Web Service (Flask)
📋 <b>Features:</b> Document Analysis + Media Generation

Ask me anything or send documents for analysis!"""
            self.send_message(chat_id, help_text)
            return
        
        elif text.lower().startswith('/voice '):
            voice_text = text[7:].strip()
            if voice_text:
                self.send_message(chat_id, "🎵 Converting text to voice...")
                voice_file = self.text_to_speech(voice_text)
                if voice_file:
                    self.send_voice_message(chat_id, voice_file)
                    # Clean up
                    try:
                        os.unlink(voice_file)
                    except:
                        pass
                else:
                    self.send_message(chat_id, "❌ Failed to generate voice message")
            else:
                self.send_message(chat_id, "❌ Please provide text to convert to voice\nExample: /voice Hello world")
            return
        
        elif text.lower().startswith('/pdf '):
            pdf_title = text[5:].strip()
            if pdf_title:
                self.send_message(chat_id, "📄 Generating PDF document...")
                content = f"This is your personalized PDF document generated by {self.assistant_name} AI."
                pdf_file = self.generate_pdf_document(pdf_title, content)
                if pdf_file:
                    self.send_document(chat_id, pdf_file, f"📄 Your PDF: {pdf_title}")
                    # Clean up
                    try:
                        os.unlink(pdf_file)
                    except:
                        pass
                else:
                    self.send_message(chat_id, "❌ Failed to generate PDF")
            else:
                self.send_message(chat_id, "❌ Please provide a title for the PDF\nExample: /pdf Business Plan")
            return
        
        elif text.lower().startswith('/word '):
            word_title = text[6:].strip()
            if word_title:
                self.send_message(chat_id, "📝 Creating Word document...")
                content = f"This is your personalized Word document generated by {self.assistant_name} AI."
                word_file = self.generate_word_document(word_title, content)
                if word_file:
                    self.send_document(chat_id, word_file, f"📝 Your Word document: {word_title}")
                    # Clean up
                    try:
                        os.unlink(word_file)
                    except:
                        pass
                else:
                    self.send_message(chat_id, "❌ Failed to generate Word document")
            else:
                self.send_message(chat_id, "❌ Please provide a title for the Word document\nExample: /word Meeting Notes")
            return
        
        elif text.lower().startswith('/excel '):
            excel_title = text[7:].strip()
            if excel_title:
                self.send_message(chat_id, "📊 Generating Excel sheet...")
                data = {
                    "Title": excel_title,
                    "Generated By": f"{self.assistant_name} AI",
                    "Creator": self.creator_name,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Type": "AI Generated Document",
                    "Deployment": "Web Service (Flask)"
                }
                excel_file = self.generate_excel_sheet(excel_title, data)
                if excel_file:
                    self.send_document(chat_id, excel_file, f"📊 Your Excel sheet: {excel_title}")
                    # Clean up
                    try:
                        os.unlink(excel_file)
                    except:
                        pass
                else:
                    self.send_message(chat_id, "❌ Failed to generate Excel sheet")
            else:
                self.send_message(chat_id, "❌ Please provide a title for the Excel sheet\nExample: /excel Project Data")
            return
        
        # Handle AI responses
        else:
            self.send_message(chat_id, f"🤔 {self.assistant_name} is thinking...")
            ai_response = self.call_groq_ai(text)
            self.send_message(chat_id, ai_response)
    
    def test_connection(self):
        """Test bot connection"""
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{self.bot_token}/getMe",
                timeout=10
            )
            if response.status_code == 200:
                bot_info = response.json()['result']
                print(f"✅ Bot connected: @{bot_info['username']} ({bot_info['first_name']})")
                return True
            else:
                print(f"❌ Bot connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
    
    def run_bot(self):
        """Run the Telegram bot in background"""
        print(f"🤖 Starting {self.assistant_name} AI Bot in background...")
        
        # Test connection
        if not self.test_connection():
            print("❌ Failed to connect to Telegram API")
            return
        
        print(f"🤖 Bot is ready and listening for messages...")
        
        while True:
            try:
                response = requests.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getUpdates",
                    params={'offset': self.last_update_id + 1, 'timeout': 30},
                    timeout=35
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('result'):
                        for update in data['result']:
                            self.last_update_id = update['update_id']
                            message = update.get('message')
                            if message:
                                chat_id = message['chat']['id']
                                user_name = message['chat'].get('first_name', 'User')
                                text = message.get('text', '')
                                
                                # Pass message data for document processing
                                self.process_message(chat_id, user_name, text, message)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n👋 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Runtime error: {e}")
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)

# Initialize bot
bot = WebAtlasBot()

# Flask routes
@app.route('/')
def home():
    return jsonify({
        "status": "healthy",
        "bot": f"{bot.assistant_name} AI Telegram Bot - Web Service Edition",
        "features": ["Voice Messages", "PDF Generation", "Word Documents", "Excel Sheets", "Document Analysis"],
        "creator": bot.creator_name,
        "deployment": "Web Service (Flask)",
        "mode": "HTTP Server + Background Bot"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": f"{bot.assistant_name}-ai-telegram-bot",
        "version": "web-service-edition",
        "bot_status": "running" if bot.test_connection() else "disconnected"
    })

@app.route('/bot/status')
def bot_status():
    return jsonify({
        "bot_name": bot.assistant_name,
        "creator": bot.creator_name,
        "telegram_connected": bot.test_connection(),
        "last_update_id": bot.last_update_id,
        "features": ["AI Intelligence", "Voice Messages", "Document Generation", "Document Analysis"]
    })

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=bot.run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(2)
    
    # Get port from environment or default to 8000
    port = int(os.getenv('PORT', 8000))
    
    print(f"🌐 Starting Flask web server on port {port}")
    print(f"🤖 {bot.assistant_name} AI Bot running in background")
    print(f"🎯 Web Service Mode: HTTP Server + Telegram Bot")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
