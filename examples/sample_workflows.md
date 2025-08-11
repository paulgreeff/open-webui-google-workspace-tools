# Sample Workflows

Real-world examples of how to use Google Workspace Tools for common productivity scenarios.

## Daily Productivity Workflows

### Morning Routine
**Scenario**: Start your day with a comprehensive overview

**Workflow**:
```
1. "What's my schedule for today?"
   → get_todays_schedule()
   
2. "Show me important emails from the last 12 hours"
   → get_recent_emails(count=15, hours_back=12)
   
3. "Any urgent emails I should respond to first?"
   → AI analyzes email content and priorities
```

**Result**: Complete daily briefing with schedule and email priorities

### Weekly Planning
**Scenario**: Plan your upcoming week

**Workflow**:
```
1. "Show me next week's calendar events"
   → get_upcoming_events(days_ahead=7)
   
2. "Find any scheduling conflicts or busy days"
   → AI analyzes event density
   
3. "When do I have 2-hour blocks free for focused work?"
   → AI identifies gaps between meetings
```

**Result**: Weekly overview with identified focus time opportunities

## Email Management Workflows

### Email Cleanup and Organization
**Scenario**: Triage and organize your inbox

**Workflow**:
```
1. "Show me emails from the last 3 days"
   → get_recent_emails(count=30, hours_back=72)
   
2. "Which emails need urgent responses?"
   → AI categorizes by urgency and importance
   
3. "Draft replies for the urgent ones"
   → create_draft() for each priority email
```

### Project Communication
**Scenario**: Follow up on project-related communications

**Workflow**:
```
1. "Find all emails about the Johnson project"
   → search_emails("Johnson project")
   
2. "Get full details of the most recent Johnson email"
   → get_email_content(email_id)
   
3. "Create a follow-up meeting about Johnson project next week"
   → create_event_smart("Johnson project follow-up", "next Tuesday 2 PM")
```

## Calendar Management Workflows

### Meeting Coordination
**Scenario**: Schedule meetings across multiple calendars

**Workflow**:
```
1. "Show me all my calendars"
   → get_calendars()
   
2. "What's my availability next week?"
   → get_upcoming_events(days_ahead=7)
   
3. "Schedule team meeting next Thursday 10 AM in work calendar"
   → create_event_smart("Team meeting", "next Thursday 10 AM", calendar_hint="work")
   
4. "Add family dinner to personal calendar Saturday 7 PM"
   → create_event_smart("Family dinner", "Saturday 7 PM", calendar_hint="family")
```

### Event Research
**Scenario**: Find and review past events

**Workflow**:
```
1. "Find all doctor appointments from the last 6 months"
   → search_calendar_events("doctor", days_back=180)
   
2. "Show details of my last dentist appointment"
   → get_event_details(event_id)
   
3. "When is my next scheduled medical appointment?"
   → search_calendar_events("doctor OR dentist OR medical", days_ahead=90)
```

## Cross-Service Integration Workflows

### Email-to-Calendar Conversion
**Scenario**: Convert email invitations or requests to calendar events

**Workflow**:
```
1. "Find emails with meeting requests from this week"
   → search_emails("meeting OR appointment OR schedule")
   
2. "Show me the content of email abc123"
   → get_email_content("abc123")
   
3. "Create a calendar event based on this meeting request"
   → create_event_smart(title, time, location) extracted from email
   
4. "Draft confirmation reply"
   → create_draft_reply(email_id, "Confirmed - added to calendar")
```

### Travel Planning
**Scenario**: Organize travel-related information

**Workflow**:
```
1. "Find all emails about my London trip"
   → search_emails("London trip OR London travel")
   
2. "Show me travel-related calendar events for next month"
   → search_calendar_events("travel OR flight OR hotel", days_ahead=30)
   
3. "Create calendar reminders for trip preparation"
   → create_event_smart("Pack for London trip", "day before departure")
```

### Document Collection
**Scenario**: Gather information for tax preparation or legal matters

