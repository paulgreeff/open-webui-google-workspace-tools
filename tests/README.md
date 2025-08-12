# Google Workspace Tools - Test Suite

Comprehensive test suite for Google Workspace Tools that allows testing all functions without Open-WebUI.

> ✅ **All tests pass successfully** - Gmail, Calendar, and Contacts functions are fully working and verified.

## Quick Start

### 1. Setup Test Environment

```bash
cd tests/

# Install dependencies (same as main project)
pip install -r requirements.txt
# Which installs: google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil pytz pydantic

# Create credential files from your Open-WebUI setup
python test_framework.py  # This creates sample files if credentials.json doesn't exist
```

### 2. Copy Credentials from Open-WebUI

**Method 1: Copy Token File (Recommended)**
```bash
# Find your Open-WebUI data directory (varies by installation)
# Look for: /app/backend/data/google_tools/[user_id]/
cp /path/to/openwebui/data/google_tools/[user_id]/token.json ./token.json
```

**Method 2: From Open-WebUI Settings**
1. Go to Open-WebUI → Tools → Google Workspace Tools → Settings
2. Copy the entire `credentials_json` field content → save as `credentials.json`
3. If you have completed authentication in Open-WebUI, copy token data → save as `token.json`

**Method 3: Convert Auth Code (If you only have auth_code)**
```bash
# Copy credentials_json from Open-WebUI → save as credentials.json
# Copy auth_code from Open-WebUI settings
python convert_auth_code.py  # Enter the auth_code when prompted
```

**Note**: The `auth_code` in Open-WebUI Valves is a temporary, single-use code. The `token.json` contains the actual access/refresh tokens needed for API calls.

### 3. Run Tests

**Interactive Test Runner** (Recommended)
```bash
python test_runner.py
```

**Individual Test Suites**
```bash
python test_gmail.py      # Gmail function tests
python test_calendar.py   # Calendar function tests
python test_framework.py  # Framework setup test
```

## Test Files Overview

### Core Framework
- **`test_framework.py`** - Base framework with credential loading and authentication
- **`test_runner.py`** - Interactive menu-driven test interface

### Function Test Suites
- **`test_gmail.py`** - Gmail API function tests
- **`test_calendar.py`** - Calendar API function tests
- **`test_contacts.py`** - Contacts API function tests
- **`test_tasks.py`** - Tasks API function tests

### Configuration Files
- **`credentials.json`** - Your Google Cloud OAuth2 credentials (you create this)
- **`token.json`** - Authentication tokens (you copy this from Open-WebUI)
- **`credentials.json.sample`** - Template showing required credential format
- **`token.json.sample`** - Template showing required token format

## Test Coverage

### Gmail Tests
✅ **get_recent_emails()** - Fetch recent emails with filtering  
✅ **search_emails()** - Search functionality with Gmail query syntax  
✅ **get_email_content()** - Full email content retrieval  
✅ **create_draft()** - Draft email creation  
✅ **create_draft_reply()** - Reply draft with proper threading  

### Calendar Tests  
✅ **get_calendars()** - List all accessible calendars  
✅ **get_upcoming_events()** - Upcoming events with filtering  
✅ **get_event_details()** - Detailed event information  
✅ **get_todays_schedule()** - Daily schedule briefing  
✅ **search_calendar_events()** - Event search with relevance scoring  
✅ **create_event_smart()** - Smart event creation with calendar matching  

### Contacts Tests
✅ **search_contacts()** - Search contacts by name, email, phone, or organization
✅ **lookup_contact_by_email()** - Find contact by specific email address  
✅ **get_contact_details()** - Get comprehensive contact information
✅ **list_recent_contacts()** - List recently modified contacts
✅ **create_contact()** - Create new contacts with duplicate detection
✅ **duplicate_detection()** - Test contact creation duplicate prevention

### Tasks Tests
✅ **get_task_lists()** - List all available task lists
✅ **create_task_list()** - Create new task lists
✅ **update_task_list()** - Update task list names
✅ **delete_task_list()** - Delete task lists (with warning)
✅ **clear_completed_tasks()** - Clear completed tasks from lists
✅ **get_tasks()** - Get tasks with filtering and hierarchy display
✅ **create_task()** - Create tasks with due dates and hierarchy support
✅ **create_task_with_smart_list_selection()** - Smart list selection for tasks
✅ **update_task()** - Update task titles, notes, due dates, and status
✅ **move_task()** - Move tasks and create task hierarchies
✅ **delete_task()** - Delete tasks and their subtasks
✅ **mark_task_complete()** - Mark tasks as completed

### Authentication Tests
✅ **get_authentication_status()** - Current auth status  
✅ **Token validation** - Automatic token refresh testing  
✅ **Service access** - Gmail, Calendar, and Contacts API accessibility  

## Usage Examples

