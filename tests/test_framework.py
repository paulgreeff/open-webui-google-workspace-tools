#!/usr/bin/env python3
"""
Test framework for Google Workspace Tools

This script allows testing all functions without Open-WebUI by loading
credentials and tokens from files that can be copied from Open-WebUI.
"""

import sys
import os
import json
import traceback
from typing import Optional, Dict, Any

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from google_workspace_tools import Tools
except ImportError as e:
    print(f"Error importing google_workspace_tools: {e}")
    print("Make sure google_workspace_tools.py is in the parent directory")
    sys.exit(1)


class TestFramework:
    """Test framework for Google Workspace Tools"""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        """Initialize test framework with credential files"""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.tools = None
        self.setup_complete = False
        
    def load_credentials(self) -> bool:
        """Load credentials and tokens from files"""
        try:
            # Read credentials
            if not os.path.exists(self.credentials_file):
                print(f"❌ Credentials file not found: {self.credentials_file}")
                print("Please copy your credentials JSON from Open-WebUI to this file")
                return False
                
            with open(self.credentials_file, 'r') as f:
                credentials_data = json.load(f)
                
            # Read token if it exists
            token_data = None
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
            
            # Create mock valves object with the data
            class MockValves:
                def __init__(self, creds, token):
                    self.credentials_json = json.dumps(creds)
                    self.enabled_services = "gmail,calendar"
                    self.user_timezone = "Europe/London"
                    self.default_email_count = 20
                    self.default_hours_back = 24
                    self.max_email_content_chars = 2000
                    self.default_event_duration_hours = 1
                    self.max_event_description_chars = 300
                    self.default_calendar_name = ""
                    self.debug_mode = True
                    self.setup_step = ""
                    self.auth_status = ""
                    self.auth_code = ""
                    
                    # Store token data for direct injection
                    self._token_data = token
            
            # Initialize tools
            mock_valves = MockValves(credentials_data, token_data)
            self.tools = Tools()
            self.tools.valves = mock_valves
            
            # If we have token data, inject it directly
            if token_data:
                self._inject_token(token_data)
                
            print("✅ Credentials loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            traceback.print_exc()
            return False
    
    def _inject_token(self, token_data: Dict[str, Any]):
        """Inject token data directly into the tools instance"""
        try:
            # Create the data directory if it doesn't exist
            user_id = "test_user"
            data_dir = f"/tmp/google_tools/{user_id}"
            os.makedirs(data_dir, exist_ok=True)
            
            # Write token file
            token_file = os.path.join(data_dir, "token.json")
            with open(token_file, 'w') as f:
                json.dump(token_data, f)
                
            print("✅ Token data injected successfully")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not inject token data: {e}")
    
    def test_authentication(self) -> bool:
        """Test authentication status"""
        try:
            print("\n📋 Testing authentication...")
            result = self.tools.get_authentication_status()
            print(f"Result: {result}")
            return "authenticated" in result.lower()
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    def run_setup_check(self) -> bool:
        """Run initial setup and checks"""
        if not self.load_credentials():
            return False
            
        if not self.test_authentication():
            print("\n⚠️  Authentication failed. You may need to:")
            print("1. Copy your token.json from Open-WebUI")
            print("2. Or re-authenticate using the main tool")
            return False
            
        self.setup_complete = True
        print("\n✅ Setup complete! Ready to run tests.")
        return True


def create_sample_files():
    """Create sample credential files for user to fill in"""
    credentials_sample = {
        "installed": {
            "client_id": "your-client-id.googleusercontent.com",
            "project_id": "your-project-id", 
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your-client-secret",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    token_sample = {
        "token": "your-access-token",
        "refresh_token": "your-refresh-token", 
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "your-client-id.googleusercontent.com",
        "client_secret": "your-client-secret",
        "scopes": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/calendar"
        ]
    }
    
    print("📁 Creating sample credential files...")
    
    with open("credentials.json.sample", 'w') as f:
        json.dump(credentials_sample, f, indent=2)
        
    with open("token.json.sample", 'w') as f:
        json.dump(token_sample, f, indent=2)
        
    print("✅ Created credentials.json.sample and token.json.sample")
    print("Copy your actual data from Open-WebUI into credentials.json and token.json")


if __name__ == "__main__":
    print("🧪 Google Workspace Tools Test Framework")
    print("=" * 50)
    
    framework = TestFramework()
    
    if not os.path.exists("credentials.json"):
        print("No credentials.json found. Creating sample files...")
        create_sample_files()
        print("\nPlease:")
        print("1. Copy your credentials JSON from Open-WebUI to credentials.json")
        print("2. Copy your token JSON from Open-WebUI to token.json (if available)")
        print("3. Run this script again")
        sys.exit(0)
    
    if framework.run_setup_check():
        print("\n🎉 Test framework ready!")
        print("You can now run specific test files:")
        print("- python test_gmail.py")
        print("- python test_calendar.py") 
        print("- python test_runner.py (interactive)")