#!/usr/bin/env python3
"""
Gmail API Authentication Setup Script
This script helps you set up Gmail API authentication for EmailDaemon
"""

import os
import sys
from pathlib import Path

def check_client_secret():
    """Check if client_secret.json exists"""
    client_secret_path = Path("auth/client_secret.json")
    
    if client_secret_path.exists():
        print("✅ client_secret.json found!")
        return True
    else:
        print("❌ client_secret.json not found!")
        print("\n📋 To fix this:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download the JSON file")
        print("6. Rename it to 'client_secret.json'")
        print("7. Place it in: auth/client_secret.json")
        return False

def test_authentication():
    """Test Gmail authentication"""
    try:
        from auth.auth import get_gmail_service
        print("\n🔄 Testing authentication...")
        creds = get_gmail_service()
        
        if creds:
            print("✅ Authentication successful!")
            print("✅ You can now run: python3 main.py")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def main():
    print("🔐 Gmail API Authentication Setup")
    print("=" * 40)
    
    # Check if client_secret.json exists
    if not check_client_secret():
        print("\n⚠️  Please complete the setup steps above and run this script again.")
        return
    
    # Test authentication
    if test_authentication():
        print("\n🎉 Setup complete! You can now run the main application.")
    else:
        print("\n⚠️  Authentication failed. Please check your credentials.")

if __name__ == "__main__":
    main()
