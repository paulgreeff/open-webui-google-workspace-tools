#!/usr/bin/env python3
"""
Interactive test runner for Google Workspace Tools

Provides a menu-driven interface to run specific tests or test suites.
"""

import sys
import os
from test_framework import TestFramework
from test_gmail import GmailTests
from test_calendar import CalendarTests


class InteractiveTestRunner:
    """Interactive menu-driven test runner"""
    
    def __init__(self):
        self.framework = TestFramework()
        self.gmail_tests = None
        self.calendar_tests = None
        self.setup_complete = False
        
    def setup(self):
        """Initialize the test framework"""
        print("🔧 Setting up test environment...")
        if self.framework.run_setup_check():
            self.gmail_tests = GmailTests(self.framework)
            self.calendar_tests = CalendarTests(self.framework)
            self.setup_complete = True
            return True
        return False
    
    def show_main_menu(self):
        """Display main menu options"""
        print("\n" + "=" * 50)
        print("🧪 Google Workspace Tools - Interactive Test Runner")
        print("=" * 50)
        print("1. 📧 Run Gmail Tests")
        print("2. 📅 Run Calendar Tests") 
        print("3. 🚀 Run All Tests")
        print("4. 🔍 Individual Function Tests")
        print("5. 📊 Authentication Status")
        print("6. ❓ Help")
        print("0. 🚪 Exit")
        print("-" * 50)
        
    def show_gmail_menu(self):
        """Display Gmail test menu"""
        print("\n📧 Gmail Tests:")
        print("1. Get Recent Emails")
        print("2. Search Emails")
        print("3. Get Email Content")
        print("4. Create Draft")
        print("5. Create Reply Draft")
        print("6. Run All Gmail Tests")
        print("0. Back to Main Menu")
        
    def show_calendar_menu(self):
        """Display Calendar test menu"""
        print("\n📅 Calendar Tests:")
        print("1. Get Calendars")
        print("2. Get Upcoming Events")
        print("3. Get Event Details")
        print("4. Today's Schedule")
        print("5. Search Events")
        print("6. Create Event (Smart)")
        print("7. Run All Calendar Tests")
        print("0. Back to Main Menu")
    
    def run_gmail_menu(self):
        """Handle Gmail test menu"""
        while True:
            self.show_gmail_menu()
            choice = input("\nEnter choice (0-6): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.gmail_tests.test_get_recent_emails()
            elif choice == "2":
                self.gmail_tests.test_search_emails()
            elif choice == "3":
                self.gmail_tests.test_get_email_content()
            elif choice == "4":
                self.gmail_tests.test_create_draft()
            elif choice == "5":
                self.gmail_tests.test_create_draft_reply()
            elif choice == "6":
                self.gmail_tests.run_all_tests()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run_calendar_menu(self):
        """Handle Calendar test menu"""
        while True:
            self.show_calendar_menu()
            choice = input("\nEnter choice (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.calendar_tests.test_get_calendars()
            elif choice == "2":
                self.calendar_tests.test_get_upcoming_events()
            elif choice == "3":
                self.calendar_tests.test_get_event_details()
            elif choice == "4":
                self.calendar_tests.test_get_todays_schedule()
            elif choice == "5":
                self.calendar_tests.test_search_calendar_events()
            elif choice == "6":
                self.calendar_tests.test_create_event_smart()
            elif choice == "7":
                self.calendar_tests.run_all_tests()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run_individual_tests(self):
        """Run individual function tests with custom parameters"""
        print("\n🔍 Individual Function Tests")
        print("-" * 30)
        print("1. Custom Email Search")
        print("2. Custom Event Creation")
        print("3. Custom Calendar Filter")
        print("4. Authentication Test")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice (0-4): ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            query = input("Enter search query: ").strip()
            max_results = input("Max results (default 5): ").strip() or "5"
            try:
                result = self.framework.tools.search_emails(query, int(max_results))
                print(f"\n✅ Search Results:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "2":
            title = input("Event title: ").strip()
            start_time = input("Start time (e.g. 'tomorrow 2 PM' or '2024-01-15 14:00'): ").strip()
            calendar_hint = input("Calendar hint (optional): ").strip() or None
            description = input("Description (optional): ").strip() or None
            
            try:
                result = self.framework.tools.create_event_smart(title, start_time, calendar_hint=calendar_hint, description=description)
                print(f"\n✅ Event Created:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "3":
            days_ahead = input("Days ahead (default 7): ").strip() or "7"
            calendar_names = input("Calendar names filter (optional): ").strip() or None
            
            try:
                result = self.framework.tools.get_upcoming_events(int(days_ahead), calendar_names=calendar_names)
                print(f"\n✅ Filtered Events:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "4":
            self.framework.test_authentication()
        else:
            print("❌ Invalid choice.")
    
    def show_help(self):
        """Display help information"""
        print("\n❓ Help - Google Workspace Tools Test Runner")
        print("=" * 50)
        print("This interactive test runner helps you test Google Workspace Tools functionality.")
        print("")
        print("🔧 Setup Requirements:")
        print("- credentials.json: Copy from Open-WebUI tool settings")
        print("- token.json: Copy from Open-WebUI after authentication")
        print("")
        print("📁 File Locations:")
        print("- Credential files should be in the tests/ directory")
        print("- Sample files are created if credentials.json is missing")
        print("")
        print("🧪 Test Categories:")
        print("- Gmail Tests: Email reading, searching, and draft creation")
        print("- Calendar Tests: Event management and calendar operations")
        print("- Individual Tests: Custom function calls with your parameters")
        print("")
        print("⚠️  Note: Some tests create real data (drafts, events)")
        print("Clean up test data as needed after running tests.")
        print("")
        print("🐛 Troubleshooting:")
        print("- Authentication errors: Check credentials.json and token.json")
        print("- Permission errors: Verify Google Cloud API access")
        print("- Enable debug mode in framework for detailed logs")
        input("\nPress Enter to continue...")
    
    def check_auth_status(self):
        """Check and display authentication status"""
        print("\n📊 Authentication Status Check")
        print("-" * 30)
        
        try:
            status = self.framework.tools.get_authentication_status()
            print(f"Status: {status}")
            
            # Also check what services are available
            print("\n📧 Testing Gmail access...")
            try:
                emails = self.framework.tools.get_recent_emails(count=1)
                print("✅ Gmail: Accessible")
            except Exception as e:
                print(f"❌ Gmail: {str(e)[:100]}")
            
            print("\n📅 Testing Calendar access...")
            try:
                calendars = self.framework.tools.get_calendars()
                print("✅ Calendar: Accessible")
                print(f"Available calendars: {calendars[:200]}...")
            except Exception as e:
                print(f"❌ Calendar: {str(e)[:100]}")
                
        except Exception as e:
            print(f"❌ Authentication check failed: {e}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main interactive loop"""
        print("🧪 Google Workspace Tools Test Runner")
        print("Starting setup...")
        
        if not self.setup():
            print("❌ Setup failed. Please check your credentials and try again.")
            return
            
        print("✅ Setup complete!")
        
        while True:
            try:
                self.show_main_menu()
                choice = input("Enter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.run_gmail_menu()
                elif choice == "2":
                    self.run_calendar_menu()
                elif choice == "3":
                    print("\n🚀 Running All Tests...")
                    gmail_success = self.gmail_tests.run_all_tests()
                    calendar_success = self.calendar_tests.run_all_tests()
                    
                    if gmail_success and calendar_success:
                        print("\n🎉 All tests passed!")
                    else:
                        print("\n💥 Some tests failed. Check the output above for details.")
                    
                    input("\nPress Enter to continue...")
                elif choice == "4":
                    self.run_individual_tests()
                elif choice == "5":
                    self.check_auth_status()
                elif choice == "6":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")


if __name__ == "__main__":
    runner = InteractiveTestRunner()
    runner.run()