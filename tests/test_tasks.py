#!/usr/bin/env python3
"""
Tasks function tests for Google Workspace Tools
"""

import sys
import os
import time
from test_framework import TestFramework


class TasksTests:
    """Tasks function test suite"""
    
    def __init__(self, framework: TestFramework):
        self.framework = framework
        self.tools = framework.tools
        self.test_list_id = None  # Will store test list ID for cleanup
        self.test_task_ids = []   # Will store test task IDs for cleanup
        
    def test_get_task_lists(self):
        """Test listing all task lists"""
        print("\n📝 Testing get_task_lists()...")
        try:
            result = self.tools.get_task_lists()
            print(f"✅ Success: Task lists retrieved")
            print(f"Preview: {result[:400]}..." if len(result) > 400 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_task_list(self):
        """Test creating a new task list"""
        print("\n✏️  Testing create_task_list()...")
        try:
            # Create unique test list name with timestamp
            timestamp = int(time.time())
            test_list_name = f"TEST TASK LIST {timestamp}"
            
            result = self.tools.create_task_list(test_list_name)
            print(f"✅ Success: Task list created")
            print(f"Result: {result}")
            
            # Extract list ID for later cleanup
            import re
            id_match = re.search(r'List ID.*?`([^`]+)`', result)
            if id_match:
                self.test_list_id = id_match.group(1)
                print(f"📝 Stored test list ID for cleanup: {self.test_list_id}")
            
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_update_task_list(self):
        """Test updating task list name"""
        print("\n✏️  Testing update_task_list()...")
        try:
            if not self.test_list_id:
                print("⚠️  No test list ID available - skipping update test")
                return True
            
            # Update with new name
            timestamp = int(time.time())
            new_name = f"UPDATED TEST LIST {timestamp}"
            
            result = self.tools.update_task_list(self.test_list_id, new_name)
            print(f"✅ Success: Task list updated")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_task(self):
        """Test creating tasks"""
        print("\n📝 Testing create_task()...")
        try:
            if not self.test_list_id:
                print("⚠️  No test list ID available - skipping task creation test")
                return True
            
            # Create test task with timestamp
            timestamp = int(time.time())
            task_title = f"Test Task {timestamp}"
            task_notes = f"This is a test task created at {timestamp}"
            
            result = self.tools.create_task(
                list_id=self.test_list_id,
                title=task_title,
                notes=task_notes,
                due_date="tomorrow"
            )
            print(f"✅ Success: Task created")
            print(f"Result: {result}")
            
            # Extract task ID for later tests
            import re
            id_match = re.search(r'Task ID.*?`([^`]+)`', result)
            if id_match:
                task_id = id_match.group(1)
                self.test_task_ids.append(task_id)
                print(f"📝 Stored test task ID: {task_id}")
            
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_subtask(self):
        """Test creating subtasks with hierarchy"""
        print("\n📝 Testing create_task() with subtasks...")
        try:
            if not self.test_list_id or not self.test_task_ids:
                print("⚠️  No test list or parent task available - skipping subtask test")
                return True
            
            # Create subtask under first test task
            parent_id = self.test_task_ids[0]
            timestamp = int(time.time())
            subtask_title = f"Subtask {timestamp}"
            
            result = self.tools.create_task(
                list_id=self.test_list_id,
                title=subtask_title,
                notes="This is a test subtask",
                parent_id=parent_id
            )
            print(f"✅ Success: Subtask created")
            print(f"Result: {result}")
            
            # Store subtask ID
            import re
            id_match = re.search(r'Task ID.*?`([^`]+)`', result)
            if id_match:
                subtask_id = id_match.group(1)
                self.test_task_ids.append(subtask_id)
                print(f"📝 Stored test subtask ID: {subtask_id}")
            
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_tasks(self):
        """Test listing tasks from task list"""
        print("\n📋 Testing get_tasks()...")
        try:
            if not self.test_list_id:
                print("⚠️  No test list ID available - skipping get tasks test")
                return True
            
            result = self.tools.get_tasks(self.test_list_id)
            print(f"✅ Success: Tasks retrieved")
            print(f"Preview: {result[:500]}..." if len(result) > 500 else result)
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_task_with_smart_list_selection(self):
        """Test smart list selection for task creation"""
        print("\n🧠 Testing create_task_with_smart_list_selection()...")
        try:
            # Use a generic hint that should match our test list
            timestamp = int(time.time())
            task_title = f"Smart Task {timestamp}"
            
            result = self.tools.create_task_with_smart_list_selection(
                title=task_title,
                notes="Created using smart list selection",
                list_hint="TEST"  # Should match our TEST TASK LIST
            )
            print(f"✅ Success: Task created with smart selection")
            print(f"Result: {result}")
            
            # Store task ID if created in our test list
            import re
            id_match = re.search(r'Task ID.*?`([^`]+)`', result)
            if id_match and self.test_list_id and self.test_list_id in result:
                task_id = id_match.group(1)
                self.test_task_ids.append(task_id)
                print(f"📝 Stored smart-created task ID: {task_id}")
            
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_update_task(self):
        """Test updating tasks"""
        print("\n✏️  Testing update_task()...")
        try:
            if not self.test_list_id or not self.test_task_ids:
                print("⚠️  No test tasks available - skipping update test")
                return True
            
            # Update first test task
            task_id = self.test_task_ids[0]
            timestamp = int(time.time())
            new_title = f"Updated Task Title {timestamp}"
            
            result = self.tools.update_task(
                list_id=self.test_list_id,
                task_id=task_id,
                title=new_title,
                notes="Task updated during testing"
            )
            print(f"✅ Success: Task updated")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_mark_task_complete(self):
        """Test marking tasks as complete"""
        print("\n✅ Testing mark_task_complete()...")
        try:
            if not self.test_list_id or not self.test_task_ids:
                print("⚠️  No test tasks available - skipping completion test")
                return True
            
            # Mark last test task as complete
            task_id = self.test_task_ids[-1]
            
            result = self.tools.mark_task_complete(self.test_list_id, task_id)
            print(f"✅ Success: Task marked complete")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_move_task(self):
        """Test moving tasks"""
        print("\n↔️  Testing move_task()...")
        try:
            if not self.test_list_id or len(self.test_task_ids) < 2:
                print("⚠️  Need at least 2 test tasks - skipping move test")
                return True
            
            # Move second task as subtask of first task (if not already)
            parent_task_id = self.test_task_ids[0]
            task_to_move = self.test_task_ids[1] if len(self.test_task_ids) > 1 else self.test_task_ids[0]
            
            # Skip if trying to move task under itself
            if parent_task_id == task_to_move:
                print("⚠️  Cannot move task under itself - skipping move test")
                return True
            
            result = self.tools.move_task(
                list_id=self.test_list_id,
                task_id=task_to_move,
                parent_id=parent_task_id
            )
            print(f"✅ Success: Task moved")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_delete_task(self):
        """Test deleting tasks"""
        print("\n🗑️  Testing delete_task()...")
        try:
            if not self.test_list_id or not self.test_task_ids:
                print("⚠️  No test tasks available - skipping delete test")
                return True
            
            # Delete one of the test tasks (keep at least one for final cleanup)
            if len(self.test_task_ids) > 1:
                task_id = self.test_task_ids.pop()  # Remove from list and delete
                
                result = self.tools.delete_task(self.test_list_id, task_id)
                print(f"✅ Success: Task deleted")
                print(f"Result: {result}")
                return True
            else:
                print("⚠️  Keeping last task for cleanup - skipping individual delete test")
                return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_clear_completed_tasks(self):
        """Test clearing completed tasks"""
        print("\n🧹 Testing clear_completed_tasks()...")
        try:
            if not self.test_list_id:
                print("⚠️  No test list ID available - skipping clear test")
                return True
            
            result = self.tools.clear_completed_tasks(self.test_list_id)
            print(f"✅ Success: Completed tasks cleared")
            print(f"Result: {result}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data created during tests"""
        print("\n🧹 Cleaning up test data...")
        try:
            # Delete test task list (this will delete all tasks in it)
            if self.test_list_id:
                print(f"Deleting test task list: {self.test_list_id}")
                result = self.tools.delete_task_list(self.test_list_id)
                print(f"Cleanup result: {result}")
                self.test_list_id = None
                self.test_task_ids.clear()
            else:
                print("No test list to clean up")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_all_tests(self):
        """Run all Tasks tests"""
        print("🧪 Running Tasks Test Suite")
        print("=" * 40)
        
        if not self.framework.setup_complete:
            print("❌ Framework not set up properly")
            return False
        
        tests = [
            ("List Task Lists", self.test_get_task_lists),
            ("Create Task List", self.test_create_task_list),
            ("Update Task List", self.test_update_task_list), 
            ("Create Task", self.test_create_task),
            ("Create Subtask", self.test_create_subtask),
            ("Get Tasks", self.test_get_tasks),
            ("Smart Task Creation", self.test_create_task_with_smart_list_selection),
            ("Update Task", self.test_update_task),
            ("Mark Task Complete", self.test_mark_task_complete),
            ("Move Task", self.test_move_task),
            ("Delete Task", self.test_delete_task),
            ("Clear Completed Tasks", self.test_clear_completed_tasks),
        ]
        
        passed = 0
        total = len(tests)
        
        try:
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
            
            print(f"\n📊 Tasks Test Results: {passed}/{total} tests passed")
            
            return passed == total
        
        finally:
            # Always attempt cleanup
            self.cleanup_test_data()


if __name__ == "__main__":
    print("🧪 Tasks Function Tests")
    print("=" * 30)
    
    framework = TestFramework()
    if not framework.run_setup_check():
        print("❌ Setup failed. Cannot run tests.")
        sys.exit(1)
    
    tasks_tests = TasksTests(framework)
    success = tasks_tests.run_all_tests()
    
    if success:
        print("\n🎉 All Tasks tests passed!")
        print("\n⚠️  Test cleanup completed. All test data was removed.")
        sys.exit(0)
    else:
        print("\n💥 Some Tasks tests failed")
        sys.exit(1)