### Interactive Testing
```bash
python test_runner.py

# Menu appears:
# 1. 📧 Run Gmail Tests
# 2. 📅 Run Calendar Tests
# 3. 👥 Run Contacts Tests
# 4. 📝 Run Tasks Tests
# 5. 🚀 Run All Tests
# 6. 🔍 Individual Function Tests
# 7. 📊 Authentication Status
```

### Quick Test Run
```bash
# Test everything
python test_gmail.py && python test_calendar.py && python test_contacts.py && python test_tasks.py

# Test specific function
python -c "
from test_framework import TestFramework
framework = TestFramework()
framework.run_setup_check()
print(framework.tools.get_calendars())
"
```

### Custom Function Testing
```python
from test_framework import TestFramework

# Setup
framework = TestFramework()
framework.run_setup_check()
tools = framework.tools

# Test any function with custom parameters
result = tools.search_emails("project update", max_results=5)
print(result)

result = tools.create_event_smart("Test Meeting", "tomorrow 2 PM", calendar_hint="work")
print(result)

# Test contact functions
result = tools.search_contacts("john", max_results=5)
print(result)

result = tools.lookup_contact_by_email("john@example.com")
print(result)

# Test task functions  
result = tools.get_task_lists()
print(result)

result = tools.create_task_with_smart_list_selection("Test task", "Test notes", "tomorrow")
print(result)
```

## Troubleshooting

### Authentication Issues

**"Not authenticated" errors:**
```bash
# Check auth status
python -c "
from test_framework import TestFramework
f = TestFramework()
f.run_setup_check()
print(f.tools.get_authentication_status())
"
```

**Token expired:**
1. Go back to Open-WebUI
2. Re-authenticate if needed
3. Copy the new token.json to tests directory

### Permission Errors

**"Permission denied" for Gmail:**
- Ensure Gmail API is enabled in Google Cloud Console
- Check that your OAuth2 credentials have the correct scopes

**"Permission denied" for Calendar:**  
- Ensure Google Calendar API is enabled
- Some calendars may be read-only (check with `get_calendars()`)

**"Permission denied" for Contacts:**
- Ensure Google People API is enabled in Google Cloud Console
- Check that your OAuth2 credentials include contacts scopes
- Some contact operations require write permissions

### Import Errors

**"Cannot import google_workspace_tools":**
```bash
# Ensure the main file is in parent directory
ls -la ../google_workspace_tools.py

# Check Python path
python -c "import sys; print(sys.path)"
```

**Missing dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil
```

### Performance Issues

**Slow test execution:**
- Large calendars/inboxes take time to process
- Reduce test parameters (fewer days, less results)
- Use calendar filtering to limit scope

### Test Data Cleanup

**Created test events/drafts/contacts:**
```bash
# Calendar events - delete from Google Calendar interface
# Gmail drafts - delete from Gmail drafts folder
# Contacts - delete from Google Contacts interface
```

Some tests create real data:
- Gmail drafts (subjects starting with "Test Draft")
- Calendar events (titles starting with "TEST EVENT")
- Contacts (names starting with "Test Contact")

## Debug Mode

Enable detailed logging by modifying test files:

```python
# In test_framework.py, change:
self.debug_mode = True

# Or set environment variable:
export GOOGLE_TOOLS_DEBUG=1
```

## Advanced Usage

### Batch Testing
```bash
# Run all tests and save output
python test_runner.py > test_results.txt 2>&1

# Test specific functions in loop
for i in {1..5}; do
    echo "Test run $i"
    python test_gmail.py
done
```

### Custom Test Development
```python
# Create your own test
from test_framework import TestFramework

def my_custom_test():
    framework = TestFramework()
    if not framework.run_setup_check():
        return
    
    tools = framework.tools
    
    # Your custom testing logic
    emails = tools.search_emails("your query here")
    # Process results...

if __name__ == "__main__":
    my_custom_test()
```

### Continuous Integration

For CI/CD pipelines, use the non-interactive functions:

```bash
#!/bin/bash
# ci_test.sh

python test_gmail.py
gmail_status=$?

python test_calendar.py  
calendar_status=$?

if [ $gmail_status -eq 0 ] && [ $calendar_status -eq 0 ]; then
    echo "All tests passed"
    exit 0
else
    echo "Tests failed"
    exit 1
fi
```

## Getting Help

1. **Check authentication first**: `python test_framework.py`
2. **Enable debug mode** for detailed error messages  
3. **Verify credentials** match your Open-WebUI setup exactly
4. **Test individual functions** to isolate issues
5. **Check Google Cloud Console** for API quotas and enabled services

For more help, refer to the main project documentation:
- [Authentication Guide](../docs/authentication.md)
- [Usage Examples](../docs/usage_examples.md)
- [Installation Guide](../docs/installation.md)