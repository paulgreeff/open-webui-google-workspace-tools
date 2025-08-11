# Open-WebUI Google Workspace Tools

Comprehensive Google Workspace integration for Open-WebUI, enabling AI assistants to intelligently manage your digital productivity with Gmail and Calendar functionality.

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

### 🎯 AI-Powered Features
- **Smart calendar selection**: "Add to family calendar" automatically finds the right calendar
- **Intelligent date parsing**: Accepts "tomorrow 2pm", "next Friday", ISO dates, and natural language
- **Tiered information display**: Basic info by default, detailed info on request
- **Permission-aware operations**: Only shows writable calendars for event creation
- **Cross-service workflows**: Convert emails to calendar events seamlessly

## Current Functionality

### Gmail Functions
- `get_recent_emails()` - Fetch recent emails with filtering options
- `search_emails()` - Search emails using Gmail syntax  
- `get_email_content()` - Get full email content with headers
- `create_draft()` - Create draft emails with optional reply threading
- `create_draft_reply()` - Smart reply drafts with proper message threading

### Calendar Functions
- `get_calendars()` - List all calendars with access permissions
- `get_upcoming_events()` - View events with smart calendar filtering
- `get_event_details()` - Comprehensive event information with attendees
- `create_event_smart()` - Create events with AI calendar selection
- `search_calendar_events()` - Search events with relevance ranking
- `get_todays_schedule()` - Daily briefings with priority categorization

## Quick Start

### 1. Installation
```bash
# Install required dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil

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
- **enabled_services**: Comma-separated list (default: "gmail,calendar")
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
- **Google Tasks**: Todo management and task automation  
- **Google Docs/Sheets**: Document creation and spreadsheet automation
- **Google Contacts**: Contact lookup and management
- **Multi-user support**: Enterprise-ready user isolation and admin controls

### Future Integrations
- **Cross-service automation**: Advanced workflows between Gmail, Calendar, and Drive
- **AI-powered insights**: Intelligent analysis of communication patterns and schedule optimization
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This tool requires Google Workspace or personal Google account access. It uses official Google APIs and follows Google's security best practices for OAuth2 authentication.