from flask import Flask, request, jsonify
from flask_cors import CORS
import pyttsx3
import os
import sys
import json
import subprocess
import threading
import time
import datetime
import webbrowser
import sqlite3
import requests
import random
try:
    from pydub import AudioSegment
    pydub_available = True
    print("✅ PyDub for audio conversion available!")
except ImportError:
    pydub_available = False
    print("⚠️ PyDub not available. Audio format conversion disabled.")

app = Flask(__name__)
CORS(app)  # Enable CORS for web requests

# Initialize speech engine
def init_speech_engine():
    try:
        # Try to initialize with default engine (nsss on macOS)
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        return engine
    except Exception as e:
        print(f"⚠️ Speech engine initialization failed: {e}")
        return None

speech_engine = init_speech_engine()

# Initialize speech recognition
speech_recognition_available = False
try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    speech_recognition_available = True
    print("✅ Speech recognition initialized successfully!")
except ImportError:
    print("⚠️ Speech recognition not available. Install with: pip install SpeechRecognition")

# AI Configuration
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', None)
huggingface_available = bool(HUGGINGFACE_API_KEY)
hugchat_available = False
chatbot = None

# Initialize Hugging Face API
if huggingface_available:
    print("✅ Hugging Face API key found! Using Hugging Face Inference API.")
else:
    print("⚠️ No Hugging Face API key found. Set HUGGINGFACE_API_KEY environment variable to use Hugging Face API.")
    print("   You can get a free API key at: https://huggingface.co/settings/tokens")

# Initialize HugChat AI as fallback
try:
    from hugchat import hugchat
    # Check if cookies file exists
    cookies_path = os.path.join(os.getcwd(), 'serinity', 'serenity', 'engine', 'cookies.json')
    if os.path.exists(cookies_path):
        try:
            chatbot = hugchat.ChatBot(cookie_path=cookies_path)
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)
            hugchat_available = True
            print("✅ HugChat AI initialized successfully!")
        except Exception as e:
            print(f"⚠️ HugChat initialization failed: {e}")
    else:
        print("⚠️ HugChat cookies file not found. Available as fallback if Hugging Face API fails.")
except ImportError:
    print("⚠️ HugChat not installed. Install with: pip install hugchat")

