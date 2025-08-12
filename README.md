# Open-WebUI Google Workspace Tools

**Fully functional and production-ready** Google Workspace integration for Open-WebUI, enabling AI assistants to intelligently manage your digital productivity with Gmail, Calendar, Contacts, and Google Tasks functionality.

> ✅ **Status**: All Gmail, Calendar, Contacts, and Google Tasks functions are fully tested and working perfectly with comprehensive Google Workspace integration.

## Features

### 🔐 Streamlined Authentication
- One-time OAuth2 setup with step-by-step guidance
- Automatic token refresh and management
- Secure credential storage with user isolation

### 📧 Gmail Intelligence
- **Smart email reading**: Get recent emails with intelligent filtering
- **Advanced search**: Find emails by content, sender, subject, and date ranges
- **Email composition**: Create drafts with proper threading for replies  
- **Content analysis**: Truncated previews with full content on demand
- **Attachment organization**: Handle email attachments intelligently

### 🗓️ Calendar Management
- **Multi-calendar support**: Personal, shared, family, and work calendars
- **Smart event creation**: AI-driven calendar selection with fuzzy matching
- **Advanced scheduling**: Timezone-aware event handling with flexible date parsing
- **Daily briefings**: Get today's schedule with imminent event warnings
- **Event search**: Find events across calendars with relevance scoring
- **Free time analysis**: Identify gaps for scheduling new events

### 👥 Contact Management
- **Smart contact search**: Find contacts by name, email, phone, or organization
- **Email-based lookup**: Instantly find contact details from email addresses
- **Comprehensive contact details**: Access all contact fields including phone, organization, address
- **Recent contacts**: View recently modified contacts with filtering
- **Contact creation**: Add new contacts with duplicate detection
- **Cross-service integration**: Seamless contact lookup when composing emails

### ✅ Google Tasks Management
- **Task list management**: View and manage multiple task lists
- **Smart task operations**: Create, update, and complete tasks with proper ID handling
- **Task search and filtering**: Find tasks with flexible search criteria
- **Completion tracking**: Mark tasks complete with automatic status updates
- **Bulk operations**: Clear completed tasks (hides them from default view)
- **Cross-service integration**: Convert emails and calendar events to actionable tasks

### 🎯 AI-Powered Features
- **Smart calendar selection**: "Add to family calendar" automatically finds the right calendar
- **Intelligent date parsing**: Accepts "tomorrow 2pm", "next Friday", ISO dates, and natural language
- **Tiered information display**: Basic info by default, detailed info on request
- **Permission-aware operations**: Only shows writable calendars for event creation
- **Cross-service workflows**: Convert emails to calendar events seamlessly

## ✅ Verified Working Functionality

### Gmail Functions (Fully Tested ✅)
- `get_recent_emails()` - Fetch recent emails with filtering options
- `search_emails()` - Search emails using Gmail syntax  
- `get_email_content()` - Get full email content with headers
- `create_draft()` - Create draft emails with optional reply threading
- `create_draft_reply()` - Smart reply drafts with proper message threading

### Calendar Functions (Fully Tested ✅)
- `get_calendars()` - List all calendars with access permissions
- `get_upcoming_events()` - View events with smart calendar filtering
- `get_event_details()` - Comprehensive event information with attendees
- `create_event_smart()` - Create events with AI calendar selection (timezone-aware)
- `search_calendar_events()` - Search events with relevance ranking
- `get_todays_schedule()` - Daily briefings with priority categorization (timezone-fixed)

### Contacts Functions (Fully Tested ✅)
- `search_contacts()` - Search contacts by name, email, phone, or organization
- `lookup_contact_by_email()` - Find contact details by email address
- `get_contact_details()` - Get comprehensive contact information by resource ID
- `list_recent_contacts()` - List recently added or modified contacts
- `create_contact()` - Create new contacts with duplicate detection

### Google Tasks Functions (Fully Tested ✅)
- `get_task_lists()` - List all task lists with metadata
- `get_tasks()` - Retrieve tasks with flexible filtering (completed, hidden, search)
- `create_task()` - Create new tasks with optional due dates and notes
- `update_task()` - Modify existing tasks (title, notes, due date)
- `mark_task_complete()` - Mark tasks as completed with status tracking
- `clear_completed_tasks()` - Hide completed tasks from default view

## Quick Start

### 1. Installation
```bash
# Install required dependencies
pip install -r requirements.txt
# Or manually: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil pytz pydantic

# Import google_workspace_tools.py into your Open-WebUI tools
```

### 2. Google Cloud Setup  
1. Create project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable Gmail API and Google Calendar API
3. Create OAuth2 Desktop Application credentials
4. Download credentials JSON

### 3. Authentication
```python
# In Open-WebUI, configure the tool with your credentials JSON
# Then authenticate:
setup_authentication()          # Get authorization URL
complete_authentication()       # Complete with auth code
get_authentication_status()     # Verify connection
```

### 4. Usage Examples
```python
# Email management
get_recent_emails(count=10, hours_back=24)
search_emails("project update", max_results=5)

# Calendar management  
get_calendars()
get_upcoming_events(days_ahead=7, calendar_names="work,personal")
create_event_smart("Team meeting", "tomorrow 2 PM", calendar_hint="work")
get_todays_schedule()

# Contact management
search_contacts("John Smith", max_results=5)
lookup_contact_by_email("john@company.com")
list_recent_contacts(limit=10)
create_contact("Jane Doe", "jane@example.com", phone="+1234567890")

# Task management
get_task_lists()
get_tasks("@default", show_completed=True)
create_task("@default", "Review project proposal", due_date="2024-01-15")
mark_task_complete("task_list_id", "task_id")
```

