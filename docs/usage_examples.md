# Usage Examples

This guide provides practical examples of using Google Workspace Tools with your AI assistant.

> ✅ **All functions are fully tested and working perfectly** in production environments.

## Gmail Functions

### Reading Emails

**Get recent emails:**
```
"Show me my recent emails from the last 24 hours"
```
- Calls: `get_recent_emails(count=20, hours_back=24)`
- Returns: List of recent emails with subjects, senders, and previews

**Search for specific emails:**
```
"Find emails about the house renovation project"
```
- Calls: `search_emails("house renovation", max_results=10)`
- Searches: Subject lines, sender names, and email content

**Get full email content:**
```
"Show me the full content of email ID abc123"
```
- Calls: `get_email_content("abc123")`
- Returns: Complete email with headers and content

### Creating Emails

**Draft a new email:**
```
"Draft an email to john@example.com about tomorrow's meeting"
```
- Calls: `create_draft(to="john@example.com", subject="...", body="...")`
- Creates draft in Gmail for you to review and send

**Reply to an email:**
```
"Create a reply to message ID xyz789 saying I'll attend"
```
- Calls: `create_draft_reply(message_id="xyz789", body="...")`
- Creates reply draft with proper threading

## Calendar Functions

### Viewing Calendar Information

**List all calendars:**
```
"What calendars do I have access to?"
```
- Calls: `get_calendars()`
- Shows: All calendars with read/write permissions

**View upcoming events:**
```
"What's on my calendar this week?"
```
- Calls: `get_upcoming_events(days_ahead=7)`
- Returns: Events from all visible calendars

**Filter by specific calendar:**
```
"Show me family events this weekend"
```
- Calls: `get_upcoming_events(days_ahead=3, calendar_names="family")`
- Filters: Only events from calendars matching "family"

### Event Details

**Get comprehensive event information:**
```
"Show me details for event ID event_123"
```
- Calls: `get_event_details("event_123")`
- Returns: Full event details including attendees and description

### Creating Events

**Simple event creation:**
```
"Create a dentist appointment tomorrow at 2 PM"
```
- Calls: `create_event_smart("Dentist appointment", "tomorrow 2 PM")`
- Uses: Default duration (1 hour) and primary calendar

**Event with specific calendar:**
```
"Add Sarah's birthday party to my family calendar this Saturday 2-4 PM"
```
- Calls: `create_event_smart("Sarah's birthday party", "this Saturday 2 PM", "this Saturday 4 PM", calendar_hint="family")`
- Smart matching: Finds calendar containing "family"

**Event with full details:**
```
"Create a project meeting next Tuesday 10 AM to 11 AM in Conference Room A"
```
- Calls: `create_event_smart("Project meeting", "next Tuesday 10 AM", "next Tuesday 11 AM", location="Conference Room A")`

### Searching Events

**Find past events:**
```
"Find all my dentist appointments from the last 6 months"
```
- Calls: `search_calendar_events("dentist", days_back=180, days_ahead=0)`
- Searches: Event titles, descriptions, and locations

**Search with calendar filter:**
```
"Look for birthday parties in my family calendar"
```
- Calls: `search_calendar_events("birthday", calendar_names="family")`
- Limits: Search to family-related calendars only

### Daily Schedule

**Morning briefing:**
```
"What's my schedule for today?"
```
- Calls: `get_todays_schedule()`
- Shows: Current events, imminent events, all-day events, and upcoming events
- Includes: Helpful warnings for events starting soon

## Contacts Functions

### Searching Contacts

**Search by name:**
```
"Find all contacts named John"
```
- Calls: `search_contacts("John", max_results=10)`
- Returns: Contacts matching the name with basic information

**Search by organization:**
```
"Show me all contacts from ABC Company"
```
- Calls: `search_contacts("ABC Company", max_results=10)`
- Searches: Name, email, phone, and organization fields

### Contact Lookup

**Find contact by email:**
```
"Who is john.smith@example.com in my contacts?"
```
- Calls: `lookup_contact_by_email("john.smith@example.com")`
- Returns: Complete contact information if found

