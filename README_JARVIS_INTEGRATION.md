# Jarvis AI Integration with Serenity Website

This integration connects your Serenity AI website chatbot to the powerful Jarvis AI backend, providing advanced voice commands, AI conversations, and system control capabilities.

## 🚀 Features

### Jarvis AI Capabilities
- **AI Chatbot**: Powered by HugChat for intelligent conversations
- **Voice Recognition**: Speech-to-text using Google Speech Recognition
- **Text-to-Speech**: Natural voice responses
- **System Control**: Open applications and websites
- **YouTube Integration**: Play music and videos
- **Contact Management**: Send messages, make calls via WhatsApp
- **Face Authentication**: Secure login with face recognition
- **Hotword Detection**: Wake with "serenity" or "alexa"

### Web Integration
- **Real-time Chat**: Connect to Jarvis AI through web interface
- **Voice Input**: Use microphone for voice commands
- **Status Monitoring**: Check connection status
- **Fallback Mode**: Works even when Jarvis is offline

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Microphone** for voice input
3. **Speakers** for voice output
4. **Webcam** (optional, for face authentication)

## 🛠️ Installation

### Option 1: Quick Start (Windows)
1. Double-click `start_jarvis_bridge.bat`
2. The script will automatically install dependencies and start the server

### Option 2: Manual Installation
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Jarvis bridge server:
   ```bash
   python jarvis_bridge.py
   ```

## 🔧 Configuration

### HugChat Setup (for AI conversations)
1. Get your HugChat cookies from https://huggingface.co/chat
2. Update the cookies in `serinity/serenity/engine/cookies.json`

### Face Authentication Setup
1. Run the face training script:
   ```bash
   cd serinity/serenity/engine/auth
   python trainer.py
   ```

### Contact Management
1. Add contacts to the database in `serinity/serenity/jarvis.db`

## 🌐 Usage

### Starting the System
1. **Start Jarvis Bridge**: Run `start_jarvis_bridge.bat` or `python jarvis_bridge.py`
2. **Open Website**: Open `MAin.html` in your browser
3. **Navigate to Chatbot**: Click on "Chatbot" in the navigation

### Using the Chatbot
1. **Text Chat**: Type messages in the input field
2. **Voice Input**: Click the microphone button (🎤) for voice commands
3. **Connection Status**: Check the green/red indicator for Jarvis connection

### Available Commands
- **General Chat**: "Hello", "How are you?", "Tell me a joke"
- **Open Applications**: "Open notepad", "Open chrome"
- **YouTube**: "Play despacito on youtube"
- **Contacts**: "Send message to John", "Call Sarah"
- **System**: "What time is it?", "Open calculator"

## 🔌 API Endpoints

The Jarvis bridge provides these REST API endpoints:

- `POST /api/chat` - Send text message to Jarvis AI
- `POST /api/voice-input` - Process voice input
- `POST /api/speak` - Convert text to speech
- `GET /api/status` - Check server status
- `POST /api/face-auth` - Face authentication

## 🐛 Troubleshooting

### Common Issues

1. **"Not connected to Jarvis"**
   - Make sure `jarvis_bridge.py` is running
   - Check if port 5000 is available
   - Verify Python dependencies are installed

2. **Voice input not working**
   - Check microphone permissions
   - Ensure PyAudio is installed correctly
   - Try running as administrator

3. **AI responses not working**
   - Verify HugChat cookies are set up
   - Check internet connection
   - Review error logs in console

4. **Face authentication issues**
   - Ensure webcam is connected
   - Run face training script
   - Check OpenCV installation

### Error Logs
Check the console output for detailed error messages when running the bridge server.

## 📁 File Structure

```
Website/
├── chatbot.html              # Updated chatbot with Jarvis integration
├── jarvis_bridge.py          # Flask server bridging web to Jarvis
├── requirements.txt          # Python dependencies
├── start_jarvis_bridge.bat   # Windows startup script
├── serinity/serenity/        # Original Jarvis system
│   ├── engine/              # Jarvis core engine
│   ├── main.py              # Jarvis main application
│   └── run.py               # Jarvis runner
└── [other website files]
```

## 🔒 Security Notes

- The bridge server runs on localhost only
- Face authentication data is stored locally
- HugChat cookies should be kept secure
- No sensitive data is transmitted over the web interface

## 🚀 Advanced Features

### Custom Commands
Add custom commands by modifying `jarvis_bridge.py` in the `process_command()` function.

### Voice Wake Word
The original Jarvis system supports wake words "serenity" and "alexa". This can be integrated with the web interface.

### Database Integration
Connect to the existing Jarvis database for contact management and user preferences.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify Python version compatibility

## 🔄 Updates

To update the integration:
1. Stop the bridge server
2. Update the Python files
3. Restart the server
4. Refresh the web page

---

**Note**: This integration maintains the original Jarvis functionality while providing a modern web interface. The web interface serves as a frontend to the powerful Jarvis AI backend. 