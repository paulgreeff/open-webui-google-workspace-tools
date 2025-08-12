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
from test_contacts import ContactTests
from test_tasks import TasksTests


class InteractiveTestRunner:
    """Interactive menu-driven test runner"""
    
    def __init__(self):
        self.framework = TestFramework()
        self.gmail_tests = None
        self.calendar_tests = None
        self.contact_tests = None
        self.tasks_tests = None
        self.setup_complete = False
        
    def setup(self):
        """Initialize the test framework"""
        print("🔧 Setting up test environment...")
        if self.framework.run_setup_check():
            self.gmail_tests = GmailTests(self.framework)
            self.calendar_tests = CalendarTests(self.framework)
            self.contact_tests = ContactTests(self.framework)
            self.tasks_tests = TasksTests(self.framework)
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
        print("3. 👥 Run Contacts Tests")
        print("4. 📝 Run Tasks Tests")
        print("5. 🚀 Run All Tests")
        print("6. 🔍 Individual Function Tests")
        print("7. 📊 Authentication Status")
        print("8. ❓ Help")
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
        
    def show_contacts_menu(self):
        """Display Contacts test menu"""
        print("\n👥 Contacts Tests:")
        print("1. List Recent Contacts")
        print("2. Search Contacts")
        print("3. Get Contact Details")
        print("4. Email Lookup")
        print("5. Create Contact")
        print("6. Duplicate Detection Test")
        print("7. Run All Contacts Tests")
        print("0. Back to Main Menu")
    
    def show_tasks_menu(self):
        """Display Tasks test menu"""
        print("\n📝 Tasks Tests:")
        print("1. List Task Lists")
        print("2. Create Task List")
        print("3. Update Task List")
        print("4. Create Task")
        print("5. Get Tasks")
        print("6. Smart Task Creation")
        print("7. Update Task")
        print("8. Mark Task Complete")
        print("9. Move Task")
        print("10. Delete Task")
        print("11. Clear Completed Tasks")
        print("12. Run All Tasks Tests")
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
    
    def run_contacts_menu(self):
        """Handle Contacts test menu"""
        while True:
            self.show_contacts_menu()
            choice = input("\nEnter choice (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.contact_tests.test_list_recent_contacts()
            elif choice == "2":
                self.contact_tests.test_search_contacts()
            elif choice == "3":
                self.contact_tests.test_get_contact_details()
            elif choice == "4":
                self.contact_tests.test_lookup_contact_by_email()
            elif choice == "5":
                self.contact_tests.test_create_contact()
            elif choice == "6":
                self.contact_tests.test_duplicate_detection()
            elif choice == "7":
                self.contact_tests.run_all_tests()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run_tasks_menu(self):
        """Handle Tasks test menu"""
        while True:
            self.show_tasks_menu()
            choice = input("\nEnter choice (0-12): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.tasks_tests.test_get_task_lists()
            elif choice == "2":
                self.tasks_tests.test_create_task_list()
            elif choice == "3":
                self.tasks_tests.test_update_task_list()
            elif choice == "4":
                self.tasks_tests.test_create_task()
            elif choice == "5":
                self.tasks_tests.test_get_tasks()
            elif choice == "6":
                self.tasks_tests.test_create_task_with_smart_list_selection()
            elif choice == "7":
                self.tasks_tests.test_update_task()
            elif choice == "8":
                self.tasks_tests.test_mark_task_complete()
            elif choice == "9":
                self.tasks_tests.test_move_task()
            elif choice == "10":
                self.tasks_tests.test_delete_task()
            elif choice == "11":
                self.tasks_tests.test_clear_completed_tasks()
            elif choice == "12":
                self.tasks_tests.run_all_tests()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run_individual_tests(self):
        """Run individual function tests with custom parameters"""
        print("\n🔍 Individual Function Tests")
        print("-" * 30)
        print("1. Custom Email Search")
        print("2. Custom Event Creation")
        print("3. Custom Calendar Filter")
        print("4. Custom Contact Search")
        print("5. Custom Contact Lookup")
        print("6. Custom Task Creation")
        print("7. Custom Task List Creation")
        print("8. Authentication Test")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice (0-8): ").strip()
        
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
            query = input("Enter contact search query: ").strip()
            max_results = input("Max results (default 10): ").strip() or "10"
            try:
                result = self.framework.tools.search_contacts(query, int(max_results))
                print(f"\n✅ Contact Search Results:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "5":
            email = input("Enter email address to lookup: ").strip()
            try:
                result = self.framework.tools.lookup_contact_by_email(email)
                print(f"\n✅ Contact Lookup Result:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "6":
            title = input("Task title: ").strip()
            list_hint = input("Task list hint (optional): ").strip() or None
            notes = input("Notes (optional): ").strip() or None
            due_date = input("Due date (optional, e.g. 'tomorrow' or '2024-01-15'): ").strip() or None
            
            try:
                result = self.framework.tools.create_task_with_smart_list_selection(title, notes, due_date, list_hint)
                print(f"\n✅ Task Created:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "7":
            name = input("Task list name: ").strip()
            
            try:
                result = self.framework.tools.create_task_list(name)
                print(f"\n✅ Task List Created:\n{result}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "8":
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
        print("- Contacts Tests: Contact search, lookup, and management")
        print("- Tasks Tests: Task list and task management operations")
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
            
            print("\n👥 Testing Contacts access...")
            try:
                contacts = self.framework.tools.list_recent_contacts(limit=1)
                print("✅ Contacts: Accessible")
                print(f"Contact status: {contacts[:200]}...")
            except Exception as e:
                print(f"❌ Contacts: {str(e)[:100]}")
            
            print("\n📝 Testing Tasks access...")
            try:
                task_lists = self.framework.tools.get_task_lists()
                print("✅ Tasks: Accessible")
                print(f"Available task lists: {task_lists[:200]}...")
            except Exception as e:
                print(f"❌ Tasks: {str(e)[:100]}")
                
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
                choice = input("Enter your choice (0-8): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.run_gmail_menu()
                elif choice == "2":
                    self.run_calendar_menu()
                elif choice == "3":
                    self.run_contacts_menu()
                elif choice == "4":
                    self.run_tasks_menu()
                elif choice == "5":
                    print("\n🚀 Running All Tests...")
                    gmail_success = self.gmail_tests.run_all_tests()
                    calendar_success = self.calendar_tests.run_all_tests()
                    contacts_success = self.contact_tests.run_all_tests()
                    tasks_success = self.tasks_tests.run_all_tests()
                    
                    if gmail_success and calendar_success and contacts_success and tasks_success:
                        print("\n🎉 All tests passed!")
                    else:
                        print("\n💥 Some tests failed. Check the output above for details.")
                    
                    input("\nPress Enter to continue...")
                elif choice == "6":
                    self.run_individual_tests()
                elif choice == "7":
                    self.check_auth_status()
                elif choice == "8":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-8.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                input("Press Enter to continue...")


if __name__ == "__main__":
    runner = InteractiveTestRunner()
    runner.run()