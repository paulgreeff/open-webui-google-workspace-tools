#!/usr/bin/env python3
"""
Gmail function tests for Google Workspace Tools
"""

import sys
import os
from test_framework import TestFramework


class GmailTests:
    """Gmail function test suite"""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.tools = framework.tools
        
    def test_get_recent_emails(self):
        """Test getting recent emails"""
        print("\n📧 Testing get_recent_emails()...")
        try:
            result = self.tools.get_recent_emails(count=5, hours_back=24)
            print(f"✅ Success: Found emails")
            print(f"Preview: {result[:200]}..." if len(result) > 200 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_search_emails(self):
        """Test email search functionality"""
        print("\n🔍 Testing search_emails()...")
        try:
            # Search for any emails (broad search)
            result = self.tools.search_emails("from:me", max_results=3)
            print(f"✅ Success: Search completed")
            print(f"Preview: {result[:200]}..." if len(result) > 200 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_email_content(self):
        """Test getting full email content"""
        print("\n📄 Testing get_email_content()...")
        try:
            # First get a recent email to test with
            recent = self.tools.get_recent_emails(count=1, hours_back=168)  # 1 week
            
            if "ID:" not in recent:
                print("⚠️  No emails found to test content retrieval")
                return False
                
            # Extract email ID from the result
            import re
            id_match = re.search(r'ID: ([a-zA-Z0-9]+)', recent)
            if not id_match:
                print("⚠️  Could not extract email ID from recent emails")
                return False
                
            email_id = id_match.group(1)
            print(f"Testing with email ID: {email_id}")
            
            result = self.tools.get_email_content(email_id)
            print(f"✅ Success: Retrieved email content")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_draft(self):
        """Test creating email drafts"""
        print("\n✏️  Testing create_draft()...")
        try:
            result = self.tools.create_draft(
                to="test@example.com",
                subject="Test Draft - Please Ignore",
                body="This is a test draft created by the Google Workspace Tools test suite. Please ignore."
            )
            print(f"✅ Success: Draft created")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_draft_reply(self):
        """Test creating reply drafts"""
        print("\n↩️  Testing create_draft_reply()...")
        try:
            # First get a recent email to reply to
            recent = self.tools.get_recent_emails(count=1, hours_back=168)  # 1 week
            
            if "ID:" not in recent:
                print("⚠️  No emails found to test reply creation")
                return False
                
            # Extract email ID
            import re
            id_match = re.search(r'ID: ([a-zA-Z0-9]+)', recent)
            if not id_match:
                print("⚠️  Could not extract email ID")
                return False
                
            email_id = id_match.group(1)
            print(f"Creating reply to email ID: {email_id}")
            
            result = self.tools.create_draft_reply(
                message_id=email_id,
                body="This is a test reply created by the Google Workspace Tools test suite. Please ignore."
            )
            print(f"✅ Success: Reply draft created")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Gmail tests"""
        print("🧪 Running Gmail Test Suite")
        print("=" * 40)
        
        if not self.framework.setup_complete:
            print("❌ Framework not set up properly")
            return False
        
        tests = [
            ("Recent Emails", self.test_get_recent_emails),
            ("Search Emails", self.test_search_emails),
            ("Email Content", self.test_get_email_content),
            ("Create Draft", self.test_create_draft),
            ("Create Reply Draft", self.test_create_draft_reply),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} Test ---")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: CRASHED - {e}")
        
        print(f"\n📊 Gmail Test Results: {passed}/{total} tests passed")
        return passed == total


if __name__ == "__main__":
    print("🧪 Gmail Function Tests")
    print("=" * 30)
    
    framework = TestFramework()
    if not framework.run_setup_check():
        print("❌ Setup failed. Cannot run tests.")
        sys.exit(1)
    
    gmail_tests = GmailTests(framework)
    success = gmail_tests.run_all_tests()
    
    if success:
        print("\n🎉 All Gmail tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some Gmail tests failed")
        sys.exit(1)