**Get detailed contact info:**
```
"Show me all details for contact ID people/c1234567890"
```
- Calls: `get_contact_details("people/c1234567890")`
- Returns: Comprehensive contact details including all fields

### Contact Management

**List recent contacts:**
```
"Show me my recently added contacts"
```
- Calls: `list_recent_contacts(limit=20)`
- Returns: Recently modified contacts with basic information

**Create a new contact:**
```
"Add Jane Doe to my contacts with email jane@example.com"
```
- Calls: `create_contact("Jane Doe", "jane@example.com", phone="+1234567890", organization="Example Corp")`
- Includes: Automatic duplicate detection and warning

## Google Tasks Functions

### Task List Management

**View all task lists:**
```
"Show me all my task lists"
```
- Calls: `get_task_lists()`
- Returns: All available task lists with their IDs and titles

**View tasks in a specific list:**
```
"Show me tasks in my default task list"
```
- Calls: `get_tasks("@default", show_completed=False)`
- Returns: Active tasks with titles, due dates, and notes

**View completed tasks:**
```
"Show me completed tasks from last week"
```
- Calls: `get_tasks("@default", show_completed=True)`
- Returns: Both active and completed tasks

### Task Creation and Management

**Create a simple task:**
```
"Add 'Review quarterly report' to my tasks"
```
- Calls: `create_task("@default", "Review quarterly report")`
- Creates: Task in default list without due date

**Create task with due date:**
```
"Add 'Submit expense report' to my tasks, due Friday"
```
- Calls: `create_task("@default", "Submit expense report", due_date="Friday")`
- Accepts: Natural language dates and ISO format

**Create task with smart list selection:**
```
"Add 'Buy groceries' to my personal tasks"
```
- Calls: `create_task_with_smart_list_selection("Buy groceries", list_hint="personal")`
- Smart matching: Finds task lists containing "personal"

### Task Updates

**Mark task as complete:**
```
"Mark task 'Review quarterly report' as completed"
```
- Calls: `mark_task_complete("list_id", "task_id")`
- Updates: Task status to completed

**Update task details:**
```
"Update task 'Submit report' to be due tomorrow with note 'Include Q3 data'"
```
- Calls: `update_task("list_id", "task_id", due_date="tomorrow", notes="Include Q3 data")`
- Modifies: Due date and notes while preserving other fields