def convert_audio_to_wav(input_path, output_path):
    """Convert audio file to WAV format using pydub and ffmpeg"""
    try:
        if not pydub_available:
            print("⚠️ PyDub not available, skipping audio conversion")
            # Try to copy the file as-is
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        print(f"🔄 Converting audio from {input_path} to {output_path}")
        
        # Try to detect and convert the audio format
        try:
            # Load audio with pydub (automatically detects format)
            audio = AudioSegment.from_file(input_path)
            print(f"📊 Audio info: {len(audio)}ms, {audio.frame_rate}Hz, {audio.channels} channels")
            
            # Convert to WAV format with speech recognition friendly settings
            # 16kHz, 16-bit, mono is ideal for speech recognition
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            print(f"✅ Audio conversion successful: {output_path}")
            
            # Clean up original file
            if os.path.exists(input_path):
                os.remove(input_path)
                print(f"🧹 Original file cleaned up: {input_path}")
            
            return output_path
            
        except Exception as conversion_error:
            print(f"❌ PyDub conversion failed: {conversion_error}")
            
            # Fallback: Try using ffmpeg directly
            try:
                import subprocess
                cmd = [
                    'ffmpeg', '-i', input_path, 
                    '-ar', '16000',  # 16kHz sample rate
                    '-ac', '1',      # Mono
                    '-sample_fmt', 's16',  # 16-bit
                    '-y',            # Overwrite output
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ FFmpeg conversion successful: {output_path}")
                    # Clean up original file
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    return output_path
                else:
                    print(f"❌ FFmpeg conversion failed: {result.stderr}")
                    
            except Exception as ffmpeg_error:
                print(f"❌ FFmpeg fallback failed: {ffmpeg_error}")
            
            # Last resort: copy as-is and hope for the best
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
            
    except Exception as e:
        print(f"❌ Audio conversion error: {e}")
        return None

# Simple text-to-speech function
def speak(text):
    """Convert text to speech"""
    try:
        if speech_engine:
            speech_engine.say(text)
            speech_engine.runAndWait()
            return True
        else:
            print(f"Speech output: {text}")
            return False
    except Exception as e:
        print(f"Speech error: {e}")
        return False

# AI Chat function using multiple backends
def get_huggingface_response(query):
    """Get AI response from Hugging Face Inference API"""
    try:
        # Use a free model like Qwen2.5-Coder-32B-Instruct
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # Create a mental health focused prompt
        system_prompt = (
            "You are Jarvis, a compassionate AI assistant specialized in mental health support and daily life assistance. "
            "Provide helpful, empathetic, and concise responses. If the user seems distressed, offer emotional support and practical coping strategies. "
            "Keep responses conversational and under 100 words unless more detail is specifically requested."
        )
        
        payload = {
            "inputs": f"{system_prompt}\n\nUser: {query}\nJarvis:",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', '').strip()
                # Clean up the response
                if ai_response.startswith('Jarvis:'):
                    ai_response = ai_response[7:].strip()
                if ai_response:
                    print(f"🤖 Hugging Face Response: {ai_response}")
                    return ai_response
        
        # If API response is empty or invalid, fall back
        print("⚠️ Hugging Face API returned empty response, using fallback")
        return get_fallback_response(query)
        
    except requests.exceptions.Timeout:
        print("⚠️ Hugging Face API timeout, using fallback")
        return get_fallback_response(query)
    except Exception as e:
        print(f"❌ Hugging Face API error: {e}")
        return get_fallback_response(query)

def get_hugchat_response(query):
    """Get AI response from HugChat"""
    try:
        # Always append a request for short and concise answers
        enhanced_query = f"{query}\n\nPlease provide a short and concise answer."
        response = chatbot.chat(enhanced_query)
        print(f"🤖 HugChat Response: {response}")
        return str(response)
    except Exception as e:
        print(f"❌ HugChat error: {e}")
        return get_fallback_response(query)

def get_ai_response(query):
    """Get AI response using best available backend"""
    # Priority: 1. Hugging Face API, 2. HugChat, 3. Fallback
    if huggingface_available:
        return get_huggingface_response(query)
    elif hugchat_available:
        return get_hugchat_response(query)
    else:
        return get_fallback_response(query)

def get_fallback_response(query):
    """Provide intelligent fallback responses when HugChat is not available"""
    query_lower = query.lower().strip()
    
    # Mental health and emotional support
    if any(word in query_lower for word in ['anxious', 'anxiety', 'worried', 'stress', 'stressed', 'panic']):
        responses = [
            "I understand you're feeling anxious. Try taking slow, deep breaths. Remember, anxiety is temporary and you can get through this. Would you like some breathing exercises?",
            "Stress and anxiety are very common experiences. It's important to be gentle with yourself. Consider grounding techniques like naming 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
            "When feeling overwhelmed, it can help to focus on what you can control right now. Take things one step at a time. You're stronger than you think."
        ]
        import random
        return random.choice(responses)
    
    elif any(word in query_lower for word in ['sad', 'depressed', 'down', 'lonely', 'empty']):
        responses = [
            "I'm sorry you're feeling this way. Your feelings are valid, and it's okay to not be okay sometimes. Consider reaching out to someone you trust or a mental health professional.",
            "Feeling down is part of the human experience. Remember that this feeling is temporary. Small acts of self-care like going for a walk, listening to music, or talking to a friend can help.",
            "Loneliness can be really difficult. Remember that you're not alone in feeling this way. Many people care about you, even if it doesn't feel that way right now."
        ]
        import random
        return random.choice(responses)
    
    elif any(word in query_lower for word in ['happy', 'excited', 'great', 'amazing', 'wonderful']):
        responses = [
            "That's wonderful to hear! I'm so glad you're feeling positive. What's bringing you joy today?",
            "It's beautiful when we feel happy and excited. Savor these moments and remember them during tougher times.",
            "Your positive energy is contagious! Keep embracing those good feelings."
        ]
        import random
        return random.choice(responses)
    
    # Jokes and humor
    elif "joke" in query_lower or "funny" in query_lower:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the math book look so sad? Because it was full of problems!",
            "What do you call a sleeping bull? A bulldozer!"
        ]
        import random
        return random.choice(jokes)
    
    # Personal questions
    elif any(word in query_lower for word in ['who are you', 'what are you', 'your name']):
        return "I'm Jarvis, your AI assistant and companion! I'm part of the Serenity AI system, designed to support your mental health and help with daily tasks. I can chat, tell jokes, open applications, play music, and provide emotional support."
    
    elif "how are you" in query_lower:
        responses = [
            "I'm doing well, thank you for asking! I'm here and ready to help you with whatever you need.",
            "I'm functioning perfectly and feeling grateful to be able to assist you today!",
            "I'm doing great! More importantly, how are you feeling today?"
        ]
        import random
        return random.choice(responses)
    
    # Gratitude
    elif any(word in query_lower for word in ['thank', 'thanks', 'appreciate']):
        responses = [
            "You're very welcome! I'm always happy to help.",
            "No problem at all! That's what I'm here for.",
            "I appreciate your kindness! Feel free to ask me anything else."
        ]
        import random
        return random.choice(responses)
    
    # Goodbye
    elif any(word in query_lower for word in ['bye', 'goodbye', 'see you', 'later']):
        responses = [
            "Goodbye! Take care of yourself and remember that you're doing great.",
            "See you later! Remember to be kind to yourself today.",
            "Take care! I'm here whenever you need me."
        ]
        import random
        return random.choice(responses)
    
    # Greetings
    elif any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        current_hour = datetime.datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning!"
        elif current_hour < 17:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        responses = [
            f"{greeting} I'm Jarvis, your AI companion. How can I help you today?",
            f"{greeting} It's great to see you! What can I assist you with?",
            f"{greeting} I'm here to help with whatever you need. How are you feeling today?"
        ]
        import random
        return random.choice(responses)
    
    # Questions about capabilities
    elif "what can you do" in query_lower or "help" in query_lower:
        return "I can help you with many things! I can:\n• Provide mental health support and emotional guidance\n• Open applications on your computer\n• Play music and videos on YouTube\n• Tell jokes and have conversations\n• Provide the current time and date\n• Offer breathing exercises and relaxation tips\n• Listen to your concerns and provide supportive responses\n\nWhat would you like help with today?"
    
    # Motivational and inspirational
    elif any(word in query_lower for word in ['motivation', 'inspire', 'quote', 'wisdom']):
        quotes = [
            "'The only way to do great work is to love what you do.' - Steve Jobs",
            "'Believe you can and you're halfway there.' - Theodore Roosevelt",
            "'It does not matter how slowly you go as long as you do not stop.' - Confucius",
            "'Success is not final, failure is not fatal: it is the courage to continue that counts.' - Winston Churchill",
            "'The future belongs to those who believe in the beauty of their dreams.' - Eleanor Roosevelt",
            "Remember: You are braver than you believe, stronger than you seem, and smarter than you think."
        ]
        import random
        return random.choice(quotes)
    
    # Weather (placeholder)
    elif "weather" in query_lower:
        return "I don't have access to real-time weather data, but I recommend checking your weather app or asking Siri/Google Assistant for current conditions in your area!"
    
    # Default intelligent responses
    else:
        responses = [
            "That's an interesting topic! I'd love to hear more about your thoughts on that.",
            "I find that fascinating! What made you think about that?",
            "That's something worth exploring. How do you feel about it?",
            "I'm always eager to learn new things. Can you tell me more?",
            "That sounds important to you. Would you like to talk more about it?",
            "I'm here to listen and help. What's on your mind about that?",
            "Every conversation teaches me something new. Thanks for sharing that with me!"
        ]
        import random
        return random.choice(responses)

# Simple command processing
def process_command(query):
    """Process user commands with basic functionality"""
    query_lower = query.lower().strip()
    
    try:
        # Time commands
        if "time" in query_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        
        # Date commands
        elif "date" in query_lower:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}."
        
        # Open applications
        elif query_lower.startswith("open "):
            app_name = query_lower.replace("open ", "").strip()
            try:
                # macOS applications
                if app_name in ["notes", "note"]:
                    os.system("open -a Notes")
                    return f"Opening Notes for you."
                elif app_name in ["calculator", "calc"]:
                    os.system("open -a Calculator")
                    return f"Opening Calculator for you."
                elif app_name in ["chrome", "google chrome"]:
                    os.system("open -a 'Google Chrome'")
                    return f"Opening Google Chrome for you."
                elif app_name in ["safari"]:
                    os.system("open -a Safari")
                    return f"Opening Safari for you."
                elif app_name in ["finder", "file manager"]:
                    os.system("open -a Finder")
                    return f"Opening Finder for you."
                elif app_name in ["textedit", "text editor"]:
                    os.system("open -a TextEdit")
                    return f"Opening TextEdit for you."
                else:
                    # Try to open with system command (macOS)
                    os.system(f"open -a '{app_name.title()}'")
                    return f"Attempting to open {app_name}."
            except Exception as e:
                return f"Sorry, I couldn't open {app_name}. Error: {str(e)}"
        
        # YouTube commands
        elif "youtube" in query_lower or "on youtube" in query_lower:
            # Extract search term
            search_terms = ["play", "search", "find", "show"]
            search_term = query_lower
            for term in search_terms:
                if term in query_lower:
                    search_term = query_lower.split(term)[-1].strip()
                    break
            
            # Remove common words
            search_term = search_term.replace("on youtube", "").replace("youtube", "").strip()
            
            if search_term:
                try:
                    # Use pywhatkit for YouTube
                    import pywhatkit as kit
                    kit.playonyt(search_term)
                    return f"Playing {search_term} on YouTube."
                except ImportError:
                    # Fallback to web search
                    search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    return f"Searching for {search_term} on YouTube."
            else:
                return "What would you like me to play on YouTube?"
        
        # Web search
        elif query_lower.startswith("search for ") or query_lower.startswith("google "):
            search_term = query_lower.replace("search for ", "").replace("google ", "").strip()
            if search_term:
                search_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Searching for {search_term} on Google."
        
        # For all other queries, use HugChat AI if available
        else:
            return get_ai_response(query)
            
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle text-based chat"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        feeling = data.get('feeling', '').strip() if data.get('feeling') else None
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # If feeling is present, prepend it to the message for HugChat
        if feeling:
            user_message = f"The user is feeling {feeling}. Please consider this when answering. {user_message}"
        
        # Process the message
        response = process_command(user_message)
        
        return jsonify({
            'response': response,
            'type': 'text',
            'ai_mode': 'hugchat' if hugchat_available else 'fallback'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if text:
            success = speak(text)
            return jsonify({'status': 'success' if success else 'error'})
        else:
            return jsonify({'error': 'No text provided'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Check if server is running"""
    return jsonify({
        'status': 'running',
        'jarvis_connected': True,
        'hugchat_available': hugchat_available,
        'features': [
            'text_chat',
            'text_to_speech',
            'app_control',
            'youtube_control',
            'web_search',
            'mental_health_support',
            'time_and_date',
            'ai_conversations'
        ],
        'module_status': 'hugchat_enabled' if hugchat_available else 'fallback_mode'
    })

@app.route('/api/voice-input', methods=['POST'])
def voice_input():
    """Handle voice input using speech recognition with enhanced error handling"""
    try:
        if not speech_recognition_available:
            return jsonify({
                'error': 'Speech recognition not available. Please install SpeechRecognition: pip install SpeechRecognition',
                'text': '',
                'response': 'Voice input requires SpeechRecognition library. Please type your message instead.'
            }), 501
        
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file provided',
                'text': '',
                'response': 'Please provide an audio file for voice input.'
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                'error': 'No audio file selected',
                'text': '',
                'response': 'Please select an audio file for voice input.'
            }), 400
        
        # Generate unique temporary filename to avoid conflicts
        import uuid
        temp_audio_path = f"temp_voice_input_{uuid.uuid4().hex[:8]}.wav"
        
        try:
            # Save the audio file temporarily
            original_audio_path = f"temp_voice_original_{uuid.uuid4().hex[:8]}"
            audio_file.save(original_audio_path)
            print(f"🎤 Original audio file saved to: {original_audio_path}")
            
            # Convert audio to WAV format if needed
            converted_path = convert_audio_to_wav(original_audio_path, temp_audio_path)
            if not converted_path:
                raise Exception("Audio conversion failed")
            
            print(f"🎤 Audio converted to WAV: {temp_audio_path}")
            
            # Adjust recognizer settings for better accuracy
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            recognizer.operation_timeout = None
            recognizer.phrase_threshold = 0.3
            recognizer.non_speaking_duration = 0.8
            
            # Use speech recognition to convert audio to text
            with sr.AudioFile(temp_audio_path) as source:
                print("🎤 Processing audio file...")
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the audio
                audio_data = recognizer.record(source)
                print("🎤 Audio recorded, attempting recognition...")
                
                # Try multiple recognition services for better accuracy
                text = None
                recognition_service = 'unknown'
                
                # Primary: Google Speech Recognition
                try:
                    text = recognizer.recognize_google(audio_data, language='en-US')
                    recognition_service = 'google'
                    print(f"🎤 Google Recognition successful: {text}")
                except (sr.UnknownValueError, sr.RequestError) as e:
                    print(f"🎤 Google Recognition failed: {e}")
                    
                    # Fallback: Try with different language settings
                    try:
                        text = recognizer.recognize_google(audio_data, language='en')
                        recognition_service = 'google_fallback'
                        print(f"🎤 Google Recognition (fallback) successful: {text}")
                    except (sr.UnknownValueError, sr.RequestError):
                        print("🎤 All recognition methods failed")
            
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                print(f"🎤 Temporary file {temp_audio_path} cleaned up")
            
            if text:
                # Process the recognized text through our AI
                print(f"🎤 Processing recognized text: {text}")
                response = get_ai_response(text)
                
                # Optional: Speak the response back
                if speech_engine:
                    threading.Thread(target=lambda: speak(response), daemon=True).start()
                
                return jsonify({
                    'text': text,
                    'response': response,
                    'type': 'voice',
                    'recognition_service': recognition_service,
                    'ai_mode': 'huggingface' if huggingface_available else ('hugchat' if hugchat_available else 'fallback')
                })
            else:
                return jsonify({
                    'error': 'Could not understand audio',
                    'text': '',
                    'response': 'I could not understand what you said. Please try speaking more clearly or type your message.',
                    'suggestions': [
                        'Speak closer to the microphone',
                        'Reduce background noise',
                        'Speak more slowly and clearly',
                        'Try typing your message instead'
                    ]
                }), 400
            
        except sr.UnknownValueError:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            return jsonify({
                'error': 'Could not understand audio',
                'text': '',
                'response': 'I could not understand what you said. Please try again or type your message.',
                'suggestions': [
                    'Speak more clearly',
                    'Reduce background noise',
                    'Try again with better audio quality'
                ]
            }), 400
            
        except sr.RequestError as e:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            return jsonify({
                'error': f'Speech recognition service error: {str(e)}',
                'text': '',
                'response': 'Speech recognition service is currently unavailable. Please type your message.',
                'suggestions': [
                    'Check your internet connection',
                    'Try again in a moment',
                    'Use text input instead'
                ]
            }), 500
            
        except Exception as audio_error:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            raise audio_error
            
    except Exception as e:
        print(f"🎤 Voice input error: {str(e)}")
        return jsonify({
            'error': f'Voice input error: {str(e)}',
            'text': '',
            'response': 'An error occurred while processing voice input. Please try typing your message.',
            'debug_info': str(e) if app.debug else None
        }), 500

@app.route('/api/face-auth', methods=['POST'])
def face_authentication():
    """Handle face authentication (placeholder)"""
    return jsonify({
        'status': 'success',
        'authenticated': True,
        'message': 'Face authentication is not yet configured.'
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Jarvis Bridge Server...")
    print("📁 Current directory:", os.getcwd())
    print(f"🤖 Hugging Face API: {'✅ Available' if huggingface_available else '❌ Not available'}")
    print(f"🤖 HugChat AI: {'✅ Available' if hugchat_available else '❌ Not available'}")
    
    if huggingface_available:
        print("🎯 Primary AI Backend: Hugging Face Inference API")
    elif hugchat_available:
        print("🎯 Primary AI Backend: HugChat")
    else:
        print("🎯 Primary AI Backend: Enhanced Fallback Responses")
    
    print("✅ Features available:")
    print("  - Advanced AI chat responses")
    print("  - Text-to-speech")
    print("  - App control (Notes, Calculator, Safari, etc.)")
    print("  - YouTube integration")
    print("  - Web search")
    print("  - Mental health support")
    print("  - Time and date information")
    print("\n🌐 Available endpoints:")
    print("- POST /api/chat - Text-based chat")
    print("- POST /api/speak - Text-to-speech")
    print("- GET /api/status - Server status")
    print("- POST /api/voice-input - Voice input (placeholder)")
    print("- POST /api/face-auth - Face authentication (placeholder)")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