**Workflow**:
```
1. "Find all emails containing invoices from 2024"
   → search_emails("invoice OR receipt OR payment", days_back=365)
   
2. "Look for tax-related appointments this year"
   → search_calendar_events("tax OR accountant OR CPA", days_back=365)
   
3. "Create reminder to organize tax documents"
   → create_event_smart("Organize tax documents", "next Friday 2 PM")
```

## Family and Personal Management

### Family Coordination
**Scenario**: Manage family schedules and activities

**Workflow**:
```
1. "What's on our family calendar this weekend?"
   → get_upcoming_events(days_ahead=3, calendar_names="family")
   
2. "Add kids' soccer practice to family calendar"
   → create_event_smart("Kids soccer practice", "Saturday 9 AM", calendar_hint="family")
   
3. "Find family birthday events coming up"
   → search_calendar_events("birthday", calendar_names="family")
```

### Health and Wellness Tracking
**Scenario**: Keep track of health appointments and activities

**Workflow**:
```
1. "Show me all medical appointments from this year"
   → search_calendar_events("doctor OR dentist OR medical OR therapy")
   
2. "When was my last gym session?"
   → search_calendar_events("gym OR workout OR exercise", days_back=14)
   
3. "Schedule next quarterly health checkup"
   → create_event_smart("Health checkup", "first Tuesday next month 10 AM")
```

## Business and Professional Workflows

### Client Management
**Scenario**: Track client interactions and follow-ups

**Workflow**:
```
1. "Find all emails from Smith Corporation"
   → search_emails("Smith Corporation OR smith@company.com")
   
2. "Show me meetings with Smith Corp from last quarter"
   → search_calendar_events("Smith", days_back=90)
   
3. "Schedule quarterly review with Smith Corp"
   → create_event_smart("Smith Corp quarterly review", "next month", calendar_hint="work")
```

### Project Deadline Tracking
**Scenario**: Monitor project timelines and deadlines

**Workflow**:
```
1. "Find all project-related events this month"
   → search_calendar_events("project OR deadline OR milestone")
   
2. "What project emails need follow-up?"
   → search_emails("project status OR deliverable OR deadline")
   
3. "Create milestone review meetings"
   → create_event_smart("Project milestone review", "every Friday 3 PM")
```

## Advanced Automation Workflows

### Weekly Review Process
**Scenario**: Automated weekly productivity review

**Workflow**:
```
1. "Analyze my calendar utilization last week"
   → get_upcoming_events(days_back=7, days_ahead=0)
   
2. "Find action items from last week's emails"
   → search_emails("action item OR follow up OR TODO", days_back=7)
   
3. "Plan focus blocks for next week"
   → Analyze calendar gaps and create_event_smart() for focus time
```

### Event Preparation Automation
**Scenario**: Automatically create preparation tasks

**Workflow**:
```
1. "Find important meetings next week"
   → get_upcoming_events(days_ahead=7)
   
2. "For each meeting, create preparation time"
   → create_event_smart("Prep for [meeting]", "30 minutes before")
   
3. "Set up follow-up tasks"
   → create_event_smart("Follow up on [meeting]", "day after meeting")
```

## Troubleshooting Workflows

### Sync and Consistency Checks
**Scenario**: Verify data consistency between email and calendar

**Workflow**:
```
1. "Find meeting invitations in email that aren't on calendar"
   → Cross-reference search_emails("meeting invite") with calendar events
   
2. "Check for calendar events without email confirmations"
   → Identify events that might need email follow-up
   
3. "Find duplicate or conflicting events"
   → Analyze overlapping time slots
```

## Customization Tips

### Workflow Optimization
- **Chain functions**: Use output from one function as input to another
- **Filter strategically**: Use calendar_names and time ranges to limit scope
- **Batch operations**: Group related tasks together for efficiency

### Error Handling
- Always check authentication status first
- Use get_calendars() to verify calendar access before creating events
- Enable debug mode for troubleshooting complex workflows

### Performance Considerations
- Limit search ranges for faster responses
- Use specific search terms rather than broad queries
- Cache frequently accessed information like calendar lists

These workflows demonstrate the powerful combinations possible when integrating Gmail and Calendar through AI assistance. Adapt them to your specific needs and create custom workflows for your unique productivity requirements.