**Clear completed tasks:**
```
"Clean up my completed tasks"
```
- Calls: `clear_completed_tasks("@default")`
- Hides: All completed tasks from default view (doesn't delete them)

## Google Drive Functions

### File Management

**Search for files:**
```
"Find all PDF files in my Drive"
```
- Calls: `search_drive("type:pdf", max_results=20)`
- Uses: Drive query syntax for precise searches

**Advanced search examples:**
```
# Simple text search (auto-converted to proper syntax)
search_drive("test document")  # → name contains 'test document'

# File type searches
search_drive("type:pdf")          # All PDF files
search_drive("type:image")        # All images
search_drive("type:spreadsheet")  # All spreadsheets

# Name-based searches
search_drive("name contains 'report'")     # Files with 'report' in name
search_drive("name = 'Budget 2024'")      # Exact name match

# Date-based searches
search_drive("modifiedTime > '2024-01-01'")           # Modified after date
search_drive("createdTime < '2024-12-31'")            # Created before date

# Size and ownership
search_drive("name contains 'large' and not me in owners")  # Shared large files
search_drive("starred")                                     # Starred files

# Folder searches
search_drive("mimeType='application/vnd.google-apps.folder'")  # Folders only

# Combined searches  
search_drive("type:pdf and modifiedTime > '2024-06-01'")  # Recent PDFs
```

**List files in root folder:**
```
"Show me files in my Drive root folder"
```
- Calls: `list_drive_folder()`
- Returns: Files and folders in root directory with organized display

**Browse a specific folder:**
```
"Show me what's in my Documents folder"
```
- Calls: `list_drive_folder("Documents")`
- Smart search: Finds folder by name and lists contents

**Get file details:**
```
"Show me details for file ID abc123xyz"
```
- Calls: `get_drive_file_details("abc123xyz")`
- Returns: Comprehensive file information including size, dates, and links

### File Downloads and Uploads

**Download a file:**
```
"Download file ID xyz789 as 'important-document.pdf'"
```
- Calls: `download_drive_file("xyz789", "important-document.pdf")`
- Downloads: To local Open-WebUI storage with size limits

**Upload a local file:**
```
"Upload /path/to/file.txt to my Drive"
```
- Calls: `upload_file_to_drive("/path/to/file.txt")`
- Uploads: To Drive root or specified folder with progress tracking

**Upload to specific folder:**
```
"Upload /path/to/document.pdf to my Work folder"
```
- Calls: `upload_file_to_drive("/path/to/document.pdf", "folder_id")`
- Organized: Places file in designated folder structure

### Folder Management

**Create a new folder:**
```
"Create a folder called 'Project Alpha' in my Drive"
```
- Calls: `create_drive_folder("Project Alpha")`
- Creates: New folder in root directory

**Create nested folders:**
```
"Create a 'Q4 Reports' folder inside my 'Finance' folder"
```
- Calls: `create_drive_folder("Q4 Reports", "finance_folder_id")`
- Hierarchical: Maintains organized folder structure

**List all folders:**
```
"Show me all my Drive folders"
```
- Calls: `get_drive_folders()`
- Returns: All top-level folders with modification dates

### Email Attachment Integration

**Upload all email attachments:**
```
"Upload all attachments from email ID email123 to Drive"
```
- Calls: `upload_attachments_to_drive("email123", folder_strategy="auto")`
- Smart organization: Automatically categorizes by email content

**Upload with manual folder selection:**
```
"Upload attachments from email email456 to my Tax Documents folder"
```
- Calls: `upload_attachments_to_drive("email456", folder_strategy="manual", target_folder="Tax Documents/2024")`
- Organized: Places files in specific folder path

**Upload single attachment:**
```
"Upload the first attachment from email email789 to my Invoices folder"
```
- Calls: `upload_attachment_to_drive("email789", "0", target_folder="Invoices")`
- Selective: Upload specific attachment by index

### Storage Management

**Check storage usage:**
```
"How much Drive storage am I using?"
```
- Calls: `get_drive_storage_info()`
- Returns: Detailed storage quota with usage breakdown and visual bar

## Advanced Usage Patterns

### Cross-Service Workflows

**Email to Calendar:**
```
"Find emails about the Johnson project and create a follow-up meeting"
```
1. `search_emails("Johnson project")`
2. `create_event_smart("Johnson project follow-up", "tomorrow 3 PM")`

**Calendar Planning:**
```
"Check my availability next week and suggest meeting times"
```
1. `get_upcoming_events(days_ahead=7)`
2. AI analyzes gaps and suggests free time slots

**Contact-Enhanced Email:**
```
"Look up contact details for john@company.com and draft a professional email"
```
1. `lookup_contact_by_email("john@company.com")`
2. `create_draft()` using the contact's full name and organization

**Meeting Contacts Integration:**
```
"Find Sarah's contact info and schedule a meeting with her"
```
1. `search_contacts("Sarah", max_results=5)`
2. `get_contact_details()` for the specific Sarah
3. `create_event_smart()` using her contact information

**Email Attachments to Drive:**
```
"Save all tax documents from my recent emails to Drive"
```
1. `search_emails("tax OR invoice OR receipt", max_results=10)`
2. For each email with attachments: `upload_attachments_to_drive(email_id, folder_strategy="auto")`
3. Auto-organization: Places files in appropriate folders (Tax Documents, Invoices, etc.)

**Email to Tasks:**
```
"Convert action items from my project emails into tasks"
```
1. `search_emails("project review action items")`
2. `get_email_content()` to extract action items
3. `create_task()` for each action item with appropriate due dates

**Calendar to Tasks:**
```
"Create follow-up tasks for all my meetings this week"
```
1. `get_upcoming_events(days_ahead=7)`
2. For each meeting: `create_task()` with follow-up actions
3. Auto-scheduling: Set task due dates based on meeting dates

**Drive Organization Workflow:**
```
"Organize my email attachments by type and create folder structure"
```
1. `search_emails("has:attachment", max_results=20)`
2. `upload_attachments_to_drive()` with "type-organized" strategy
3. `get_drive_folders()` to verify organized structure

### Productivity Workflows

**Daily Planning:**
```
"Give me my daily briefing and highlight urgent items"
```
- `get_todays_schedule()` provides prioritized view
- Highlights events starting soon
- Shows completion status

**Email Triage:**
```
"Show me important emails and help me prioritize responses"
```
- `get_recent_emails()` gets latest emails
- AI analyzes importance and urgency
- Suggests response priorities

## Configuration Tips

### Timezone Settings
Set your timezone in tool settings for accurate event creation and scheduling:
- **Europe/London** for UK
- **America/New_York** for US East Coast  
- **Asia/Tokyo** for Japan
- **Australia/Sydney** for Australia

✅ **Timezone handling is fully working** - Events are created in your local timezone and displayed correctly.

### Calendar Name Matching
The tool uses fuzzy matching for calendar names:
- "family" matches "Family Calendar", "Greeff Family", etc.
- "work" matches "Work Calendar", "Work Events", etc.
- Use descriptive calendar names for better AI recognition

### Email Content Limits
Default limits prevent token overflow:
- Email content: 2000 characters
- Event descriptions: 300 characters
- Contact display fields: customizable
- Task results: 50 per query
- Adjust in settings if needed

### Drive Configuration
Configure Drive settings for optimal file management:
- **drive_default_folder**: Base folder for uploads ("Open-WebUI Attachments")
- **max_drive_file_size_mb**: Upload size limit (100MB default)
- **drive_organization_strategy**: "hybrid", "manual", or "auto"
- **drive_folder_structure**: "email-organized", "date-organized", or "type-organized"

### Tasks Configuration
Customize task management behavior:
- **default_task_list_name**: Preferred list for new tasks
- **max_task_results**: Limit for task queries (50 default)
- **show_completed_by_default**: Include completed tasks in listings

## Troubleshooting

### Authentication Issues

**"Not authenticated" errors:**
1. Run `get_authentication_status()` to check status
2. If expired, re-run authentication setup
3. Ensure Google Cloud APIs are still enabled

### Permission Errors

**"Permission denied" for calendar creation:**
- You may only have read access to some calendars
- Use `get_calendars()` to see which calendars allow editing
- Shared calendars often have restricted permissions

### Function Not Working

**Functions returning errors:**
1. Enable debug mode in tool settings
2. Check the exact error message
3. Verify API quotas in Google Cloud Console
4. Ensure your Google account has access to the services

### Performance Issues

**Slow responses:**
- Large calendars may take time to process
- Reduce `days_ahead` or `days_back` parameters
- Use calendar filtering to limit scope

### Common Mistakes

**Date format issues:**
- Use natural language: "tomorrow 2 PM", "next Monday"
- Or ISO format: "2024-01-15 14:30"
- Avoid ambiguous formats like "01/02/24"

**Calendar not found:**
- Use `get_calendars()` to see exact names
- Calendar names are case-insensitive but must contain the hint
- Shared calendars may have different names than expected

**Drive search issues:**
- Simple quoted searches like `"document"` are auto-converted to `name contains 'document'`
- Use `type:pdf` instead of `mimeType='application/pdf'` for easier syntax
- Date searches need quotes: `modifiedTime > '2024-01-01'` not `modifiedTime > 2024-01-01`
- For exact matches use `name = 'filename'`, for partial use `name contains 'text'`

## Getting More Help

For additional support:
1. Check the [authentication guide](authentication.md) for setup issues
2. Review the [installation guide](installation.md) for dependency problems  
3. Enable debug mode to see detailed error messages
4. Consult the Google API documentation for quota and permission details