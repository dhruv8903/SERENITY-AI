#!/usr/bin/env python3
"""
Serenity AI Setup Script
This script helps you configure the AI backend for your Serenity AI system.
"""

import os
import sys

def setup_huggingface_api():
    """Setup Hugging Face API key"""
    print("🤖 Setting up Hugging Face API...")
    print("\n📋 To use the Hugging Face API:")
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Create a free account if you don't have one")
    print("3. Generate a new token (Read access is sufficient)")
    print("4. Copy the token")
    
    api_key = input("\n🔑 Enter your Hugging Face API token (or press Enter to skip): ").strip()
    
    if api_key:
        # Set environment variable for current session
        os.environ['HUGGINGFACE_API_KEY'] = api_key
        
        # Create a .env file for persistence
        with open('.env', 'w') as f:
            f.write(f"HUGGINGFACE_API_KEY={api_key}\n")
        
        print("✅ Hugging Face API key configured!")
        print("💡 To make this permanent, add this line to your shell profile:")
        print(f"   export HUGGINGFACE_API_KEY={api_key}")
        return True
    else:
        print("⏭️  Skipping Hugging Face API setup. You can run this script again later.")
        return False

def setup_hugchat():
    """Setup HugChat cookies"""
    print("\n🍪 Setting up HugChat...")
    print("\n📋 To use HugChat:")
    print("1. Go to https://huggingface.co/chat")
    print("2. Sign in to your account")
    print("3. Open browser developer tools (F12)")
    print("4. Go to Application/Storage > Cookies")
    print("5. Copy all cookies and save them as cookies.json in the serinity/serenity/engine/ folder")
    
    cookies_path = os.path.join('serinity', 'serenity', 'engine', 'cookies.json')
    
    if os.path.exists(cookies_path):
        print(f"✅ HugChat cookies found at {cookies_path}")
        return True
    else:
        print(f"❌ HugChat cookies not found at {cookies_path}")
        print("   You can set this up later by placing your cookies.json file in the correct location.")
        return False

def main():
    print("🌟 Welcome to Serenity AI Setup!")
    print("="*50)
    
    # Check current AI status
    huggingface_key = os.environ.get('HUGGINGFACE_API_KEY')
    if huggingface_key:
        print("✅ Hugging Face API key already configured")
        hf_configured = True
    else:
        hf_configured = setup_huggingface_api()
    
    hugchat_configured = setup_hugchat()
    
    print("\n" + "="*50)
    print("🎯 Configuration Summary:")
    print(f"   Hugging Face API: {'✅ Configured' if hf_configured else '❌ Not configured'}")
    print(f"   HugChat: {'✅ Configured' if hugchat_configured else '❌ Not configured'}")
    
    if hf_configured or hugchat_configured:
        print("\n🚀 You're all set! Your AI backend is configured.")
        print("   Run the server with: python jarvis_bridge.py")
    else:
        print("\n🔄 No AI backends configured, but don't worry!")
        print("   The system will use intelligent fallback responses that work great for mental health support.")
        print("   Run the server with: python jarvis_bridge.py")
    
    print("\n💡 Tips:")
    print("   - Hugging Face API is recommended for the best AI responses")
    print("   - HugChat is free but requires browser cookies")
    print("   - Fallback mode provides excellent mental health support without any setup")

if __name__ == "__main__":
    main()
