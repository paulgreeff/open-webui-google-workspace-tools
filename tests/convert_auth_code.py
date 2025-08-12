#!/usr/bin/env python3
"""
Helper script to convert auth_code to token.json for testing

If you only have an auth_code from Open-WebUI, this script will
exchange it for proper tokens and save them to token.json.
"""

import json
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


def convert_auth_code_to_tokens(credentials_file: str, auth_code: str):
    """Convert authorization code to token file"""
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        print("Please create credentials.json first")
        return False
    
    try:
        # Load credentials
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
        
        # Set up OAuth2 flow
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar'
        ]
        
        flow = InstalledAppFlow.from_client_config(creds_data, scopes)
        flow.redirect_uri = 'http://localhost'
        
        # Exchange authorization code for tokens
        print("🔄 Exchanging authorization code for tokens...")
        flow.fetch_token(code=auth_code)
        
        # Convert credentials to dictionary format
        creds = flow.credentials
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        
        # Save to token.json
        with open('token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("✅ Token saved successfully to token.json")
        print("🧪 You can now run tests with: python test_runner.py")
        return True
        
    except Exception as e:
        print(f"❌ Error converting auth code: {e}")
        print("\nPossible issues:")
        print("- Auth code may be expired (they expire quickly)")
        print("- Auth code may have already been used")
        print("- Credentials file may be invalid")
        return False


if __name__ == "__main__":
    print("🔄 Auth Code to Token Converter")
    print("=" * 40)
    
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found")
        print("Please create credentials.json first by copying from Open-WebUI")
        exit(1)
    
    auth_code = input("Enter your authorization code from Open-WebUI: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        exit(1)
    
    if convert_auth_code_to_tokens("credentials.json", auth_code):
        print("\n🎉 Success! Token file created.")
    else:
        print("\n💥 Failed to convert auth code.")
        print("\nAlternatives:")
        print("1. Copy token.json directly from Open-WebUI data directory")
        print("2. Get a fresh auth code from Open-WebUI and try again")
        print("3. Complete authentication in Open-WebUI first, then copy token.json")