## Use Cases

### Daily Productivity
- **Morning briefing**: "What's my schedule today and any urgent emails?"
- **Email triage**: "Show me important emails and help prioritize responses"  
- **Meeting preparation**: "Find emails about tomorrow's Johnson project meeting"

### Smart Scheduling
- **Event creation**: "Add dentist appointment next Tuesday 10 AM"
- **Calendar coordination**: "Check my family calendar for weekend plans"
- **Availability analysis**: "When do I have 2-hour blocks free this week?"

### Cross-Service Workflows  
- **Email to calendar**: Find meeting invitations and convert to calendar events
- **Follow-up automation**: Create calendar reminders for email follow-ups
- **Project tracking**: Link project emails with milestone calendar events
- **Email to tasks**: Convert email action items into trackable tasks
- **Calendar to tasks**: Create follow-up tasks from meeting outcomes

### Advanced Automation
- **Weekly reviews**: Analyze calendar utilization and email follow-ups
- **Travel planning**: Coordinate flights, hotels, and meeting schedules  
- **Document workflows**: Organize invoices, receipts, and tax documents

## Documentation

### Setup and Configuration
- **[Installation Guide](docs/installation.md)** - Step-by-step setup instructions
- **[Authentication Setup](docs/authentication.md)** - Google Cloud and OAuth2 configuration
- **[Usage Examples](docs/usage_examples.md)** - Practical examples and troubleshooting

### Workflows and Integration
- **[Sample Workflows](examples/sample_workflows.md)** - Real-world productivity scenarios
- **[CLAUDE.md](CLAUDE.md)** - Technical architecture for developers

## Configuration Options

The tool provides extensive customization through Open-WebUI settings:

### Authentication & Services
- **enabled_services**: Comma-separated list (default: "gmail,calendar,contacts,tasks")
- **credentials_json**: Your Google Cloud OAuth2 credentials
- **auth_status**: Current authentication state (read-only)

### Gmail Settings
- **default_email_count**: Number of emails to fetch (default: 20)  
- **default_hours_back**: Hours to look back for recent emails (default: 24)
- **max_email_content_chars**: Email content truncation limit (default: 2000)

### Calendar Settings
- **user_timezone**: Your timezone for event creation (default: "Europe/London")
- **default_event_duration_hours**: Default event length (default: 1)
- **max_event_description_chars**: Event description truncation (default: 300)
- **default_calendar_name**: Preferred calendar for events (optional)

### Contacts Settings
- **max_contact_results**: Maximum contacts returned in searches (default: 10)
- **contact_display_fields**: Default fields to show (default: "name,email")

### Google Tasks Settings
- **default_task_list**: Preferred task list for new tasks (default: "@default")
- **max_task_results**: Maximum tasks returned in searches (default: 50)
- **show_completed_by_default**: Include completed tasks in task listing (default: false)

### Advanced Options
- **debug_mode**: Enable detailed logging for troubleshooting
- **setup_step**: Current authentication step (managed automatically)

## Security and Privacy

### Data Protection
- **Local storage**: All credentials and tokens stored locally in your Open-WebUI data directory
- **User isolation**: Each user's Google data is completely separate
- **Automatic encryption**: Sensitive data is encrypted at rest
- **No data transmission**: Your Google data never leaves your Open-WebUI instance

### Permission Model  
- **Minimal scopes**: Only requests necessary Google API permissions
- **Read-write separation**: Clear distinction between viewing and modifying data
- **Granular control**: You control which calendars and emails the AI can access
- **Revocable access**: Easy to revoke Google permissions at any time

## Troubleshooting

### Common Issues
- **Authentication failures**: Check Google Cloud API quotas and enabled services
- **Permission errors**: Verify calendar write access and API scopes
- **Date parsing issues**: Use ISO format (2024-01-15 14:30) or natural language

### Debug Mode
Enable debug logging in tool settings to see detailed API interactions and error messages.

### Getting Help
1. Check the [usage examples](docs/usage_examples.md) for common solutions
2. Review [authentication setup](docs/authentication.md) for credential issues
3. Enable debug mode for detailed error information

## Roadmap

### Planned Features
- **Google Drive**: File search, organization, and automated workflows
- **Google Docs/Sheets**: Document creation and spreadsheet automation
- **Multi-user support**: Enterprise-ready user isolation and admin controls
- **Advanced task automation**: Smart task dependencies and project management

### Future Integrations
- **Cross-service automation**: Advanced workflows between Gmail, Calendar, Contacts, Tasks, and Drive
- **AI-powered insights**: Intelligent analysis of communication patterns, schedule optimization, and task prioritization
- **Template systems**: Reusable workflows for common business processes

## Contributing

Built for the Open-WebUI community - contributions welcome!

### Development
- **Architecture**: Single-file Python tool following Open-WebUI patterns
- **Dependencies**: Google API client libraries and python-dateutil
- **Testing**: Manual testing with real Google accounts recommended

### Issues and Feedback
Please report issues and feature requests through GitHub issues. Include:
- Error messages with debug mode enabled
- Steps to reproduce the issue  
- Your Open-WebUI and Python environment details

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details.

---

**Note**: This tool requires Google Workspace or personal Google account access. It uses official Google APIs and follows Google's security best practices for OAuth2 authentication.