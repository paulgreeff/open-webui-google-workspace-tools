#!/usr/bin/env python3
"""
Contacts function tests for Google Workspace Tools
"""

import sys
import os
from test_framework import TestFramework


class ContactTests:
    """Contacts function test suite"""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.tools = framework.tools
        
    def test_list_recent_contacts(self):
        """Test listing recent contacts"""
        print("\n👥 Testing list_recent_contacts()...")
        try:
            result = self.tools.list_recent_contacts(limit=10)
            print(f"✅ Success: Listed contacts")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_search_contacts(self):
        """Test contact search functionality"""
        print("\n🔍 Testing search_contacts()...")
        try:
            # Search for any contacts (broad search using common names)
            result = self.tools.search_contacts("a", max_results=5)
            print(f"✅ Success: Search completed")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_contact_details(self):
        """Test getting full contact details"""
        print("\n📄 Testing get_contact_details()...")
        try:
            # First get recent contacts to test with
            recent = self.tools.list_recent_contacts(limit=1)
            
            if "ID:" not in recent:
                print("⚠️  No contacts found to test details retrieval")
                return False
                
            # Extract contact ID from the result
            import re
            id_match = re.search(r'ID: `([^`]+)`', recent)
            if not id_match:
                print("⚠️  Could not extract contact ID from recent contacts")
                return False
                
            contact_id = id_match.group(1)
            print(f"Testing with contact ID: {contact_id}")
            
            result = self.tools.get_contact_details(contact_id)
            print(f"✅ Success: Retrieved contact details")
            print(f"Preview: {result[:400]}..." if len(result) > 400 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_lookup_contact_by_email(self):
        """Test looking up contact by email address"""
        print("\n📧 Testing lookup_contact_by_email()...")
        try:
            # First get recent contacts to find an email address
            recent = self.tools.list_recent_contacts(limit=5)
            
            if "📧" not in recent:
                print("⚠️  No contacts with email addresses found to test lookup")
                return False
                
            # Extract email address from the result
            import re
            email_match = re.search(r'📧 ([^•\s]+)', recent)
            if not email_match:
                print("⚠️  Could not extract email address from contacts")
                return False
                
            email = email_match.group(1).strip().rstrip(',')
            print(f"Testing lookup with email: {email}")
            
            result = self.tools.lookup_contact_by_email(email)
            print(f"✅ Success: Contact lookup completed")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_contact(self):
        """Test creating a new contact"""
        print("\n✏️  Testing create_contact()...")
        try:
            # Use timestamp to make unique contact
            import time
            timestamp = int(time.time())
            
            result = self.tools.create_contact(
                name=f"Test Contact {timestamp}",
                email=f"test{timestamp}@example.com",
                phone="+1234567890",
                organization="Test Organization"
            )
            print(f"✅ Success: Contact created")
            print(f"Result: {result}")
            
            # Note: User should manually delete this test contact later
            print(f"⚠️  Remember to manually delete test contact: Test Contact {timestamp}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_duplicate_detection(self):
        """Test duplicate contact detection"""
        print("\n🔍 Testing duplicate detection in create_contact()...")
        try:
            # Try to create a contact with existing email (should be detected)
            recent = self.tools.list_recent_contacts(limit=5)
            
            if "📧" not in recent:
                print("⚠️  No existing contacts with email addresses found for duplicate test")
                return True  # Skip this test if no existing emails
                
            # Extract email address from existing contact
            import re
            email_match = re.search(r'📧 ([^•\s]+)', recent)
            if not email_match:
                print("⚠️  Could not extract email address for duplicate test")
                return True  # Skip this test
                
            existing_email = email_match.group(1).strip().rstrip(',')
            print(f"Testing duplicate detection with existing email: {existing_email}")
            
            result = self.tools.create_contact(
                name="Duplicate Test Contact",
                email=existing_email
            )
            
            # Should return a duplicate warning, not create the contact
            if "Duplicate contact detected" in result:
                print(f"✅ Success: Duplicate detection working correctly")
                print(f"Warning message: {result[:200]}...")
                return True
            else:
                print(f"⚠️  Unexpected result - may have created duplicate: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Contacts tests"""
        print("🧪 Running Contacts Test Suite")
        print("=" * 40)
        
        if not self.framework.setup_complete:
            print("❌ Framework not set up properly")
            return False
        
        tests = [
            ("List Recent Contacts", self.test_list_recent_contacts),
            ("Search Contacts", self.test_search_contacts),
            ("Contact Details", self.test_get_contact_details),
            ("Email Lookup", self.test_lookup_contact_by_email),
            ("Create Contact", self.test_create_contact),
            ("Duplicate Detection", self.test_duplicate_detection),
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
        
        print(f"\n📊 Contacts Test Results: {passed}/{total} tests passed")
        
        if passed < total:
            print("\n⚠️  **Test Cleanup Note**: Some tests create contacts with 'Test Contact' prefix.")
            print("    You may want to manually delete these test contacts from your Google Contacts.")
        
        return passed == total


if __name__ == "__main__":
    print("🧪 Contacts Function Tests")
    print("=" * 30)
    
    framework = TestFramework()
    if not framework.run_setup_check():
        print("❌ Setup failed. Cannot run tests.")
        sys.exit(1)
    
    contact_tests = ContactTests(framework)
    success = contact_tests.run_all_tests()
    
    if success:
        print("\n🎉 All Contacts tests passed!")
        print("\n⚠️  Don't forget to clean up any test contacts created during testing.")
        sys.exit(0)
    else:
        print("\n💥 Some Contacts tests failed")
        sys.exit(1)