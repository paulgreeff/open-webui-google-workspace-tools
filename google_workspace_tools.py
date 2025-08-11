"""
Google Workspace Tools for Open-WebUI
Comprehensive Google Workspace integration enabling AI assistants to manage Gmail, Calendar, Drive, and more
"""

import os
import json
import base64
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import email
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError as e:
    logging.error(f"Google API libraries not available: {e}")

class Tools:
    """Google Workspace Integration Tool for Open-WebUI"""
    
    def __init__(self):
        self.valves = self.Valves()
        self.gmail_service = None
        self.data_dir = "/app/backend/data"
        self.google_dir = os.path.join(self.data_dir, "google_tools")
        self.ensure_directories()
        
    class Valves(BaseModel):
        """Configuration settings for Google Workspace Tools"""
        
        # Authentication Settings
        credentials_json: str = Field(
            default="",
            description="Paste your Google OAuth2 credentials JSON content here (from Google Cloud Console)"
        )
        
        auth_status: str = Field(
            default="❌ Not authenticated",
            description="Current authentication status (read-only)"
        )
        
        auth_code: str = Field(
            default="",
            description="Paste authorization code here after visiting auth URL"
        )
        
        # Feature Configuration
        enabled_services: str = Field(
            default="gmail,calendar",
            description="Enabled Google services (comma-separated): gmail,calendar,drive,tasks"
        )
        
        # Gmail Settings
        default_email_count: int = Field(
            default=20,
            description="Default number of recent emails to fetch"
        )
        
        default_hours_back: int = Field(
            default=24,
            description="Default hours to look back for 'recent' emails"
        )
        
        max_email_content_chars: int = Field(
            default=2000,
            description="Maximum characters of email content to return (prevent token overflow)"
        )
        
        # Calendar Settings
        user_timezone: str = Field(
            default="Europe/London",
            description="Your timezone (e.g., Europe/London, America/New_York, Asia/Tokyo). Used for event creation and display."
        )
        
        default_event_duration_hours: int = Field(
            default=1,
            description="Default duration in hours for events when not specified"
        )
        
        max_event_description_chars: int = Field(
            default=300,
            description="Maximum characters in event descriptions before truncation"
        )
        
        default_calendar_name: str = Field(
            default="",
            description="Name of your default calendar for event creation (leave empty for primary calendar)"
        )
        
        # Debug Settings
        debug_mode: bool = Field(
            default=False,
            description="Enable detailed debug logging"
        )
        
        # Setup Workflow
        setup_step: str = Field(
            default="step1_credentials",
            description="Current setup step (step1_credentials, step2_auth, step3_complete)"
        )

    def ensure_directories(self):
        """Create necessary directories for data storage"""
        try:
            os.makedirs(self.google_dir, exist_ok=True)
            if self.valves.debug_mode:
                self.log_debug(f"Google Workspace tools directory ensured: {self.google_dir}")
        except Exception as e:
            self.log_error(f"Failed to create directories: {e}")

    def log_debug(self, message: str):
        """Debug logging when enabled"""
        if self.valves.debug_mode:
            print(f"[Google Workspace Tools Debug] {message}")

    def log_error(self, message: str):
        """Error logging"""
        print(f"[Google Workspace Tools Error] {message}")

    def get_credentials_path(self) -> str:
        """Get path for credentials file"""
        return os.path.join(self.google_dir, "credentials.json")

    def get_token_path(self) -> str:
        """Get path for token file"""
        return os.path.join(self.google_dir, "token.json")

    def get_scopes(self) -> List[str]:
        """Generate required scopes based on enabled services"""
        scope_mapping = {
            'gmail': [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.compose',
                'https://www.googleapis.com/auth/gmail.modify'
            ],
            'calendar': ['https://www.googleapis.com/auth/calendar'],
            'drive': [
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive.readonly'
            ],
            'tasks': ['https://www.googleapis.com/auth/tasks'],
            'contacts': ['https://www.googleapis.com/auth/contacts.readonly']
        }
        
        enabled = [s.strip() for s in self.valves.enabled_services.split(',')]
        scopes = []
        for service in enabled:
            if service in scope_mapping:
                scopes.extend(scope_mapping[service])
        
        return list(set(scopes))  # Remove duplicates

    def setup_authentication(self) -> str:
        """Start the authentication setup process"""
        try:
            if not self.valves.credentials_json.strip():
                return """
🔐 **Step 1: Google Cloud Credentials Required**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Gmail API (and other APIs you want)
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Desktop Application"
6. Download the credentials JSON file
7. **Copy the entire JSON content and paste it in the 'credentials_json' field above**

Then click this function again to continue setup.
                """

            # Save credentials to file
            credentials_path = self.get_credentials_path()
            try:
                creds_data = json.loads(self.valves.credentials_json)
                with open(credentials_path, 'w') as f:
                    json.dump(creds_data, f, indent=2)
                self.log_debug(f"Credentials saved to {credentials_path}")
            except json.JSONDecodeError:
                return "❌ **Error**: Invalid JSON in credentials field. Please check the format."

            # Generate authorization URL
            scopes = self.get_scopes()
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            
            # Use out-of-band flow for headless environments
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # Generate auth URL
            auth_url = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )[0]

            return f"""
🔐 **Step 2: Authorization Required**

**Enabled Services**: {self.valves.enabled_services}

1. **Click this link**: {auth_url}
2. Sign in to your Google account
3. Grant permissions to the application
4. **Copy the authorization code** from the success page
5. **Paste the code in the 'auth_code' field above**
6. Click 'Complete Authentication' below

**Next**: Use the `complete_authentication()` function after pasting the auth code.
            """

        except Exception as e:
            self.log_error(f"Setup authentication failed: {e}")
            return f"❌ **Setup failed**: {str(e)}"

    def complete_authentication(self) -> str:
        """Complete the authentication using the provided auth code"""
        try:
            if not self.valves.auth_code.strip():
                return "❌ **Error**: Please provide the authorization code in the 'auth_code' field first."

            credentials_path = self.get_credentials_path()
            if not os.path.exists(credentials_path):
                return "❌ **Error**: Credentials not found. Please run setup_authentication() first."

            # Exchange auth code for tokens
            scopes = self.get_scopes()
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # Manually fetch token with auth code (out-of-band flow)
            flow.fetch_token(code=self.valves.auth_code.strip())
            creds = flow.credentials

            # Save token
            token_path = self.get_token_path()
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())

            # Update auth status
            self.valves.auth_status = "✅ Authenticated"
            self.valves.setup_step = "step3_complete"
            
            self.log_debug("Authentication completed successfully")
            
            return """
🎉 **Authentication Complete!**

✅ Google account connected successfully
✅ Tokens saved and ready for use
✅ Gmail tool is now ready

**You can now use Gmail functions:**
- `get_recent_emails()` - Get recent emails
- `search_emails()` - Search your emails
- `get_email_content()` - Get full email content
- `create_draft()` - Create draft emails

**Try asking**: "Show me my recent important emails"
            """

        except Exception as e:
            self.log_error(f"Complete authentication failed: {e}")
            return f"❌ **Authentication failed**: {str(e)}"

    def get_authenticated_service(self, service_name: str = 'gmail', version: str = 'v1'):
        """Get authenticated Google service"""
        try:
            token_path = self.get_token_path()
            if not os.path.exists(token_path):
                return None, "❌ Not authenticated. Run setup_authentication() first."

            creds = Credentials.from_authorized_user_file(token_path, self.get_scopes())

            # Refresh token if expired
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(token_path, 'w') as token_file:
                        token_file.write(creds.to_json())
                    self.log_debug("Token refreshed successfully")
                else:
                    return None, "❌ Token expired and cannot be refreshed. Please re-authenticate."

            service = build(service_name, version, credentials=creds)
            return service, "✅ Authenticated"

        except Exception as e:
            self.log_error(f"Authentication failed: {e}")
            return None, f"❌ Authentication error: {str(e)}"

    def get_recent_emails(self, count: Optional[int] = None, hours_back: Optional[int] = None) -> str:
        """
        Get recent emails from Gmail inbox
        
        Args:
            count: Number of emails to fetch (default from settings)
            hours_back: Hours to look back (default from settings)
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            count = count or self.valves.default_email_count
            hours_back = hours_back or self.valves.default_hours_back

            # Calculate date filter
            since_time = datetime.now() - timedelta(hours=hours_back)
            since_timestamp = int(since_time.timestamp())

            # Search for recent emails
            query = f'in:inbox after:{since_timestamp}'
            
            self.log_debug(f"Searching emails with query: {query}")
            
            # Get email list
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=count
            ).execute()

            messages = results.get('messages', [])
            
            if not messages:
                return f"📧 No emails found in the last {hours_back} hours."

            # Get email details
            emails = []
            for msg in messages[:count]:
                try:
                    email_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date', 'To']
                    ).execute()

                    headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
                    
                    emails.append({
                        'id': msg['id'],
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown Sender'),
                        'date': headers.get('Date', 'Unknown Date'),
                        'snippet': email_data.get('snippet', '')[:200],
                        'unread': 'UNREAD' in email_data.get('labelIds', [])
                    })
                    
                except Exception as e:
                    self.log_error(f"Failed to get email {msg['id']}: {e}")
                    continue

            # Format response
            response = f"📧 **Recent Emails** (last {hours_back} hours, {len(emails)} found):\n\n"
            
            for i, email in enumerate(emails, 1):
                unread_indicator = "🔵" if email['unread'] else "⚪"
                response += f"{i}. {unread_indicator} **{email['subject']}**\n"
                response += f"   From: {email['from']}\n"
                response += f"   Date: {email['date']}\n"
                response += f"   Preview: {email['snippet']}...\n"
                response += f"   ID: `{email['id']}`\n\n"

            response += "\n💡 Use `get_email_content('email_id')` to read full content of any email."
            
            return response

        except Exception as e:
            self.log_error(f"Get recent emails failed: {e}")
            return f"❌ **Error getting emails**: {str(e)}"

    def search_emails(self, query: str, max_results: int = 10) -> str:
        """
        Search emails using Gmail search syntax
        
        Args:
            query: Gmail search query (e.g., "from:someone@email.com", "subject:urgent")
            max_results: Maximum number of results to return
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Searching emails with query: {query}")

            # Search emails
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            
            if not messages:
                return f"📧 No emails found for query: '{query}'"

            # Get email details
            emails = []
            for msg in messages:
                try:
                    email_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date']
                    ).execute()

                    headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
                    
                    emails.append({
                        'id': msg['id'],
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown Sender'),
                        'date': headers.get('Date', 'Unknown Date'),
                        'snippet': email_data.get('snippet', '')[:200]
                    })
                    
                except Exception as e:
                    self.log_error(f"Failed to get email {msg['id']}: {e}")
                    continue

            # Format response
            response = f"🔍 **Search Results** for '{query}' ({len(emails)} found):\n\n"
            
            for i, email in enumerate(emails, 1):
                response += f"{i}. **{email['subject']}**\n"
                response += f"   From: {email['from']}\n"
                response += f"   Date: {email['date']}\n"
                response += f"   Preview: {email['snippet']}...\n"
                response += f"   ID: `{email['id']}`\n\n"

            response += "\n💡 Use `get_email_content('email_id')` to read full content."
            
            return response

        except Exception as e:
            self.log_error(f"Search emails failed: {e}")
            return f"❌ **Error searching emails**: {str(e)}"

    def get_email_content(self, email_id: str) -> str:
        """
        Get full content of a specific email
        
        Args:
            email_id: Gmail message ID
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Getting content for email: {email_id}")

            # Get full email
            email_data = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
            
            # Extract body content
            body = self._extract_email_body(email_data['payload'])
            
            # Truncate if too long
            if len(body) > self.valves.max_email_content_chars:
                body = body[:self.valves.max_email_content_chars] + "\n\n[Content truncated...]"

            # Format response
            response = f"📧 **Email Content**\n\n"
            response += f"**Subject**: {headers.get('Subject', 'No Subject')}\n"
            response += f"**From**: {headers.get('From', 'Unknown')}\n"
            response += f"**To**: {headers.get('To', 'Unknown')}\n"
            response += f"**Date**: {headers.get('Date', 'Unknown')}\n"
            response += f"**Message ID**: `{email_id}`\n\n"
            response += "**Content**:\n"
            response += f"{body}\n"

            return response

        except Exception as e:
            self.log_error(f"Get email content failed: {e}")
            return f"❌ **Error getting email content**: {str(e)}"

    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract text content from email payload"""
        try:
            body = ""
            
            if 'parts' in payload:
                # Multi-part email
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html' and not body:
                        # Fallback to HTML if no plain text
                        if 'data' in part['body']:
                            body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            else:
                # Single part email
                if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif payload['mimeType'] == 'text/html' and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            return body.strip()

        except Exception as e:
            self.log_error(f"Extract email body failed: {e}")
            return "Error extracting email content"

    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation without regex"""
        # Simple validation - check for @ symbol and basic format
        email = email.strip()
        if not email or '@' not in email:
            return False
        
        parts = email.split('@')
        if len(parts) != 2:
            return False
            
        local, domain = parts
        if not local or not domain:
            return False
            
        # Check domain has at least one dot
        if '.' not in domain:
            return False
            
        return True

    def create_draft(self, to: str, subject: str, body: str, reply_to_id: Optional[str] = None) -> str:
        """
        Create a draft email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            reply_to_id: Optional message ID to reply to
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            # Clean and validate email address
            to_email = to.strip()
            if not self._is_valid_email(to_email):
                return f"❌ **Invalid email address**: '{to_email}'. Please provide a valid email address."

            self.log_debug(f"Creating draft to: {to_email}, subject: {subject}")

            # Create message using email.mime
            message = MIMEText(body, 'plain', 'utf-8')
            message['To'] = to_email
            message['Subject'] = subject
            
            # Get sender email from profile
            try:
                profile = service.users().getProfile(userId='me').execute()
                sender_email = profile.get('emailAddress', '')
                if sender_email:
                    message['From'] = sender_email
            except Exception as e:
                self.log_debug(f"Could not get sender email: {e}")
            
            if reply_to_id:
                try:
                    # Get original message for proper threading
                    original = service.users().messages().get(
                        userId='me', 
                        id=reply_to_id,
                        format='metadata',
                        metadataHeaders=['Message-ID', 'Subject', 'References', 'In-Reply-To']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in original['payload'].get('headers', [])}
                    
                    # Set threading headers
                    if headers.get('Message-ID'):
                        message['In-Reply-To'] = headers['Message-ID']
                        # Build references chain
                        references = headers.get('References', '')
                        if references:
                            message['References'] = f"{references} {headers['Message-ID']}"
                        else:
                            message['References'] = headers['Message-ID']
                    
                    # Update subject for reply
                    original_subject = headers.get('Subject', '')
                    if original_subject and not original_subject.lower().startswith('re:'):
                        message.replace_header('Subject', f"Re: {original_subject}")
                        
                    self.log_debug(f"Reply threading set up for message {reply_to_id}")
                    
                except Exception as e:
                    self.log_error(f"Failed to set up reply threading: {e}")
                    # Continue without threading

            # Convert to raw format
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create draft
            draft_body = {
                'message': {
                    'raw': raw_message
                }
            }

            self.log_debug(f"Creating draft with raw message length: {len(raw_message)}")
            
            draft = service.users().drafts().create(userId='me', body=draft_body).execute()
            
            draft_id = draft['id']
            message_id = draft.get('message', {}).get('id', 'Unknown')
            
            self.log_debug(f"Draft created successfully: {draft_id}")
            
            # Verify draft was created by trying to retrieve it
            try:
                verify_draft = service.users().drafts().get(userId='me', id=draft_id).execute()
                self.log_debug(f"Draft verification successful: {verify_draft['id']}")
            except Exception as e:
                self.log_error(f"Draft verification failed: {e}")
                return f"⚠️ **Draft created but verification failed**: ID {draft_id}. Check your Gmail drafts folder."
            
            response = f"✅ **Draft Created Successfully**\n\n"
            response += f"**To**: {to_email}\n"
            response += f"**Subject**: {subject}\n"
            response += f"**Draft ID**: `{draft_id}`\n"
            response += f"**Message ID**: `{message_id}`\n\n"
            response += "📧 The draft has been saved to your Gmail Drafts folder. "
            response += "You can find it in Gmail → Drafts to review and send."
            
            if reply_to_id:
                response += f"\n🔗 This is a reply to message: `{reply_to_id}`"

            return response

        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            self.log_error(f"Gmail API error creating draft: {error_details}")
            
            if "Invalid To header" in str(e):
                return f"❌ **Invalid email format**: '{to}'. Please check the email address format."
            elif "insufficientPermissions" in str(e):
                return f"❌ **Permission denied**: Your account may not have permission to create drafts."
            else:
                return f"❌ **Gmail API error**: {str(e)}"
                
        except Exception as e:
            self.log_error(f"Create draft failed: {e}")
            return f"❌ **Error creating draft**: {str(e)}"

    def get_calendars(self) -> str:
        """
        List all available calendars with read/write status
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            self.log_debug("Fetching calendar list")

            # Get calendar list
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            if not calendars:
                return "📅 **No calendars found**. Please check your Google Calendar access."

            response = f"📅 **Available Calendars** ({len(calendars)} found):\n\n"
            
            for i, calendar in enumerate(calendars, 1):
                calendar_id = calendar.get('id', 'Unknown ID')
                calendar_name = calendar.get('summary', 'Unnamed Calendar')
                access_role = calendar.get('accessRole', 'unknown')
                is_primary = calendar.get('primary', False)
                selected = calendar.get('selected', True)
                
                # Determine access level
                if access_role == 'owner':
                    access_icon = "👑"
                    access_desc = "Owner"
                elif access_role == 'writer':
                    access_icon = "✏️"
                    access_desc = "Read/Write"
                elif access_role == 'reader':
                    access_icon = "👁️"
                    access_desc = "Read-only"
                else:
                    access_icon = "❓"
                    access_desc = "Unknown access"
                
                # Primary calendar indicator
                primary_indicator = " (PRIMARY)" if is_primary else ""
                selected_indicator = "" if selected else " (Hidden)"
                
                response += f"{i}. {access_icon} **{calendar_name}**{primary_indicator}{selected_indicator}\n"
                response += f"   Access: {access_desc}\n"
                response += f"   ID: `{calendar_id}`\n\n"

            response += "💡 **Usage Tips:**\n"
            response += "- Use calendar names in `create_event_smart()` for easy event creation\n"
            response += "- Read-only calendars (👁️) cannot be modified\n"
            response += "- Primary calendar is your default Google Calendar"
            
            return response

        except Exception as e:
            self.log_error(f"Get calendars failed: {e}")
            return f"❌ **Error getting calendars**: {str(e)}"

    def get_upcoming_events(self, days_ahead: int = 7, calendar_names: Optional[str] = None) -> str:
        """
        Get upcoming events from specified calendars or all calendars
        
        Args:
            days_ahead: Number of days ahead to look for events
            calendar_names: Comma-separated calendar names to filter (optional)
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            # Calculate time range
            now = datetime.now()
            end_time = now + timedelta(days=days_ahead)
            
            # Format as RFC3339 timestamp
            time_min = now.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'
            
            self.log_debug(f"Getting events from {time_min} to {time_max}")

            # Get calendar list first
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            if not calendars:
                return "📅 **No calendars found**. Please check your Google Calendar access."

            # Filter calendars if names specified
            selected_calendars = []
            if calendar_names:
                filter_names = [name.strip().lower() for name in calendar_names.split(',')]
                for calendar in calendars:
                    calendar_name = calendar.get('summary', '').lower()
                    if any(filter_name in calendar_name for filter_name in filter_names):
                        selected_calendars.append(calendar)
            else:
                selected_calendars = [cal for cal in calendars if cal.get('selected', True)]
            
            if not selected_calendars:
                filter_msg = f" matching '{calendar_names}'" if calendar_names else ""
                return f"📅 **No calendars found{filter_msg}**. Use `get_calendars()` to see available calendars."

            # Collect events from all selected calendars
            all_events = []
            
            for calendar in selected_calendars:
                calendar_id = calendar['id']
                calendar_name = calendar.get('summary', 'Unknown')
                
                try:
                    # Get events for this calendar
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=50,  # Reasonable limit per calendar
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    for event in events:
                        # Add calendar context to each event
                        event['_calendar_name'] = calendar_name
                        event['_calendar_id'] = calendar_id
                        all_events.append(event)
                        
                except Exception as e:
                    self.log_error(f"Failed to get events from calendar '{calendar_name}': {e}")
                    continue

            if not all_events:
                calendar_list = ', '.join([cal.get('summary', 'Unknown') for cal in selected_calendars])
                return f"📅 **No upcoming events** in the next {days_ahead} days.\n**Searched calendars**: {calendar_list}"

            # Sort all events by start time
            all_events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))

            # Format response with basic info (tiered approach)
            response = f"📅 **Upcoming Events** (next {days_ahead} days, {len(all_events)} found):\n\n"
            
            for i, event in enumerate(all_events[:20], 1):  # Limit to 20 events
                title = event.get('summary', 'No Title')
                calendar_name = event.get('_calendar_name', 'Unknown Calendar')
                event_id = event.get('id', 'Unknown ID')
                
                # Parse start time
                start = event.get('start', {})
                if 'dateTime' in start:
                    # Timed event
                    start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    time_str = start_time.strftime("%a %d/%m, %H:%M")
                elif 'date' in start:
                    # All-day event
                    start_date = datetime.fromisoformat(start['date'])
                    time_str = start_date.strftime("%a %d/%m (All day)")
                else:
                    time_str = "Time unknown"
                
                # Attendee count
                attendees = event.get('attendees', [])
                attendee_count = len(attendees) if attendees else 0
                attendee_str = f" • {attendee_count} attendees" if attendee_count > 0 else ""
                
                response += f"{i}. **{title}**\n"
                response += f"   📅 {time_str} • {calendar_name}{attendee_str}\n"
                response += f"   ID: `{event_id}`\n\n"

            if len(all_events) > 20:
                response += f"... and {len(all_events) - 20} more events\n\n"
                
            response += "💡 Use `get_event_details('event_id')` to see full details of any event."
            
            return response

        except Exception as e:
            self.log_error(f"Get upcoming events failed: {e}")
            return f"❌ **Error getting upcoming events**: {str(e)}"

    def get_event_details(self, event_id: str, calendar_id: Optional[str] = None) -> str:
        """
        Get full details of a specific event
        
        Args:
            event_id: Google Calendar event ID
            calendar_id: Optional calendar ID (will search all calendars if not provided)
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            self.log_debug(f"Getting details for event: {event_id}")

            event = None
            found_calendar_name = None
            
            if calendar_id:
                # Try the specific calendar
                try:
                    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
                    # Get calendar name
                    calendar_info = service.calendars().get(calendarId=calendar_id).execute()
                    found_calendar_name = calendar_info.get('summary', 'Unknown Calendar')
                except Exception as e:
                    self.log_debug(f"Event not found in specified calendar {calendar_id}: {e}")
            else:
                # Search all calendars
                calendar_list = service.calendarList().list().execute()
                calendars = calendar_list.get('items', [])
                
                for calendar in calendars:
                    try:
                        event = service.events().get(calendarId=calendar['id'], eventId=event_id).execute()
                        found_calendar_name = calendar.get('summary', 'Unknown Calendar')
                        break
                    except Exception:
                        continue

            if not event:
                return f"❌ **Event not found**: `{event_id}`. Please check the event ID or calendar access."

            # Extract comprehensive event details
            title = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            status = event.get('status', 'confirmed')
            
            # Time information
            start = event.get('start', {})
            end = event.get('end', {})
            
            if 'dateTime' in start and 'dateTime' in end:
                # Timed event
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                time_str = f"{start_time.strftime('%A, %d %B %Y at %H:%M')} - {end_time.strftime('%H:%M')}"
                duration = end_time - start_time
                duration_str = f"Duration: {duration}"
            elif 'date' in start:
                # All-day event
                start_date = datetime.fromisoformat(start['date'])
                if 'date' in end:
                    end_date = datetime.fromisoformat(end['date']) - timedelta(days=1)  # End date is exclusive
                    if start_date == end_date:
                        time_str = f"{start_date.strftime('%A, %d %B %Y')} (All day)"
                    else:
                        time_str = f"{start_date.strftime('%A, %d %B %Y')} - {end_date.strftime('%A, %d %B %Y')} (All day)"
                else:
                    time_str = f"{start_date.strftime('%A, %d %B %Y')} (All day)"
                duration_str = "All day event"
            else:
                time_str = "Time unknown"
                duration_str = "Duration unknown"

            # Attendees information
            attendees = event.get('attendees', [])
            organizer = event.get('organizer', {})
            
            # Creator information
            creator = event.get('creator', {})
            created = event.get('created', '')
            updated = event.get('updated', '')

            # Build detailed response
            response = f"📅 **Event Details**\n\n"
            response += f"**Title**: {title}\n"
            response += f"**Calendar**: {found_calendar_name}\n"
            response += f"**Time**: {time_str}\n"
            response += f"**{duration_str}**\n"
            response += f"**Status**: {status.title()}\n\n"

            if location:
                response += f"**📍 Location**: {location}\n\n"

            if description:
                # Truncate description if too long
                if len(description) > self.valves.max_event_description_chars:
                    truncated_desc = description[:self.valves.max_event_description_chars] + "..."
                    response += f"**📝 Description**: {truncated_desc}\n\n"
                    response += f"*[Description truncated at {self.valves.max_event_description_chars} characters]*\n\n"
                else:
                    response += f"**📝 Description**: {description}\n\n"

            # Organizer
            if organizer:
                organizer_name = organizer.get('displayName', organizer.get('email', 'Unknown'))
                response += f"**👤 Organizer**: {organizer_name}\n"

            # Attendees
            if attendees:
                response += f"**👥 Attendees** ({len(attendees)}):\n"
                for attendee in attendees[:10]:  # Limit to 10 attendees
                    name = attendee.get('displayName', attendee.get('email', 'Unknown'))
                    status = attendee.get('responseStatus', 'needsAction')
                    status_emoji = {
                        'accepted': '✅',
                        'declined': '❌', 
                        'tentative': '❓',
                        'needsAction': '⏳'
                    }.get(status, '❓')
                    response += f"  {status_emoji} {name}\n"
                
                if len(attendees) > 10:
                    response += f"  ... and {len(attendees) - 10} more attendees\n"
                response += "\n"

            # Metadata
            if creator.get('email'):
                response += f"**Created by**: {creator.get('displayName', creator.get('email'))}\n"
            
            response += f"**Event ID**: `{event_id}`\n"

            return response

        except Exception as e:
            self.log_error(f"Get event details failed: {e}")
            return f"❌ **Error getting event details**: {str(e)}"

    def get_authentication_status(self) -> str:
        """Check current authentication status"""
        try:
            token_path = self.get_token_path()
            if not os.path.exists(token_path):
                return "❌ **Not authenticated**. Run `setup_authentication()` to get started."

            service, status = self.get_authenticated_service('gmail', 'v1')
            if service:
                # Test the connection
                profile = service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress', 'Unknown')
                
                return f"✅ **Authenticated as**: {email_address}\n**Services**: {self.valves.enabled_services}"
            else:
                return status

        except Exception as e:
            return f"❌ **Authentication error**: {str(e)}"

# Available functions for the LLM to call
def setup_authentication() -> str:
    """Start Google Workspace authentication setup process"""
    tool = Tools()
    return tool.setup_authentication()

def complete_authentication() -> str:
    """Complete Google Workspace authentication with auth code"""
    tool = Tools()
    return tool.complete_authentication()

def get_authentication_status() -> str:
    """Check current Google Workspace authentication status"""
    tool = Tools()
    return tool.get_authentication_status()

def get_recent_emails(count: int = 20, hours_back: int = 24) -> str:
    """Get recent emails from Gmail inbox"""
    tool = Tools()
    return tool.get_recent_emails(count, hours_back)

def search_emails(query: str, max_results: int = 10) -> str:
    """Search emails using Gmail search syntax"""
    tool = Tools()
    return tool.search_emails(query, max_results)

def get_email_content(email_id: str) -> str:
    """Get full content of a specific email by ID"""
    tool = Tools()
    return tool.get_email_content(email_id)

def create_draft(to: str, subject: str, body: str, reply_to_id: str = None) -> str:
    """Create a draft email"""
    tool = Tools()
    return tool.create_draft(to, subject, body, reply_to_id)

def create_draft_reply(message_id: str, body: str) -> str:
    """Create a draft reply to a specific email message"""
    tool = Tools()
    
    try:
        # Get the original email to extract recipient info
        service, auth_status = tool.get_authenticated_service('gmail', 'v1')
        if not service:
            return auth_status
            
        # Get original message details
        original = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['Subject', 'From', 'To', 'Message-ID']
        ).execute()
        
        headers = {h['name']: h['value'] for h in original['payload'].get('headers', [])}
        
        # Extract reply-to address (sender of original message)
        from_header = headers.get('From', '')
        # Simple email extraction from "Name <email@domain.com>" format
        if '<' in from_header and '>' in from_header:
            reply_to = from_header.split('<')[1].split('>')[0].strip()
        else:
            reply_to = from_header.strip()
            
        # Generate reply subject
        original_subject = headers.get('Subject', '')
        if original_subject and not original_subject.lower().startswith('re:'):
            reply_subject = f"Re: {original_subject}"
        else:
            reply_subject = original_subject or "Re: (No Subject)"
            
        tool.log_debug(f"Creating reply draft to {reply_to} for message {message_id}")
        
        # Use the main create_draft function with reply parameters
        return tool.create_draft(reply_to, reply_subject, body, message_id)
        
    except Exception as e:
        tool.log_error(f"Create draft reply failed: {e}")
        return f"❌ **Error creating reply draft**: {str(e)}"

# Calendar functions
def get_calendars() -> str:
    """List all available calendars with read/write status"""
    tool = Tools()
    return tool.get_calendars()

def get_upcoming_events(days_ahead: int = 7, calendar_names: str = None) -> str:
    """Get upcoming events from specified calendars or all calendars"""
    tool = Tools()
    return tool.get_upcoming_events(days_ahead, calendar_names)

def get_event_details(event_id: str, calendar_id: str = None) -> str:
    """Get full details of a specific event by ID"""
    tool = Tools()
    return tool.get_event_details(event_id, calendar_id)
      
