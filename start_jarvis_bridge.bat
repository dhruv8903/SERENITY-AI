@echo off
echo Starting Jarvis Bridge Server...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Jarvis Bridge Server on http://localhost:5000
echo.
echo The server will provide these endpoints:
echo - POST /api/chat - Text-based chat with Jarvis AI
echo - POST /api/voice-input - Voice input processing
echo - POST /api/speak - Text-to-speech
echo - GET /api/status - Server status
echo - POST /api/face-auth - Face authentication
echo.
echo Press Ctrl+C to stop the server
echo.

python jarvis_bridge.py

pause 