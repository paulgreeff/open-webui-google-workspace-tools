#!/usr/bin/env python3
"""
Calendar function tests for Google Workspace Tools
"""

import sys
import os
from test_framework import TestFramework
from datetime import datetime, timedelta


class CalendarTests:
    """Calendar function test suite"""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.tools = framework.tools
        
    def test_get_calendars(self):
        """Test listing calendars"""
        print("\n📅 Testing get_calendars()...")
        try:
            result = self.tools.get_calendars()
            print(f"✅ Success: Retrieved calendars")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events"""
        print("\n🔮 Testing get_upcoming_events()...")
        try:
            result = self.tools.get_upcoming_events(days_ahead=7)
            print(f"✅ Success: Retrieved upcoming events")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_upcoming_events_filtered(self):
        """Test filtered upcoming events"""
        print("\n🎯 Testing get_upcoming_events() with calendar filter...")
        try:
            # First get calendars to see what we can filter by
            calendars_result = self.tools.get_calendars()
            print(f"Available calendars: {calendars_result}")
            
            result = self.tools.get_upcoming_events(days_ahead=14, calendar_names="primary")
            print(f"✅ Success: Retrieved filtered events")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_event_details(self):
        """Test getting detailed event information"""
        print("\n🔍 Testing get_event_details()...")
        try:
            # First get some upcoming events to test with
            events = self.tools.get_upcoming_events(days_ahead=30)
            
            if "Event ID:" not in events:
                print("⚠️  No events found to test details retrieval")
                return False
                
            # Extract an event ID from the result
            import re
            id_match = re.search(r'Event ID: ([a-zA-Z0-9_-]+)', events)
            if not id_match:
                print("⚠️  Could not extract event ID from upcoming events")
                return False
                
            event_id = id_match.group(1)
            print(f"Testing with event ID: {event_id}")
            
            result = self.tools.get_event_details(event_id)
            print(f"✅ Success: Retrieved event details")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_todays_schedule(self):
        """Test getting today's schedule"""
        print("\n📋 Testing get_todays_schedule()...")
        try:
            result = self.tools.get_todays_schedule()
            print(f"✅ Success: Retrieved today's schedule")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_search_calendar_events(self):
        """Test calendar event search"""
        print("\n🔍 Testing search_calendar_events()...")
        try:
            # Search for any events (broad search terms)
            result = self.tools.search_calendar_events("meeting OR appointment OR call", days_back=30, days_ahead=30)
            print(f"✅ Success: Search completed")
            print(f"Preview: {result[:300]}..." if len(result) > 300 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_event_smart(self):
        """Test smart event creation"""
        print("\n✨ Testing create_event_smart()...")
        try:
            # Create a test event for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = f"{tomorrow.strftime('%Y-%m-%d')} 15:00"
            
            result = self.tools.create_event_smart(
                title="TEST EVENT - Please Delete",
                start_time=start_time,
                description="This is a test event created by the Google Workspace Tools test suite. Please delete it."
            )
            print(f"✅ Success: Event created")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_event_smart_with_calendar_hint(self):
        """Test smart event creation with calendar hint"""
        print("\n🎯 Testing create_event_smart() with calendar hint...")
        try:
            # Create event with calendar hint
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = f"{tomorrow.strftime('%Y-%m-%d')} 16:00"
            
            result = self.tools.create_event_smart(
                title="TEST EVENT 2 - Please Delete", 
                start_time=start_time,
                calendar_hint="primary",
                description="Another test event with calendar hint."
            )
            print(f"✅ Success: Event created with calendar hint")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_event_smart_with_duration(self):
        """Test smart event creation with custom duration"""
        print("\n⏰ Testing create_event_smart() with custom duration...")
        try:
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = f"{tomorrow.strftime('%Y-%m-%d')} 17:00"
            end_time = f"{tomorrow.strftime('%Y-%m-%d')} 18:30"
            
            result = self.tools.create_event_smart(
                title="TEST EVENT 3 - Please Delete",
                start_time=start_time,
                end_time=end_time,
                description="Test event with custom duration (1.5 hours)."
            )
            print(f"✅ Success: Event created with custom duration")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Calendar tests"""
        print("🧪 Running Calendar Test Suite")
        print("=" * 40)
        
        if not self.framework.setup_complete:
            print("❌ Framework not set up properly")
            return False
        
        tests = [
            ("Get Calendars", self.test_get_calendars),
            ("Upcoming Events", self.test_get_upcoming_events),
            ("Filtered Events", self.test_get_upcoming_events_filtered),
            ("Event Details", self.test_get_event_details),
            ("Today's Schedule", self.test_get_todays_schedule),
            ("Search Events", self.test_search_calendar_events),
            ("Create Event", self.test_create_event_smart),
            ("Create Event with Hint", self.test_create_event_smart_with_calendar_hint),
            ("Create Event with Duration", self.test_create_event_smart_with_duration),
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
        
        print(f"\n📊 Calendar Test Results: {passed}/{total} tests passed")
        
        if passed > 0 and "Create Event" in [t[0] for t in tests if test_func.__name__ in ['test_create_event_smart', 'test_create_event_smart_with_calendar_hint', 'test_create_event_smart_with_duration']]:
            print("\n⚠️  Note: Test events were created. Please delete them from your calendar if desired.")
            
        return passed == total


if __name__ == "__main__":
    print("🧪 Calendar Function Tests")
    print("=" * 30)
    
    framework = TestFramework()
    if not framework.run_setup_check():
        print("❌ Setup failed. Cannot run tests.")
        sys.exit(1)
    
    calendar_tests = CalendarTests(framework)
    success = calendar_tests.run_all_tests()
    
    if success:
        print("\n🎉 All Calendar tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some Calendar tests failed")
        sys.exit(1)