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
        self.drive_service = None
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
            default="gmail,calendar,contacts,tasks,drive",
            description="Enabled Google services (comma-separated): gmail,calendar,contacts,tasks,drive"
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
        
        # Contacts Settings
        max_contact_results: int = Field(
            default=10,
            description="Maximum number of contacts to return in search results"
        )
        
        contact_display_fields: str = Field(
            default="name,email",
            description="Default fields to display for contacts (comma-separated): name,email,phone,organization"
        )
        
        # Tasks Settings
        default_task_list_name: str = Field(
            default="",
            description="Name of your default task list for new tasks (leave empty for auto-detection)"
        )
        
        max_task_results: int = Field(
            default=20,
            description="Maximum number of tasks to return in listings"
        )
        
        task_display_fields: str = Field(
            default="title,due_date,status,notes",
            description="Default fields to display for tasks (comma-separated): title,due_date,status,notes"
        )
        
        show_completed_tasks_default: bool = Field(
            default=False,
            description="Whether to show completed tasks by default in task listings"
        )
        
        # Attachment Settings
        max_attachment_size_mb: int = Field(
            default=10,
            description="Maximum attachment size to download in MB (default 10MB)"
        )
        
        attachment_storage_dir: str = Field(
            default="attachments",
            description="Directory name for storing downloaded attachments (relative to google_tools directory)"
        )
        
        # Drive Settings
        drive_default_folder: str = Field(
            default="Open-WebUI Attachments",
            description="Default folder name for uploading attachments and files to Google Drive"
        )
        
        max_drive_file_size_mb: int = Field(
            default=100,
            description="Maximum file size for uploads to Google Drive in MB (default 100MB)"
        )
        
        drive_organization_strategy: str = Field(
            default="hybrid",
            description="Folder organization strategy: 'hybrid' (smart with manual override), 'manual' (user-specified), 'auto' (fully automatic)"
        )
        
        drive_folder_structure: str = Field(
            default="email-organized",
            description="Folder structure pattern: 'email-organized' (by sender/subject), 'date-organized' (by date), 'type-organized' (by file type)"
        )
        
        drive_storage_root: str = Field(
            default="",
            description="Root folder ID or name for all Open-WebUI file operations (leave empty for Drive root)"
        )
        
        # Smart Organizer Settings
        organizer_batch_size: int = Field(
            default=3,
            description="Emails per LLM batch call for attachment classification (1-10)"
        )
        
        organizer_email_context_chars: int = Field(
            default=1500,
            description="Maximum email body characters for LLM context"
        )
        
        organizer_enable_progress_logging: bool = Field(
            default=True,
            description="Show detailed progress in debug logs during organization"
        )
        
        # LLM Integration Settings
        llm_enabled: bool = Field(
            default=False,
            description="Enable AI-powered attachment classification"
        )
        
        llm_provider: str = Field(
            default="openai",
            description="LLM provider: 'openai', 'ollama', 'anthropic'"
        )
        
        llm_api_url: str = Field(
            default="",
            description="Custom LLM API endpoint (for Ollama/custom providers)"
        )
        
        llm_api_key: str = Field(
            default="",
            description="LLM API key (leave empty for local providers like Ollama)"
        )
        
        llm_model: str = Field(
            default="gpt-3.5-turbo",
            description="LLM model name (e.g., gpt-3.5-turbo, llama2, claude-3-haiku)"
        )
        
        llm_confidence_threshold: float = Field(
            default=0.7,
            description="Minimum confidence score for auto-upload (0.0-1.0)"
        )
        
        llm_timeout_seconds: int = Field(
            default=30,
            description="LLM API timeout in seconds"
        )
        
        llm_smart_folders: bool = Field(
            default=True,
            description="Enable LLM smart folder suggestions (when target_folder not specified)"
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
                'https://www.googleapis.com/auth/drive'
            ],
            'tasks': ['https://www.googleapis.com/auth/tasks'],
            'contacts': [
                'https://www.googleapis.com/auth/contacts.readonly',
                'https://www.googleapis.com/auth/contacts'
            ]
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

    def _get_drive_service(self):
        """Get authenticated Google Drive service"""
        if self.drive_service is None:
            service, status = self.get_authenticated_service('drive', 'v3')
            if service is None:
                return None, status
            self.drive_service = service
            self.log_debug("Drive service initialized")
        return self.drive_service, "✅ Drive service ready"

    def get_recent_emails(self, count: Optional[int] = None, hours_back: Optional[int] = None, show_attachments: bool = True) -> str:
        """
        Get recent emails from Gmail inbox
        
        Args:
            count: Number of emails to fetch (default from settings)
            hours_back: Hours to look back (default from settings)
            show_attachments: Whether to show attachment indicators (default True)
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
                    # Get email format based on attachment detection needs
                    email_format = 'full' if show_attachments else 'metadata'
                    metadata_headers = ['Subject', 'From', 'Date', 'To'] if not show_attachments else None
                    
                    email_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format=email_format,
                        metadataHeaders=metadata_headers
                    ).execute()

                    headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
                    
                    email_info = {
                        'id': msg['id'],
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown Sender'),
                        'date': headers.get('Date', 'Unknown Date'),
                        'snippet': email_data.get('snippet', '')[:200],
                        'unread': 'UNREAD' in email_data.get('labelIds', [])
                    }
                    
                    # Add attachment information if requested
                    if show_attachments:
                        try:
                            attachments = self._detect_attachments(email_data['payload'])
                            if attachments:
                                total_size = sum(att.get('size', 0) for att in attachments)
                                email_info['attachment_count'] = len(attachments)
                                email_info['attachment_size'] = total_size
                            else:
                                email_info['attachment_count'] = 0
                                email_info['attachment_size'] = 0
                        except Exception as e:
                            self.log_debug(f"Failed to detect attachments for email {msg['id']}: {e}")
                            email_info['attachment_count'] = 0
                            email_info['attachment_size'] = 0
                    
                    emails.append(email_info)
                    
                except Exception as e:
                    self.log_error(f"Failed to get email {msg['id']}: {e}")
                    continue

            # Format response
            response = f"📧 **Recent Emails** (last {hours_back} hours, {len(emails)} found):\n\n"
            
            for i, email in enumerate(emails, 1):
                unread_indicator = "🔵" if email['unread'] else "⚪"
                
                # Add attachment indicator if enabled and attachments exist
                attachment_indicator = ""
                if show_attachments and email.get('attachment_count', 0) > 0:
                    count = email['attachment_count']
                    size = email['attachment_size']
                    size_str = self._format_file_size(size) if size > 0 else "unknown size"
                    attachment_indicator = f" 📎 {count} file{'s' if count != 1 else ''} ({size_str})"
                
                response += f"{i}. {unread_indicator} **{email['subject']}**{attachment_indicator}\n"
                response += f"   From: {email['from']}\n"
                response += f"   Date: {email['date']}\n"
                response += f"   Preview: {email['snippet']}...\n"
                response += f"   ID: `{email['id']}`\n\n"

            # Add helpful tips
            tips = ["💡 Use `get_email_content('email_id')` to read full content of any email."]
            if show_attachments:
                tips.append("📎 Use `list_email_attachments('email_id')` to see attachment details.")
            
            response += "\n" + "\n".join(tips)
            
            return response

        except Exception as e:
            self.log_error(f"Get recent emails failed: {e}")
            return f"❌ **Error getting emails**: {str(e)}"

    def search_emails(self, query: str, max_results: int = 10, show_attachments: bool = True) -> str:
        """
        Search emails using Gmail search syntax
        
        Args:
            query: Gmail search query (e.g., "from:someone@email.com", "subject:urgent", "has:attachment")
            max_results: Maximum number of results to return
            show_attachments: Whether to show attachment indicators (default True)
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
                    # Get email format based on attachment detection needs
                    email_format = 'full' if show_attachments else 'metadata'
                    metadata_headers = ['Subject', 'From', 'Date'] if not show_attachments else None
                    
                    email_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format=email_format,
                        metadataHeaders=metadata_headers
                    ).execute()

                    headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
                    
                    email_info = {
                        'id': msg['id'],
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown Sender'),
                        'date': headers.get('Date', 'Unknown Date'),
                        'snippet': email_data.get('snippet', '')[:200]
                    }
                    
                    # Add attachment information if requested
                    if show_attachments:
                        try:
                            attachments = self._detect_attachments(email_data['payload'])
                            if attachments:
                                total_size = sum(att.get('size', 0) for att in attachments)
                                email_info['attachment_count'] = len(attachments)
                                email_info['attachment_size'] = total_size
                            else:
                                email_info['attachment_count'] = 0
                                email_info['attachment_size'] = 0
                        except Exception as e:
                            self.log_debug(f"Failed to detect attachments for email {msg['id']}: {e}")
                            email_info['attachment_count'] = 0
                            email_info['attachment_size'] = 0
                    
                    emails.append(email_info)
                    
                except Exception as e:
                    self.log_error(f"Failed to get email {msg['id']}: {e}")
                    continue

            # Format response
            response = f"🔍 **Search Results** for '{query}' ({len(emails)} found):\n\n"
            
            for i, email in enumerate(emails, 1):
                # Add attachment indicator if enabled and attachments exist
                attachment_indicator = ""
                if show_attachments and email.get('attachment_count', 0) > 0:
                    count = email['attachment_count']
                    size = email['attachment_size']
                    size_str = self._format_file_size(size) if size > 0 else "unknown size"
                    attachment_indicator = f" 📎 {count} file{'s' if count != 1 else ''} ({size_str})"
                
                response += f"{i}. **{email['subject']}**{attachment_indicator}\n"
                response += f"   From: {email['from']}\n"
                response += f"   Date: {email['date']}\n"
                response += f"   Preview: {email['snippet']}...\n"
                response += f"   ID: `{email['id']}`\n\n"

            # Add helpful tips
            tips = ["💡 Use `get_email_content('email_id')` to read full content."]
            if show_attachments:
                tips.append("📎 Use `list_email_attachments('email_id')` to see attachment details.")
            tips.append("🔍 **Search tip**: Use 'has:attachment' to find emails with attachments.")
            
            response += "\n" + "\n".join(tips)
            
            return response

        except Exception as e:
            self.log_error(f"Search emails failed: {e}")
            return f"❌ **Error searching emails**: {str(e)}"

    def get_email_content(self, email_id: str = None, subject_contains: str = None, from_sender: str = None) -> str:
        """
        Get full content of a specific email - supports smart searching
        
        Args:
            email_id: Gmail message ID (if provided, other params ignored)
            subject_contains: Search for emails containing this text in subject
            from_sender: Search for emails from this sender
            
        Note: Can combine subject_contains and from_sender for precise matching
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            # Smart email resolution
            if not email_id and (subject_contains or from_sender):
                # Search for emails using smart criteria
                matching_emails = self._search_emails_smart(subject_contains, from_sender, max_results=5)
                
                if not matching_emails:
                    search_desc = []
                    if subject_contains:
                        search_desc.append(f"subject containing '{subject_contains}'")
                    if from_sender:
                        search_desc.append(f"from '{from_sender}'")
                    return f"📧 **No emails found** matching criteria: {' and '.join(search_desc)}"
                
                elif len(matching_emails) == 1:
                    # Perfect match - use this email
                    email_id = matching_emails[0]['id']
                    self.log_debug(f"🎯 Smart resolution: Found single match for email_id: {email_id}")
                
                else:
                    # Multiple matches - show options
                    search_desc = []
                    if subject_contains:
                        search_desc.append(f"subject containing '{subject_contains}'")
                    if from_sender:
                        search_desc.append(f"from '{from_sender}'")
                    
                    response = f"📧 **Found {len(matching_emails)} emails** matching criteria: {' and '.join(search_desc)}\n\n"
                    response += "**Please be more specific or use email ID:**\n"
                    
                    for i, email in enumerate(matching_emails, 1):
                        response += f"{i}. **'{email['subject']}'**\n"
                        response += f"   From: {email['sender']}\n"
                        response += f"   Date: {email['date']}\n"
                        response += f"   ID: `{email['id']}`\n\n"
                    
                    response += "**Usage**: `get_email_content('email_id')` or use more specific search criteria."
                    return response
            
            elif not email_id:
                return "❌ **Missing parameter**: Please provide either email_id or search criteria (subject_contains/from_sender)"

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

            # Detect attachments
            attachments = self._detect_attachments(email_data['payload'])
            
            # Format response
            response = f"📧 **Email Content**\n\n"
            response += f"**Subject**: {headers.get('Subject', 'No Subject')}\n"
            response += f"**From**: {headers.get('From', 'Unknown')}\n"
            response += f"**To**: {headers.get('To', 'Unknown')}\n"
            response += f"**Date**: {headers.get('Date', 'Unknown')}\n"
            response += f"**Message ID**: `{email_id}`\n\n"
            response += "**Content**:\n"
            response += f"{body}\n"
            
            # Add attachment summary
            if attachments:
                response += f"\n📎 **Attachments** ({len(attachments)} file{'s' if len(attachments) != 1 else ''}):\n"
                total_size = 0
                for i, attachment in enumerate(attachments, 1):
                    filename = attachment['filename']
                    size = attachment.get('size', 0)
                    mime_type = attachment['mime_type']
                    size_str = self._format_file_size(size) if size > 0 else "unknown size"
                    total_size += size
                    
                    response += f"{i}. **{filename}** ({size_str}) - {mime_type}\n"
                
                total_size_str = self._format_file_size(total_size) if total_size > 0 else "unknown total size"
                response += f"\n**Total attachment size**: {total_size_str}\n"
                response += f"\n💡 **Attachment actions**:\n"
                response += f"• Use `list_email_attachments('{email_id}')` for detailed attachment info\n"
                response += f"• Use `extract_all_attachments('{email_id}')` to download all attachments\n"
                response += f"• Use `download_email_attachment('{email_id}', 'attachment_id')` for specific files"
            else:
                response += f"\n📎 **No attachments** found in this email."

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

    def _get_attachments_from_email_id(self, email_id: str) -> List[Dict[str, Any]]:
        """Get attachments from email ID by fetching email data first"""
        try:
            self.log_debug(f"📎 Getting attachments for email ID: {email_id}")
            
            # Get Gmail service
            service, status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                self.log_error(f"Gmail service not available: {status}")
                return []
            
            # Get email data with full payload
            email_data = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            payload = email_data.get('payload', {})
            self.log_debug(f"📎 Email payload keys: {list(payload.keys())}")
            
            return self._detect_attachments(payload)
            
        except Exception as e:
            self.log_error(f"Get attachments from email ID failed: {e}")
            return []

    def _detect_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect and extract attachment metadata from email payload"""
        try:
            self.log_debug(f"📎 Detecting attachments in payload with keys: {list(payload.keys()) if isinstance(payload, dict) else 'Not a dict!'}")
            
            if not isinstance(payload, dict):
                self.log_error(f"📎 ERROR: payload is not a dict, it's a {type(payload)}: {str(payload)[:100]}")
                return []
            attachments = []
            
            def process_part(part: Dict[str, Any], part_index: int = 0):
                """Recursively process email parts to find attachments"""
                self.log_debug(f"📎 Processing part {part_index}: {type(part)} with keys: {list(part.keys()) if isinstance(part, dict) else 'Not a dict!'}")
                
                if not isinstance(part, dict):
                    self.log_error(f"📎 ERROR: part is not a dict, it's a {type(part)}: {str(part)[:100]}")
                    return
                
                filename = None
                attachment_id = None
                size = 0
                mime_type = part.get('mimeType', 'unknown')
                self.log_debug(f"📎 Part {part_index} MIME type: {mime_type}")
                
                # Check if this part has a filename (indicates attachment)
                headers = part.get('headers', [])
                for header in headers:
                    if header.get('name', '').lower() == 'content-disposition':
                        disposition = header.get('value', '')
                        if 'attachment' in disposition.lower() or 'filename=' in disposition.lower():
                            # Extract filename from Content-Disposition header
                            import re
                            filename_match = re.search(r'filename[*]?=([^;]+)', disposition)
                            if filename_match:
                                filename = filename_match.group(1).strip('"\'')
                
                # Also check part filename directly
                if not filename:
                    filename = part.get('filename')
                
                # Get attachment ID and size from body
                body = part.get('body', {})
                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']
                    size = body.get('size', 0)
                elif 'data' in body and filename:
                    # Small attachment with inline data
                    size = body.get('size', len(body.get('data', '')))
                
                # If we have a filename or attachment ID, this is likely an attachment
                if filename or attachment_id:
                    # Skip common inline content that shouldn't be treated as attachments
                    if mime_type.startswith('text/') and not filename:
                        return
                    
                    attachment_info = {
                        'filename': filename or f'attachment_{part_index}',
                        'mime_type': mime_type,
                        'size': size,
                        'attachment_id': attachment_id,
                        'inline_data': body.get('data') if not attachment_id else None,
                        'part_index': part_index
                    }
                    attachments.append(attachment_info)
                    return
                
                # Recursively process sub-parts
                if 'parts' in part:
                    for i, sub_part in enumerate(part['parts']):
                        process_part(sub_part, len(attachments))
            
            # Start processing from the root payload
            if 'parts' in payload:
                for i, part in enumerate(payload['parts']):
                    process_part(part, len(attachments))
            else:
                # Single part message - check if it's an attachment
                process_part(payload, 0)
            
            self.log_debug(f"Detected {len(attachments)} attachments")
            return attachments
            
        except Exception as e:
            self.log_error(f"Detect attachments failed: {e}")
            return []

    def _get_attachment_data(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """Fetch attachment data from Gmail API"""
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                self.log_error(f"Authentication failed: {auth_status}")
                return None

            self.log_debug(f"Fetching attachment {attachment_id} from message {message_id}")

            # Get attachment data
            attachment = service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            # Decode base64 data
            data = attachment.get('data', '')
            if data:
                attachment_data = base64.urlsafe_b64decode(data)
                self.log_debug(f"Successfully fetched attachment, size: {len(attachment_data)} bytes")
                return attachment_data
            else:
                self.log_error("No data found in attachment response")
                return None

        except Exception as e:
            self.log_error(f"Get attachment data failed: {e}")
            return None

    def _save_attachment(self, attachment_data: bytes, filename: str, message_id: str) -> Optional[str]:
        """Save attachment data to disk with organized structure"""
        try:
            # Create attachment directory structure
            attachment_dir = os.path.join(self.google_dir, self.valves.attachment_storage_dir)
            message_dir = os.path.join(attachment_dir, message_id)
            os.makedirs(message_dir, exist_ok=True)
            
            # Sanitize filename
            import re
            safe_filename = re.sub(r'[^\w\s.-]', '_', filename)
            safe_filename = re.sub(r'\s+', '_', safe_filename)
            
            # Create full file path
            file_path = os.path.join(message_dir, safe_filename)
            
            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while os.path.exists(file_path):
                name, ext = os.path.splitext(safe_filename)
                file_path = os.path.join(message_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            # Write attachment data
            with open(file_path, 'wb') as f:
                f.write(attachment_data)
            
            self.log_debug(f"Saved attachment to: {file_path}")
            return file_path
            
        except Exception as e:
            self.log_error(f"Save attachment failed: {e}")
            return None

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        i = min(i, len(size_names) - 1)
        p = math.pow(1024, i)
        s = round(size_bytes / p, 1)
        return f"{s} {size_names[i]}"

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

    # Smart Parameter Resolvers
    def _resolve_task_list_id(self, identifier: str) -> str:
        """Convert task list name to ID if needed"""
        try:
            # If it looks like an ID already, return as-is
            if len(identifier) > 40 or identifier.startswith('@') or identifier.count('_') > 2:
                return identifier
            
            # Search by name
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return identifier  # Fallback to original
                
            task_lists = service.tasklists().list().execute()
            for task_list in task_lists.get('items', []):
                title = task_list.get('title', '').lower()
                if identifier.lower() in title:
                    self.log_debug(f"Resolved task list '{identifier}' to ID: {task_list['id']}")
                    return task_list['id']
            
            return identifier  # Fallback if no match found
        except Exception as e:
            self.log_debug(f"Error resolving task list ID: {e}")
            return identifier  # Fallback

    def _resolve_attachment_identifier(self, email_id: str, identifier: str) -> str:
        """Convert attachment name/position to index"""
        try:
            # If it's already an integer index, return as string
            if isinstance(identifier, int):
                return str(identifier)
            
            if identifier.isdigit():
                return identifier
            
            # Handle position words
            position_map = {
                'first': '0', 'second': '1', 'third': '2', 'fourth': '3', 'fifth': '4',
                'last': None,  # Will be resolved below
                '1st': '0', '2nd': '1', '3rd': '2', '4th': '3', '5th': '4'
            }
            
            if identifier.lower() in position_map:
                if identifier.lower() == 'last':
                    # Get attachments to find last index
                    attachments = self._get_attachments_from_email_id(email_id)
                    if attachments:
                        return str(len(attachments) - 1)
                    return '0'
                return position_map[identifier.lower()]
            
            # Find by filename (partial match)
            attachments = self._get_attachments_from_email_id(email_id)
            for i, att in enumerate(attachments):
                filename = att.get('filename', '').lower()
                if identifier.lower() in filename:
                    self.log_debug(f"Resolved attachment '{identifier}' to index: {i}")
                    return str(i)
            
            return identifier  # Fallback
        except Exception as e:
            self.log_debug(f"Error resolving attachment identifier: {e}")
            return identifier  # Fallback

    def _search_emails_smart(self, subject_contains: str = None, from_sender: str = None, max_results: int = 5) -> List[Dict]:
        """Search emails with smart criteria"""
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return []
            
            # Build search query
            query_parts = []
            if subject_contains:
                query_parts.append(f'subject:"{subject_contains}"')
            if from_sender:
                query_parts.append(f'from:{from_sender}')
            
            query = ' AND '.join(query_parts) if query_parts else ''
            
            # Search emails
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            email_list = []
            
            for msg in messages:
                # Get basic info for each email
                email_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata'
                ).execute()
                
                headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
                
                email_list.append({
                    'id': msg['id'],
                    'subject': headers.get('Subject', 'No Subject'),
                    'sender': headers.get('From', 'Unknown'),
                    'date': headers.get('Date', 'Unknown')
                })
            
            return email_list
        except Exception as e:
            self.log_debug(f"Error in smart email search: {e}")
            return []

    def _resolve_drive_file_id(self, identifier: str) -> str:
        """Convert filename to file ID if needed"""
        try:
            # If it looks like a Drive file ID already, return as-is
            if len(identifier) > 25 and not ' ' in identifier and not '.' in identifier:
                return identifier
            
            # Search by name
            service, auth_status = self.get_authenticated_service('drive', 'v3')
            if not service:
                return identifier
            
            # Search for files with name containing the identifier
            query = f"name contains '{identifier}' and trashed = false"
            results = service.files().list(q=query, pageSize=5).execute()
            files = results.get('files', [])
            
            if len(files) == 1:
                self.log_debug(f"Resolved file '{identifier}' to ID: {files[0]['id']}")
                return files[0]['id']
            elif len(files) > 1:
                # Multiple matches - return special marker to trigger disambiguation
                return f"MULTIPLE_MATCHES:{identifier}"
            
            return identifier  # No matches, fallback
        except Exception as e:
            self.log_debug(f"Error resolving Drive file ID: {e}")
            return identifier

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

    def create_event_smart(self, title: str, start_time: str, end_time: str = None, 
                          calendar_hint: Optional[str] = None, description: Optional[str] = None, 
                          location: Optional[str] = None) -> str:
        """
        Create an event with smart calendar selection
        
        Args:
            title: Event title
            start_time: Start time (various formats supported)
            end_time: End time (optional, uses default duration if not provided)
            calendar_hint: Calendar name hint for fuzzy matching (optional)
            description: Event description (optional)
            location: Event location (optional)
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            self.log_debug(f"Creating smart event: {title}")

            # Parse and validate times with timezone awareness
            try:
                from dateutil.parser import parse
                import pytz
                
                # Get user timezone
                try:
                    user_tz = pytz.timezone(self.valves.user_timezone)
                except:
                    user_tz = pytz.UTC
                    self.log_debug(f"Using UTC timezone (invalid timezone: {self.valves.user_timezone})")
                
                # Parse start time
                start_dt = parse(start_time)
                # If naive, localize to user timezone
                if start_dt.tzinfo is None:
                    start_dt = user_tz.localize(start_dt)
                
                if end_time:
                    end_dt = parse(end_time)
                    # If naive, localize to user timezone
                    if end_dt.tzinfo is None:
                        end_dt = user_tz.localize(end_dt)
                else:
                    # Use default duration
                    end_dt = start_dt + timedelta(hours=self.valves.default_event_duration_hours)
                    
                self.log_debug(f"Parsed times: {start_dt.isoformat()} to {end_dt.isoformat()}")
                    
            except ImportError:
                return "❌ **Error**: dateutil library not available. Cannot parse dates."
            except Exception as e:
                return f"❌ **Invalid date/time format**: {str(e)}. Please use formats like '2024-01-15 14:30' or 'tomorrow 2pm'."

            # Find target calendar
            target_calendar_id = None
            target_calendar_name = "Primary"
            
            # Get calendar list
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            if calendar_hint:
                # Smart calendar matching
                hint_lower = calendar_hint.lower()
                best_match = None
                best_score = 0
                
                for calendar in calendars:
                    calendar_name = calendar.get('summary', '').lower()
                    access_role = calendar.get('accessRole', 'reader')
                    
                    # Only consider writable calendars
                    if access_role in ['owner', 'writer']:
                        # Simple fuzzy matching
                        if hint_lower in calendar_name:
                            score = len(hint_lower) / len(calendar_name)  # Preference for exact matches
                            if score > best_score:
                                best_score = score
                                best_match = calendar
                
                if best_match:
                    target_calendar_id = best_match['id']
                    target_calendar_name = best_match.get('summary', 'Unknown')
                else:
                    return f"❌ **Calendar not found**: No writable calendar matching '{calendar_hint}'. Use `get_calendars()` to see available calendars."
            
            elif self.valves.default_calendar_name:
                # Use configured default calendar
                default_name_lower = self.valves.default_calendar_name.lower()
                for calendar in calendars:
                    calendar_name = calendar.get('summary', '').lower()
                    access_role = calendar.get('accessRole', 'reader')
                    
                    if access_role in ['owner', 'writer'] and default_name_lower in calendar_name:
                        target_calendar_id = calendar['id']
                        target_calendar_name = calendar.get('summary', 'Unknown')
                        break
                        
                if not target_calendar_id:
                    return f"❌ **Default calendar not found**: '{self.valves.default_calendar_name}' not found or not writable."
            
            else:
                # Use primary calendar
                for calendar in calendars:
                    if calendar.get('primary', False) and calendar.get('accessRole') in ['owner', 'writer']:
                        target_calendar_id = calendar['id']
                        target_calendar_name = calendar.get('summary', 'Primary')
                        break
                
                if not target_calendar_id:
                    # Fallback to first writable calendar
                    for calendar in calendars:
                        if calendar.get('accessRole') in ['owner', 'writer']:
                            target_calendar_id = calendar['id']
                            target_calendar_name = calendar.get('summary', 'Unknown')
                            break

            if not target_calendar_id:
                return "❌ **No writable calendars found**. Please check your calendar permissions."

            # Build event object
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': self.valves.user_timezone,
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': self.valves.user_timezone,
                }
            }
            
            if description:
                event['description'] = description
                
            if location:
                event['location'] = location

            # Create the event
            self.log_debug(f"Creating event in calendar: {target_calendar_name} ({target_calendar_id})")
            
            created_event = service.events().insert(
                calendarId=target_calendar_id,
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink', '')
            
            # Format response
            duration = end_dt - start_dt
            
            response = f"✅ **Event Created Successfully**\n\n"
            response += f"**Title**: {title}\n"
            response += f"**Calendar**: {target_calendar_name}\n"
            response += f"**Time**: {start_dt.strftime('%A, %d %B %Y at %H:%M')} - {end_dt.strftime('%H:%M')}\n"
            response += f"**Duration**: {duration}\n"
            
            if location:
                response += f"**Location**: {location}\n"
                
            if description:
                response += f"**Description**: {description[:100]}{'...' if len(description) > 100 else ''}\n"
            
            response += f"**Event ID**: `{event_id}`\n"
            
            if event_link:
                response += f"**View in Google Calendar**: {event_link}\n"
            
            response += "\n💡 Use `get_event_details('{event_id}')` for full event details."

            return response

        except Exception as e:
            self.log_error(f"Create smart event failed: {e}")
            return f"❌ **Error creating event**: {str(e)}"

    def search_calendar_events(self, query: str, days_back: int = 30, days_ahead: int = 30, 
                              calendar_names: Optional[str] = None) -> str:
        """
        Search for events across calendars using text query
        
        Args:
            query: Search query (searches title, description, location)
            days_back: Days to look back (default 30)
            days_ahead: Days to look ahead (default 30)  
            calendar_names: Comma-separated calendar names to filter (optional)
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            # Calculate time range
            now = datetime.now()
            time_min = (now - timedelta(days=days_back)).isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            self.log_debug(f"Searching events for '{query}' from {time_min} to {time_max}")

            # Get calendar list
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

            # Search across selected calendars
            matching_events = []
            query_lower = query.lower()
            
            for calendar in selected_calendars:
                calendar_id = calendar['id']
                calendar_name = calendar.get('summary', 'Unknown')
                
                try:
                    # Get events from this calendar
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=100,  # Higher limit for search
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    for event in events:
                        # Search in title, description, and location
                        title = event.get('summary', '').lower()
                        description = event.get('description', '').lower()
                        location = event.get('location', '').lower()
                        
                        if (query_lower in title or 
                            query_lower in description or 
                            query_lower in location):
                            
                            # Add calendar context
                            event['_calendar_name'] = calendar_name
                            event['_calendar_id'] = calendar_id
                            event['_match_score'] = self._calculate_match_score(query_lower, title, description, location)
                            matching_events.append(event)
                        
                except Exception as e:
                    self.log_error(f"Failed to search calendar '{calendar_name}': {e}")
                    continue

            if not matching_events:
                calendar_list = ', '.join([cal.get('summary', 'Unknown') for cal in selected_calendars])
                return f"🔍 **No events found** matching '{query}' in the last {days_back} days and next {days_ahead} days.\n**Searched calendars**: {calendar_list}"

            # Sort by relevance (match score) then by time
            matching_events.sort(key=lambda x: (-x.get('_match_score', 0), x.get('start', {}).get('dateTime', x.get('start', {}).get('date', ''))))

            # Format response
            response = f"🔍 **Search Results** for '{query}' ({len(matching_events)} found):\n\n"
            
            for i, event in enumerate(matching_events[:15], 1):  # Limit to 15 results
                title = event.get('summary', 'No Title')
                calendar_name = event.get('_calendar_name', 'Unknown Calendar')
                event_id = event.get('id', 'Unknown ID')
                
                # Parse time
                start = event.get('start', {})
                if 'dateTime' in start:
                    start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    time_str = start_time.strftime("%a %d/%m, %H:%M")
                elif 'date' in start:
                    start_date = datetime.fromisoformat(start['date'])
                    time_str = start_date.strftime("%a %d/%m (All day)")
                else:
                    time_str = "Time unknown"
                
                # Show match context
                description = event.get('description', '')
                location = event.get('location', '')
                match_context = []
                
                if query_lower in title.lower():
                    match_context.append("title")
                if query_lower in description.lower():
                    match_context.append("description") 
                if query_lower in location.lower():
                    match_context.append("location")
                    
                context_str = f" • Match: {', '.join(match_context)}" if match_context else ""
                
                response += f"{i}. **{title}**\n"
                response += f"   📅 {time_str} • {calendar_name}{context_str}\n"
                response += f"   ID: `{event_id}`\n\n"

            if len(matching_events) > 15:
                response += f"... and {len(matching_events) - 15} more results\n\n"
                
            response += "💡 Use `get_event_details('event_id')` for full details of any event."
            
            return response

        except Exception as e:
            self.log_error(f"Search calendar events failed: {e}")
            return f"❌ **Error searching events**: {str(e)}"

    def _calculate_match_score(self, query: str, title: str, description: str, location: str) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        
        # Title matches are most important
        if query in title:
            score += 10.0 * (len(query) / len(title)) if title else 0
            
        # Description matches
        if query in description:
            score += 5.0 * (len(query) / len(description)) if description else 0
            
        # Location matches  
        if query in location:
            score += 3.0 * (len(query) / len(location)) if location else 0
            
        return score

    def get_todays_schedule(self) -> str:
        """
        Get today's schedule with imminent event warnings for daily briefings
        """
        try:
            service, auth_status = self.get_authenticated_service('calendar', 'v3')
            if not service:
                return auth_status

            # Get user timezone
            import pytz
            try:
                user_tz = pytz.timezone(self.valves.user_timezone)
            except:
                user_tz = pytz.UTC
                self.log_debug(f"Using UTC timezone (invalid timezone: {self.valves.user_timezone})")

            # Calculate today's time range in user timezone
            now = datetime.now(user_tz)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            time_min = start_of_day.isoformat()
            time_max = end_of_day.isoformat()
            
            self.log_debug(f"Getting today's schedule from {time_min} to {time_max} (timezone: {user_tz})")

            # Get calendar list
            calendar_list = service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            if not calendars:
                return "📅 **No calendars found**. Please check your Google Calendar access."

            # Get events from all visible calendars
            all_events = []
            
            for calendar in calendars:
                if not calendar.get('selected', True):
                    continue  # Skip hidden calendars
                    
                calendar_id = calendar['id']
                calendar_name = calendar.get('summary', 'Unknown')
                
                try:
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=50,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    for event in events:
                        event['_calendar_name'] = calendar_name
                        event['_calendar_id'] = calendar_id
                        all_events.append(event)
                        
                except Exception as e:
                    self.log_error(f"Failed to get today's events from '{calendar_name}': {e}")
                    continue

            if not all_events:
                return f"📅 **Today's Schedule** ({now.strftime('%A, %d %B %Y')}):\n\n🎉 **No events scheduled for today!** Enjoy your free day!"

            # Sort events by start time
            all_events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))

            # Categorize events
            past_events = []
            current_events = []
            imminent_events = []  # Within next hour
            upcoming_events = []
            all_day_events = []
            
            for event in all_events:
                start = event.get('start', {})
                end = event.get('end', {})
                
                if 'date' in start:
                    # All-day event
                    all_day_events.append(event)
                elif 'dateTime' in start:
                    # Timed event - parse with timezone awareness
                    start_dt_str = start['dateTime']
                    end_dt_str = end.get('dateTime', start_dt_str)
                    
                    # Parse datetime strings properly
                    if start_dt_str.endswith('Z'):
                        start_time = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00'))
                    else:
                        start_time = datetime.fromisoformat(start_dt_str)
                    
                    if end_dt_str.endswith('Z'):
                        end_time = datetime.fromisoformat(end_dt_str.replace('Z', '+00:00'))
                    else:
                        end_time = datetime.fromisoformat(end_dt_str)
                    
                    # Convert to user timezone for comparison
                    start_time_user = start_time.astimezone(user_tz)
                    end_time_user = end_time.astimezone(user_tz)
                    
                    if end_time_user <= now:
                        past_events.append(event)
                    elif start_time_user <= now <= end_time_user:
                        current_events.append(event)
                    elif start_time_user <= now + timedelta(hours=1):
                        imminent_events.append(event)
                    else:
                        upcoming_events.append(event)

            # Build response
            response = f"📅 **Today's Schedule** ({now.strftime('%A, %d %B %Y')}):\n\n"
            
            # Current events (most important)
            if current_events:
                response += "🔴 **HAPPENING NOW**:\n"
                for event in current_events:
                    title = event.get('summary', 'No Title')
                    calendar_name = event.get('_calendar_name', 'Unknown')
                    
                    # Parse and convert to user timezone for display
                    start_dt_str = event['start']['dateTime']
                    end_dt_str = event['end']['dateTime']
                    
                    if start_dt_str.endswith('Z'):
                        start_time = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00')).astimezone(user_tz)
                    else:
                        start_time = datetime.fromisoformat(start_dt_str).astimezone(user_tz)
                        
                    if end_dt_str.endswith('Z'):
                        end_time = datetime.fromisoformat(end_dt_str.replace('Z', '+00:00')).astimezone(user_tz)
                    else:
                        end_time = datetime.fromisoformat(end_dt_str).astimezone(user_tz)
                        
                    response += f"• **{title}** ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}) • {calendar_name}\n"
                response += "\n"
            
            # Imminent events (urgent)
            if imminent_events:
                response += "⚠️ **STARTING SOON** (within 1 hour):\n"
                for event in imminent_events:
                    title = event.get('summary', 'No Title')
                    calendar_name = event.get('_calendar_name', 'Unknown')
                    
                    # Parse and convert to user timezone for display and calculation
                    start_dt_str = event['start']['dateTime']
                    if start_dt_str.endswith('Z'):
                        start_time = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00')).astimezone(user_tz)
                    else:
                        start_time = datetime.fromisoformat(start_dt_str).astimezone(user_tz)
                        
                    time_until = start_time - now
                    minutes_until = int(time_until.total_seconds() / 60)
                    response += f"• **{title}** in {minutes_until} minutes ({start_time.strftime('%H:%M')}) • {calendar_name}\n"
                response += "\n"
            
            # All-day events
            if all_day_events:
                response += "📋 **ALL DAY**:\n"
                for event in all_day_events:
                    title = event.get('summary', 'No Title')
                    calendar_name = event.get('_calendar_name', 'Unknown')
                    response += f"• **{title}** • {calendar_name}\n"
                response += "\n"
                
            # Remaining events
            if upcoming_events:
                response += "⏰ **UPCOMING**:\n"
                for event in upcoming_events[:10]:  # Limit to avoid clutter
                    title = event.get('summary', 'No Title')
                    calendar_name = event.get('_calendar_name', 'Unknown')
                    start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                    response += f"• **{title}** ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}) • {calendar_name}\n"
                
                if len(upcoming_events) > 10:
                    response += f"... and {len(upcoming_events) - 10} more events\n"
                response += "\n"
            
            # Summary
            total_events = len(all_events)
            completed_events = len(past_events)
            remaining_events = total_events - completed_events
            
            response += f"📊 **Summary**: {total_events} events today • {completed_events} completed • {remaining_events} remaining\n"
            
            # Helpful tips
            if imminent_events:
                response += "\n💡 **Tip**: You have events starting soon - consider preparing now!"
            elif not upcoming_events and not current_events:
                response += "\n🎯 **Tip**: Rest of your day is free - great time for focused work!"
                
            return response

        except Exception as e:
            self.log_error(f"Get today's schedule failed: {e}")
            return f"❌ **Error getting today's schedule**: {str(e)}"

    def list_email_attachments(self, email_id: str) -> str:
        """
        List all attachments in a specific email with metadata
        
        Args:
            email_id: Gmail message ID
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Listing attachments for email: {email_id}")

            # Get full email to analyze attachments
            email_data = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            # Extract basic email info
            headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')

            # Detect attachments
            attachments = self._detect_attachments(email_data['payload'])
            
            if not attachments:
                return f"📧 **Email: {subject}**\n\n📎 **No attachments found** in this email."

            # Format response
            response = f"📧 **Email: {subject}**\n"
            response += f"**From**: {sender}\n"
            response += f"**Message ID**: `{email_id}`\n\n"
            response += f"📎 **Attachments Found** ({len(attachments)}):\n\n"
            
            for i, attachment in enumerate(attachments, 1):
                filename = attachment['filename']
                mime_type = attachment['mime_type']
                size = attachment['size']
                attachment_id = attachment['attachment_id']
                
                # Format size
                size_str = self._format_file_size(size) if size > 0 else "Size unknown"
                
                # Check if size exceeds limit
                size_mb = size / (1024 * 1024) if size > 0 else 0
                size_warning = ""
                if size_mb > self.valves.max_attachment_size_mb:
                    size_warning = f" ⚠️ (Exceeds {self.valves.max_attachment_size_mb}MB limit)"
                
                response += f"{i}. **{filename}**\n"
                response += f"   📄 Type: {mime_type}\n"
                response += f"   📊 Size: {size_str}{size_warning}\n"
                
                if attachment_id:
                    response += f"   🔗 Attachment ID: `{attachment_id}`\n"
                    response += f"   💾 Use: `download_email_attachment('{email_id}', '{attachment_id}', '{filename}')`\n"
                else:
                    response += f"   📦 Inline data available\n"
                    response += f"   💾 Use: `download_email_attachment('{email_id}', '{i-1}', '{filename}')`\n"
                
                response += "\n"

            response += f"💡 **Tips**:\n"
            response += f"• Use `download_email_attachment()` to download individual attachments\n"
            response += f"• Use `extract_all_attachments('{email_id}')` to download all attachments\n"
            response += f"• Current size limit: {self.valves.max_attachment_size_mb}MB per file"
            
            return response

        except Exception as e:
            self.log_error(f"List email attachments failed: {e}")
            return f"❌ **Error listing attachments**: {str(e)}"

    def download_email_attachment(self, email_id: str, attachment_identifier: str, filename: Optional[str] = None) -> str:
        """
        Download a specific attachment from an email
        
        Args:
            email_id: Gmail message ID
            attachment_identifier: Attachment ID or attachment index (for inline attachments)
            filename: Optional custom filename for saving
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Downloading attachment {attachment_identifier} from email {email_id}")

            # Get full email to analyze attachments
            email_data = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            # Extract basic email info
            headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
            subject = headers.get('Subject', 'No Subject')

            # Detect attachments
            attachments = self._detect_attachments(email_data['payload'])
            
            if not attachments:
                return f"❌ **No attachments found** in email: {subject}"

            # Find the specific attachment
            target_attachment = None
            
            # Try to match by attachment ID first
            for attachment in attachments:
                if attachment.get('attachment_id') == attachment_identifier:
                    target_attachment = attachment
                    break
            
            # If no match by ID, try by index for inline attachments
            if not target_attachment:
                try:
                    index = int(attachment_identifier)
                    if 0 <= index < len(attachments):
                        target_attachment = attachments[index]
                except ValueError:
                    pass
            
            if not target_attachment:
                attachment_list = []
                for i, att in enumerate(attachments):
                    att_id = att.get('attachment_id', f"index_{i}")
                    attachment_list.append(f"  • {att['filename']} (ID: `{att_id}`)")
                
                return f"❌ **Attachment not found**: `{attachment_identifier}`\n\n**Available attachments**:\n" + "\n".join(attachment_list)

            # Use provided filename or original filename
            save_filename = filename or target_attachment['filename']
            
            # Check size limit
            size_mb = target_attachment['size'] / (1024 * 1024) if target_attachment['size'] > 0 else 0
            if size_mb > self.valves.max_attachment_size_mb:
                return f"❌ **File too large**: {self._format_file_size(target_attachment['size'])} exceeds limit of {self.valves.max_attachment_size_mb}MB"

            # Get attachment data
            attachment_data = None
            
            if target_attachment.get('attachment_id'):
                # Large attachment - fetch via API
                attachment_data = self._get_attachment_data(email_id, target_attachment['attachment_id'])
            elif target_attachment.get('inline_data'):
                # Small inline attachment
                try:
                    attachment_data = base64.urlsafe_b64decode(target_attachment['inline_data'])
                except Exception as e:
                    self.log_error(f"Failed to decode inline attachment data: {e}")
                    return f"❌ **Error decoding attachment data**: {str(e)}"
            
            if not attachment_data:
                return f"❌ **Failed to retrieve attachment data** for: {target_attachment['filename']}"

            # Save attachment
            saved_path = self._save_attachment(attachment_data, save_filename, email_id)
            
            if not saved_path:
                return f"❌ **Failed to save attachment**: {save_filename}"

            # Format response
            response = f"✅ **Attachment Downloaded Successfully**\n\n"
            response += f"📧 **Email**: {subject}\n"
            response += f"📎 **File**: {target_attachment['filename']}\n"
            response += f"📄 **Type**: {target_attachment['mime_type']}\n"
            response += f"📊 **Size**: {self._format_file_size(target_attachment['size'])}\n"
            response += f"💾 **Saved to**: `{saved_path}`\n"
            response += f"🔗 **Email ID**: `{email_id}`"
            
            return response

        except Exception as e:
            self.log_error(f"Download email attachment failed: {e}")
            return f"❌ **Error downloading attachment**: {str(e)}"

    def extract_all_attachments(self, email_id: str) -> str:
        """
        Extract and download all attachments from an email
        
        Args:
            email_id: Gmail message ID
        """
        try:
            service, auth_status = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Extracting all attachments from email: {email_id}")

            # Get full email to analyze attachments
            email_data = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            # Extract basic email info
            headers = {h['name']: h['value'] for h in email_data['payload'].get('headers', [])}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')

            # Detect attachments
            attachments = self._detect_attachments(email_data['payload'])
            
            if not attachments:
                return f"📧 **Email: {subject}**\n\n📎 **No attachments found** in this email."

            # Track results
            successful_downloads = []
            failed_downloads = []
            skipped_files = []
            total_size = 0

            response = f"📧 **Email: {subject}**\n"
            response += f"**From**: {sender}\n"
            response += f"**Message ID**: `{email_id}`\n\n"
            response += f"📦 **Extracting {len(attachments)} attachment(s)**...\n\n"

            for i, attachment in enumerate(attachments, 1):
                filename = attachment['filename']
                size = attachment['size']
                mime_type = attachment['mime_type']
                
                # Check size limit
                size_mb = size / (1024 * 1024) if size > 0 else 0
                if size_mb > self.valves.max_attachment_size_mb:
                    skipped_files.append({
                        'filename': filename,
                        'reason': f"Exceeds {self.valves.max_attachment_size_mb}MB limit ({self._format_file_size(size)})"
                    })
                    continue

                try:
                    # Get attachment data
                    attachment_data = None
                    
                    if attachment.get('attachment_id'):
                        # Large attachment - fetch via API
                        attachment_data = self._get_attachment_data(email_id, attachment['attachment_id'])
                    elif attachment.get('inline_data'):
                        # Small inline attachment
                        attachment_data = base64.urlsafe_b64decode(attachment['inline_data'])
                    
                    if not attachment_data:
                        failed_downloads.append({
                            'filename': filename,
                            'reason': 'Failed to retrieve attachment data'
                        })
                        continue

                    # Save attachment
                    saved_path = self._save_attachment(attachment_data, filename, email_id)
                    
                    if saved_path:
                        successful_downloads.append({
                            'filename': filename,
                            'size': size,
                            'mime_type': mime_type,
                            'path': saved_path
                        })
                        total_size += size
                    else:
                        failed_downloads.append({
                            'filename': filename,
                            'reason': 'Failed to save to disk'
                        })

                except Exception as e:
                    self.log_error(f"Failed to extract attachment {filename}: {e}")
                    failed_downloads.append({
                        'filename': filename,
                        'reason': str(e)
                    })

            # Format results
            if successful_downloads:
                response += f"✅ **Successfully Downloaded** ({len(successful_downloads)} files, {self._format_file_size(total_size)} total):\n"
                for download in successful_downloads:
                    response += f"• **{download['filename']}** ({self._format_file_size(download['size'])})\n"
                    response += f"  📄 {download['mime_type']}\n"
                    response += f"  💾 `{download['path']}`\n\n"

            if skipped_files:
                response += f"⚠️ **Skipped Files** ({len(skipped_files)}):\n"
                for skip in skipped_files:
                    response += f"• **{skip['filename']}** - {skip['reason']}\n"
                response += "\n"

            if failed_downloads:
                response += f"❌ **Failed Downloads** ({len(failed_downloads)}):\n"
                for fail in failed_downloads:
                    response += f"• **{fail['filename']}** - {fail['reason']}\n"
                response += "\n"

            # Summary
            total_attachments = len(attachments)
            response += f"📊 **Summary**:\n"
            response += f"• Total attachments: {total_attachments}\n"
            response += f"• Successfully downloaded: {len(successful_downloads)}\n"
            response += f"• Skipped (size limit): {len(skipped_files)}\n"
            response += f"• Failed: {len(failed_downloads)}\n"
            response += f"• Total downloaded size: {self._format_file_size(total_size)}"

            return response

        except Exception as e:
            self.log_error(f"Extract all attachments failed: {e}")
            return f"❌ **Error extracting attachments**: {str(e)}"

    # ========== GOOGLE DRIVE FUNCTIONS ==========

    def search_drive_files(self, query: str, max_results: int = 20) -> str:
        """
        Search files in Google Drive using query syntax
        
        Args:
            query: Search query (supports Drive search syntax)
            max_results: Maximum number of files to return
            
        Returns:
            Formatted string with search results
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            self.log_debug(f"🔍 Searching Drive files: '{query}' (max: {max_results})")
            
            # Clean and validate query
            cleaned_query = query.strip()
            
            # If query looks like a simple search term with quotes, convert to proper Drive syntax
            if cleaned_query.startswith('"') and cleaned_query.endswith('"') and cleaned_query.count('"') == 2:
                # Convert "search term" to name contains 'search term'
                search_term = cleaned_query[1:-1]  # Remove quotes
                cleaned_query = f"name contains '{search_term}'"
                self.log_debug(f"🔧 Converted query to: '{cleaned_query}'")
            
            # Build query parameters
            fields = "nextPageToken,files(id,name,mimeType,size,parents,modifiedTime,webViewLink,owners)"
            
            # Execute search
            results = drive_service.files().list(
                q=cleaned_query,
                pageSize=min(max_results, 100),
                fields=fields,
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return f"📂 **No files found** matching query: '{cleaned_query}'"
            
            response = f"📂 **Drive Search Results** (showing {len(files)} files)\n"
            response += f"**Query**: {cleaned_query}\n\n"
            
            for file in files:
                name = file.get('name', 'Unnamed')
                file_id = file.get('id', '')
                mime_type = file.get('mimeType', 'unknown')
                size = file.get('size', 0)
                modified = file.get('modifiedTime', '')
                
                # Format file type
                if 'folder' in mime_type:
                    icon = "📁"
                    type_str = "Folder"
                elif 'document' in mime_type:
                    icon = "📄"
                    type_str = "Google Doc"
                elif 'spreadsheet' in mime_type:
                    icon = "📊"
                    type_str = "Google Sheet"
                elif 'presentation' in mime_type:
                    icon = "📋"
                    type_str = "Google Slides"
                elif 'image' in mime_type:
                    icon = "🖼️"
                    type_str = "Image"
                elif 'pdf' in mime_type:
                    icon = "📄"
                    type_str = "PDF"
                else:
                    icon = "📎"
                    type_str = "File"
                
                # Format size
                if size and size != '0':
                    size_mb = int(size) / (1024 * 1024)
                    size_str = f" ({size_mb:.1f}MB)" if size_mb >= 1 else f" ({int(size) // 1024}KB)"
                else:
                    size_str = ""
                
                # Format modification date
                if modified:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = modified[:10]
                else:
                    date_str = "Unknown"
                
                response += f"{icon} **{name}**{size_str}\n"
                response += f"   📋 Type: {type_str} | 🕒 Modified: {date_str}\n"
                response += f"   🆔 ID: `{file_id}`\n\n"
            
            if len(files) == max_results:
                response += f"⚠️ **Note**: Results limited to {max_results} files. Use more specific search terms for better results.\n"
            
            response += f"\n💡 **Usage**: Use `get_drive_file_details('file_id')` for more information"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive search failed: {e}")
            return f"❌ **Error searching Drive**: {str(e)}"

    def list_drive_files(self, folder_id: str = None, max_results: int = 50) -> str:
        """
        List files in a specific Drive folder or root
        
        Args:
            folder_id: Folder ID to list (None for root folder)
            max_results: Maximum number of files to return
            
        Returns:
            Formatted string with file listing
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            # Build query
            if folder_id:
                query = f"'{folder_id}' in parents and trashed=false"
                location = f"folder {folder_id}"
            else:
                query = "parents in 'root' and trashed=false"
                location = "root folder"
            
            self.log_debug(f"📂 Listing Drive files in {location} (max: {max_results})")
            
            # Execute listing
            fields = "nextPageToken,files(id,name,mimeType,size,modifiedTime,webViewLink)"
            results = drive_service.files().list(
                q=query,
                pageSize=min(max_results, 100),
                fields=fields,
                orderBy="folder,name"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return f"📂 **Empty folder** - No files found in {location}"
            
            # Separate folders and files
            folders = [f for f in files if 'folder' in f.get('mimeType', '')]
            regular_files = [f for f in files if 'folder' not in f.get('mimeType', '')]
            
            response = f"📂 **Drive Folder Contents** ({len(files)} items)\n"
            response += f"**Location**: {location}\n\n"
            
            # List folders first
            if folders:
                response += "📁 **Folders**:\n"
                for folder in folders:
                    name = folder.get('name', 'Unnamed')
                    folder_id = folder.get('id', '')
                    response += f"   📁 {name} (`{folder_id}`)\n"
                response += "\n"
            
            # List files
            if regular_files:
                response += "📄 **Files**:\n"
                for file in regular_files:
                    name = file.get('name', 'Unnamed')
                    file_id = file.get('id', '')
                    size = file.get('size', 0)
                    
                    # Format size
                    if size and size != '0':
                        size_mb = int(size) / (1024 * 1024)
                        size_str = f" ({size_mb:.1f}MB)" if size_mb >= 1 else f" ({int(size) // 1024}KB)"
                    else:
                        size_str = ""
                    
                    response += f"   📄 {name}{size_str} (`{file_id}`)\n"
            
            response += f"\n💡 **Usage**: Use `get_drive_file_details('file_id')` for file details or `list_drive_files('folder_id')` to browse folders"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive listing failed: {e}")
            return f"❌ **Error listing Drive files**: {str(e)}"

    def get_drive_file_details(self, file_id: str) -> str:
        """
        Get comprehensive details for a specific Drive file
        
        Args:
            file_id: Google Drive file ID or filename (will search by name if not an ID)
            
        Returns:
            Formatted string with file details
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            # Smart resolution: Convert filename to file ID if needed
            original_file_id = file_id
            file_id = self._resolve_drive_file_id(file_id)
            
            # Handle multiple matches
            if file_id.startswith("MULTIPLE_MATCHES:"):
                search_term = file_id.split(":", 1)[1]
                query = f"name contains '{search_term}' and trashed = false"
                results = drive_service.files().list(q=query, pageSize=10).execute()
                files = results.get('files', [])
                
                response = f"💾 **Found {len(files)} files** matching '{search_term}':\n\n"
                for i, file in enumerate(files, 1):
                    response += f"{i}. **{file['name']}**\n"
                    response += f"   ID: `{file['id']}`\n"
                    response += f"   Type: {file.get('mimeType', 'unknown')}\n\n"
                
                response += "**Usage**: `get_drive_file_details('file_id')` with the exact ID from above."
                return response
            
            if file_id != original_file_id:
                self.log_debug(f"🎯 Smart resolution: '{original_file_id}' → '{file_id}'")
            
            self.log_debug(f"📋 Getting Drive file details for: {file_id}")
            
            # Get file metadata
            fields = "id,name,mimeType,size,parents,createdTime,modifiedTime,webViewLink,webContentLink,owners,permissions,description"
            file_metadata = drive_service.files().get(
                fileId=file_id,
                fields=fields
            ).execute()
            
            name = file_metadata.get('name', 'Unnamed')
            mime_type = file_metadata.get('mimeType', 'unknown')
            size = file_metadata.get('size', 0)
            created = file_metadata.get('createdTime', '')
            modified = file_metadata.get('modifiedTime', '')
            description = file_metadata.get('description', '')
            web_view_link = file_metadata.get('webViewLink', '')
            web_content_link = file_metadata.get('webContentLink', '')
            owners = file_metadata.get('owners', [])
            
            # Format file type
            if 'folder' in mime_type:
                icon = "📁"
                type_str = "Folder"
            elif 'document' in mime_type:
                icon = "📄"
                type_str = "Google Document"
            elif 'spreadsheet' in mime_type:
                icon = "📊"
                type_str = "Google Spreadsheet"
            elif 'presentation' in mime_type:
                icon = "📋"
                type_str = "Google Presentation"
            elif 'image' in mime_type:
                icon = "🖼️"
                type_str = "Image"
            elif 'pdf' in mime_type:
                icon = "📄"
                type_str = "PDF Document"
            else:
                icon = "📎"
                type_str = "File"
            
            response = f"{icon} **{name}**\n\n"
            response += f"**📋 File Details**:\n"
            response += f"• **Type**: {type_str}\n"
            response += f"• **ID**: `{file_id}`\n"
            
            # Size information
            if size and size != '0':
                size_mb = int(size) / (1024 * 1024)
                if size_mb >= 1:
                    response += f"• **Size**: {size_mb:.2f} MB\n"
                else:
                    response += f"• **Size**: {int(size) // 1024} KB\n"
            
            # Dates
            if created:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    response += f"• **Created**: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                except:
                    response += f"• **Created**: {created}\n"
            
            if modified:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    response += f"• **Modified**: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                except:
                    response += f"• **Modified**: {modified}\n"
            
            # Owner information
            if owners:
                owner_names = [owner.get('displayName', 'Unknown') for owner in owners]
                response += f"• **Owner**: {', '.join(owner_names)}\n"
            
            # Description
            if description:
                response += f"• **Description**: {description}\n"
            
            # Links
            response += f"\n**🔗 Access Links**:\n"
            if web_view_link:
                response += f"• **View**: {web_view_link}\n"
            if web_content_link:
                response += f"• **Download**: {web_content_link}\n"
            
            # Action suggestions
            response += f"\n**💡 Available Actions**:\n"
            if 'folder' not in mime_type:
                response += f"• `download_drive_file('{file_id}', 'local_filename')` - Download file\n"
            else:
                response += f"• `list_drive_files('{file_id}')` - Browse folder contents\n"
            response += f"• `upload_file_to_drive('local_path', '{file_id}', 'filename')` - Upload to this location\n"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive file details failed: {e}")
            return f"❌ **Error getting file details**: {str(e)}"

    def download_drive_file(self, file_id: str, local_filename: str = None) -> str:
        """
        Download a file from Google Drive to local storage
        
        Args:
            file_id: Google Drive file ID or filename (will search by name if not an ID)
            local_filename: Local filename (optional, will use Drive filename if not provided)
            
        Returns:
            Status message with download details
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            # Smart resolution: Convert filename to file ID if needed
            original_file_id = file_id
            file_id = self._resolve_drive_file_id(file_id)
            
            # Handle multiple matches
            if file_id.startswith("MULTIPLE_MATCHES:"):
                search_term = file_id.split(":", 1)[1]
                return f"❌ **Multiple files found** matching '{search_term}'. Please use `get_drive_file_details('{search_term}')` to see all matches and get the exact file ID."
            
            if file_id != original_file_id:
                self.log_debug(f"🎯 Smart resolution: '{original_file_id}' → '{file_id}'")
            
            # Get file metadata first
            file_metadata = drive_service.files().get(fileId=file_id, fields="name,size,mimeType").execute()
            drive_filename = file_metadata.get('name', 'unnamed_file')
            file_size = int(file_metadata.get('size', 0))
            mime_type = file_metadata.get('mimeType', '')
            
            # Check file size limit
            max_size_bytes = self.valves.max_drive_file_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                return f"❌ **File too large**: {file_size // (1024*1024)}MB exceeds limit of {self.valves.max_drive_file_size_mb}MB"
            
            # Use provided filename or default to Drive filename
            if not local_filename:
                local_filename = drive_filename
            
            # Create downloads directory
            downloads_dir = os.path.join(self.google_dir, "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Full path for downloaded file
            local_path = os.path.join(downloads_dir, local_filename)
            
            self.log_debug(f"⬇️ Downloading Drive file: {drive_filename} ({file_size} bytes)")
            
            # Handle Google Workspace files (export as common formats)
            if 'google-apps' in mime_type:
                export_map = {
                    'google-apps.document': 'application/pdf',
                    'google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                }
                
                export_mime = None
                for app_type, export_type in export_map.items():
                    if app_type in mime_type:
                        export_mime = export_type
                        # Update filename extension
                        if not local_filename.endswith(('.pdf', '.xlsx', '.pptx')):
                            if 'document' in mime_type:
                                local_filename += '.pdf'
                            elif 'spreadsheet' in mime_type:
                                local_filename += '.xlsx'
                            elif 'presentation' in mime_type:
                                local_filename += '.pptx'
                            local_path = os.path.join(downloads_dir, local_filename)
                        break
                
                if export_mime:
                    request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime)
                    download_type = "exported"
                else:
                    return f"❌ **Unsupported Google Workspace file type**: {mime_type}"
            else:
                # Regular file download
                request = drive_service.files().get_media(fileId=file_id)
                download_type = "downloaded"
            
            # Download the file
            with open(local_path, 'wb') as local_file:
                downloader = request.execute()
                local_file.write(downloader)
            
            # Get actual file size after download
            actual_size = os.path.getsize(local_path)
            size_mb = actual_size / (1024 * 1024)
            
            response = f"✅ **File {download_type} successfully**\n\n"
            response += f"📁 **File Details**:\n"
            response += f"• **Original**: {drive_filename}\n"
            response += f"• **Local**: {local_filename}\n"
            response += f"• **Size**: {size_mb:.2f} MB\n"
            response += f"• **Location**: `{local_path}`\n"
            response += f"• **Drive ID**: `{file_id}`\n\n"
            
            if download_type == "exported":
                response += f"📄 **Note**: Google Workspace file exported to common format\n"
            
            response += f"💡 **Usage**: File is now available locally at the path shown above"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive download failed: {e}")
            return f"❌ **Error downloading file**: {str(e)}"

    def upload_file_to_drive(self, local_path: str, parent_folder_id: str = None, filename: str = None) -> str:
        """
        Upload a local file to Google Drive
        
        Args:
            local_path: Path to local file to upload
            parent_folder_id: Drive folder ID to upload to (None for root)
            filename: Custom filename for Drive (optional, uses local filename if not provided)
            
        Returns:
            Status message with upload details
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            # Check if local file exists
            if not os.path.exists(local_path):
                return f"❌ **Local file not found**: {local_path}"
            
            # Check file size
            file_size = os.path.getsize(local_path)
            max_size_bytes = self.valves.max_drive_file_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                size_mb = file_size / (1024 * 1024)
                return f"❌ **File too large**: {size_mb:.1f}MB exceeds limit of {self.valves.max_drive_file_size_mb}MB"
            
            # Determine filename
            if not filename:
                filename = os.path.basename(local_path)
            
            self.log_debug(f"⬆️ Uploading file to Drive: {filename} ({file_size} bytes)")
            
            # Prepare file metadata
            file_metadata = {'name': filename}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            # Import MediaFileUpload
            try:
                from googleapiclient.http import MediaFileUpload
            except ImportError:
                return f"❌ **Error**: MediaFileUpload not available. Please install google-api-python-client"
            
            # Create media upload object
            media = MediaFileUpload(local_path, resumable=True)
            
            # Upload the file
            request = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,webViewLink,parents'
            )
            
            file_result = request.execute()
            
            # Extract upload results
            uploaded_file_id = file_result.get('id')
            uploaded_name = file_result.get('name')
            uploaded_size = int(file_result.get('size', 0))
            web_view_link = file_result.get('webViewLink', '')
            
            # Determine location
            if parent_folder_id:
                location = f"folder {parent_folder_id}"
            else:
                location = "Drive root"
            
            size_mb = uploaded_size / (1024 * 1024)
            
            response = f"✅ **File uploaded successfully**\n\n"
            response += f"📁 **Upload Details**:\n"
            response += f"• **Local file**: {os.path.basename(local_path)}\n"
            response += f"• **Drive name**: {uploaded_name}\n"
            response += f"• **Size**: {size_mb:.2f} MB\n"
            response += f"• **Location**: {location}\n"
            response += f"• **Drive ID**: `{uploaded_file_id}`\n"
            
            if web_view_link:
                response += f"• **View link**: {web_view_link}\n"
            
            response += f"\n💡 **Available Actions**:\n"
            response += f"• `get_drive_file_details('{uploaded_file_id}')` - View file details\n"
            response += f"• `download_drive_file('{uploaded_file_id}', 'new_name')` - Download file\n"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive upload failed: {e}")
            return f"❌ **Error uploading file**: {str(e)}"

    def create_drive_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Create a new folder in Google Drive
        
        Args:
            folder_name: Name for the new folder
            parent_folder_id: Parent folder ID (None for root folder)
            
        Returns:
            Status message with folder details
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            self.log_debug(f"📁 Creating Drive folder: {folder_name}")
            
            # Prepare folder metadata
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            # Create the folder
            folder_result = drive_service.files().create(
                body=folder_metadata,
                fields='id,name,webViewLink,parents'
            ).execute()
            
            folder_id = folder_result.get('id')
            folder_name_result = folder_result.get('name')
            web_view_link = folder_result.get('webViewLink', '')
            
            # Determine location
            if parent_folder_id:
                location = f"inside folder {parent_folder_id}"
            else:
                location = "in Drive root"
            
            response = f"✅ **Folder created successfully**\n\n"
            response += f"📁 **Folder Details**:\n"
            response += f"• **Name**: {folder_name_result}\n"
            response += f"• **Location**: {location}\n"
            response += f"• **Folder ID**: `{folder_id}`\n"
            
            if web_view_link:
                response += f"• **View link**: {web_view_link}\n"
            
            response += f"\n💡 **Available Actions**:\n"
            response += f"• `list_drive_files('{folder_id}')` - Browse folder contents\n"
            response += f"• `upload_file_to_drive('local_path', '{folder_id}', 'filename')` - Upload files to folder\n"
            response += f"• `create_drive_folder('subfolder_name', '{folder_id}')` - Create subfolder\n"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive folder creation failed: {e}")
            return f"❌ **Error creating folder**: {str(e)}"

    def get_drive_folders(self, parent_folder_id: str = None) -> str:
        """
        List folders in Drive or within a specific parent folder
        
        Args:
            parent_folder_id: Parent folder ID (None for root level folders)
            
        Returns:
            Formatted string with folder listing
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            # Build query for folders only
            if parent_folder_id:
                query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                location = f"folder {parent_folder_id}"
            else:
                query = "parents in 'root' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                location = "Drive root"
            
            self.log_debug(f"📁 Listing Drive folders in {location}")
            
            # Execute query
            fields = "nextPageToken,files(id,name,modifiedTime,webViewLink)"
            results = drive_service.files().list(
                q=query,
                pageSize=100,
                fields=fields,
                orderBy="name"
            ).execute()
            
            folders = results.get('files', [])
            
            if not folders:
                return f"📁 **No folders found** in {location}"
            
            response = f"📁 **Drive Folders** ({len(folders)} folders in {location})\n\n"
            
            for folder in folders:
                name = folder.get('name', 'Unnamed')
                folder_id = folder.get('id', '')
                modified = folder.get('modifiedTime', '')
                
                # Format modification date
                if modified:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = modified[:10]
                else:
                    date_str = "Unknown"
                
                response += f"📁 **{name}**\n"
                response += f"   🆔 ID: `{folder_id}`\n"
                response += f"   🕒 Modified: {date_str}\n\n"
            
            response += f"💡 **Usage**: Use `list_drive_files('folder_id')` to browse folder contents or `create_drive_folder('name', 'parent_id')` to create subfolders"
            
            return response
            
        except Exception as e:
            self.log_error(f"Drive folder listing failed: {e}")
            return f"❌ **Error listing folders**: {str(e)}"

    def _find_or_create_folder_path(self, folder_path: str, root_folder_id: str = None) -> str:
        """
        Find or create a folder path like 'Documents/Projects/2024'
        
        Args:
            folder_path: Slash-separated folder path
            root_folder_id: Starting folder ID (None for Drive root)
            
        Returns:
            Final folder ID or error message
        """
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return None
            
            # Split path into components
            path_parts = [p.strip() for p in folder_path.split('/') if p.strip()]
            if not path_parts:
                return root_folder_id or 'root'
            
            current_folder_id = root_folder_id
            
            for folder_name in path_parts:
                # Search for existing folder
                if current_folder_id:
                    query = f"'{current_folder_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                else:
                    query = f"parents in 'root' and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                
                results = drive_service.files().list(q=query, fields="files(id,name)").execute()
                folders = results.get('files', [])
                
                if folders:
                    # Folder exists, use it
                    current_folder_id = folders[0]['id']
                    self.log_debug(f"📁 Found existing folder: {folder_name} ({current_folder_id})")
                else:
                    # Create new folder
                    folder_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    
                    if current_folder_id:
                        folder_metadata['parents'] = [current_folder_id]
                    
                    folder_result = drive_service.files().create(
                        body=folder_metadata,
                        fields='id,name'
                    ).execute()
                    
                    current_folder_id = folder_result.get('id')
                    self.log_debug(f"📁 Created new folder: {folder_name} ({current_folder_id})")
            
            return current_folder_id
            
        except Exception as e:
            self.log_error(f"Folder path creation failed: {e}")
            return None

    def upload_email_attachments_to_drive(self, email_id: str, folder_strategy: str = "auto", target_folder: str = None) -> str:
        """
        Upload all attachments from an email to Google Drive with smart organization
        
        Args:
            email_id: Gmail message ID
            folder_strategy: Organization strategy ('auto', 'manual', 'hybrid')
            target_folder: Specific folder ID or path for manual strategy
            
        Returns:
            Status message with upload results
        """
        try:
            # First get the email attachments
            attachments = self._get_attachments_from_email_id(email_id)
            if not attachments:
                return f"📎 **No attachments found** in email {email_id}"
            
            # Get email details for smart folder organization
            email_details = self._get_email_details_for_drive_organization(email_id)
            
            # Determine target folder based on strategy
            if folder_strategy == "manual" and target_folder:
                # Clean folder name - strip trailing punctuation that AI might add
                cleaned_folder = target_folder.rstrip('.,!?;:')
                if cleaned_folder != target_folder:
                    self.log_debug(f"🧹 Cleaned folder name: '{target_folder}' → '{cleaned_folder}'")
                    target_folder = cleaned_folder
                
                # Manual specification
                if target_folder.startswith('/') or '/' in target_folder:
                    # Path-like specification, find or create folder path
                    folder_id = self._find_or_create_folder_path(target_folder)
                elif len(target_folder) > 25 and not ' ' in target_folder:
                    # Looks like a Drive folder ID
                    folder_id = target_folder
                else:
                    # Simple folder name - search for existing or create
                    folder_id = self._find_or_create_folder_path(target_folder)
            else:
                # Auto or hybrid strategy - smart folder organization
                folder_id = self._determine_smart_folder(email_details, target_folder)
            
            if not folder_id:
                return f"❌ **Error**: Could not determine target folder for uploads"
            
            self.log_debug(f"📤 Uploading {len(attachments)} attachments to folder {folder_id}")
            
            uploaded_files = []
            failed_uploads = []
            
            for attachment in attachments:
                try:
                    # Get attachment data
                    if attachment.get('attachment_id'):
                        attachment_data = self._get_attachment_data(email_id, attachment['attachment_id'])
                    elif attachment.get('inline_data'):
                        attachment_data = base64.urlsafe_b64decode(attachment['inline_data'])
                    else:
                        attachment_data = None
                    
                    if not attachment_data:
                        failed_uploads.append(f"Could not retrieve: {attachment.get('filename', 'unknown')}")
                        continue
                    
                    # Save attachment temporarily
                    temp_dir = os.path.join(self.google_dir, "temp_uploads")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    filename = attachment.get('filename', f"attachment_{len(uploaded_files)}")
                    temp_path = os.path.join(temp_dir, filename)
                    
                    with open(temp_path, 'wb') as f:
                        f.write(attachment_data)
                    
                    # Upload to Drive
                    upload_result = self.upload_file_to_drive(temp_path, folder_id, filename)
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    
                    if "✅" in upload_result:
                        uploaded_files.append({
                            'filename': filename,
                            'size': len(attachment_data),
                            'status': 'success'
                        })
                    else:
                        failed_uploads.append(f"{filename}: {upload_result}")
                        
                except Exception as e:
                    failed_uploads.append(f"{attachment.get('filename', 'unknown')}: {str(e)}")
            
            # Generate response
            response = f"📤 **Email Attachments Upload Results**\n\n"
            response += f"**Email ID**: {email_id}\n"
            response += f"**Target folder**: {folder_id}\n"
            response += f"**Strategy**: {folder_strategy}\n\n"
            
            if uploaded_files:
                total_size = sum(f['size'] for f in uploaded_files)
                total_mb = total_size / (1024 * 1024)
                
                response += f"✅ **Successfully uploaded** ({len(uploaded_files)} files, {total_mb:.2f}MB):\n"
                for file_info in uploaded_files:
                    size_mb = file_info['size'] / (1024 * 1024)
                    response += f"   📎 {file_info['filename']} ({size_mb:.2f}MB)\n"
                response += "\n"
            
            if failed_uploads:
                response += f"❌ **Failed uploads** ({len(failed_uploads)} files):\n"
                for failure in failed_uploads:
                    response += f"   ⚠️ {failure}\n"
                response += "\n"
            
            response += f"💡 **Usage**: Use `list_drive_files('{folder_id}')` to view uploaded files"
            
            return response
            
        except Exception as e:
            self.log_error(f"Email attachments upload failed: {e}")
            return f"❌ **Error uploading attachments**: {str(e)}"

    def upload_attachment_to_drive(self, email_id: str, attachment_identifier: str, target_folder: str = None, custom_filename: str = None) -> str:
        """
        Upload a specific email attachment to Google Drive
        
        Args:
            email_id: Gmail message ID
            attachment_identifier: Attachment ID, index (0-based), filename, or position ("first", "last", etc.)
            target_folder: Drive folder ID, folder name, or path (None for auto organization)
            custom_filename: Custom filename for Drive (optional)
            
        Returns:
            Status message with upload result
        """
        try:
            # Get the specific attachment
            attachments = self._get_attachments_from_email_id(email_id)
            if not attachments:
                return f"📎 **No attachments found** in email {email_id}"
            
            # Smart resolution: Convert filename/position to index
            original_identifier = attachment_identifier
            attachment_identifier = self._resolve_attachment_identifier(email_id, attachment_identifier)
            if attachment_identifier != original_identifier:
                self.log_debug(f"🎯 Smart resolution: '{original_identifier}' → '{attachment_identifier}'")
            
            # Find the specific attachment
            attachment = None
            if attachment_identifier.isdigit():
                # Index-based selection
                index = int(attachment_identifier)
                if 0 <= index < len(attachments):
                    attachment = attachments[index]
                else:
                    return f"❌ **Invalid attachment index**: {index} (available: 0-{len(attachments)-1})"
            else:
                # ID-based selection
                self.log_debug(f"🔍 Looking for attachment ID: {attachment_identifier[:50]}...")
                self.log_debug(f"📎 Available attachment IDs in fresh fetch:")
                for i, att in enumerate(attachments):
                    att_id = att.get('attachment_id', 'NO_ID')
                    self.log_debug(f"   {i}: {att_id[:50]}...")
                
                for att in attachments:
                    if att.get('attachment_id') == attachment_identifier:
                        attachment = att
                        break
                
                if not attachment:
                    return f"❌ **Attachment not found**: {attachment_identifier}"
            
            # Get attachment data
            if attachment.get('attachment_id'):
                attachment_data = self._get_attachment_data(email_id, attachment['attachment_id'])
            elif attachment.get('inline_data'):
                attachment_data = base64.urlsafe_b64decode(attachment['inline_data'])
            else:
                attachment_data = None
            
            if not attachment_data:
                return f"❌ **Could not retrieve attachment data** for {attachment.get('filename', 'unknown')}"
            
            # Determine target folder
            if target_folder:
                # Clean folder name - strip trailing punctuation that AI might add
                cleaned_folder = target_folder.rstrip('.,!?;:')
                if cleaned_folder != target_folder:
                    self.log_debug(f"🧹 Cleaned folder name: '{target_folder}' → '{cleaned_folder}'")
                    target_folder = cleaned_folder
                
                if target_folder.startswith('/') or '/' in target_folder:
                    # Path-like specification
                    folder_id = self._find_or_create_folder_path(target_folder)
                elif len(target_folder) > 25 and not ' ' in target_folder:
                    # Looks like a Drive folder ID
                    folder_id = target_folder
                else:
                    # Simple folder name - search for existing or create
                    folder_id = self._find_or_create_folder_path(target_folder)
            else:
                # Auto organization
                email_details = self._get_email_details_for_drive_organization(email_id)
                folder_id = self._determine_smart_folder(email_details)
            
            if not folder_id:
                error_msg = f"❌ **Error**: Could not determine target folder from '{target_folder}'"
                self.log_debug(error_msg)
                return error_msg
            
            self.log_debug(f"📁 Resolved target folder: '{target_folder}' → '{folder_id}'")
            
            # Use custom filename or original
            filename = custom_filename or attachment.get('filename', 'attachment')
            
            # Save attachment temporarily
            temp_dir = os.path.join(self.google_dir, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(attachment_data)
            
            # Upload to Drive
            upload_result = self.upload_file_to_drive(temp_path, folder_id, filename)
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
            
            if "✅" in upload_result:
                size_mb = len(attachment_data) / (1024 * 1024)
                response = f"✅ **Attachment uploaded successfully**\n\n"
                response += f"📎 **Attachment Details**:\n"
                response += f"• **Email ID**: {email_id}\n"
                response += f"• **Original filename**: {attachment.get('filename', 'unknown')}\n"
                response += f"• **Drive filename**: {filename}\n"
                response += f"• **Size**: {size_mb:.2f} MB\n"
                response += f"• **Target folder**: {folder_id}\n\n"
                response += upload_result.split('\n\n', 1)[1] if '\n\n' in upload_result else ""
                return response
            else:
                return upload_result
            
        except Exception as e:
            self.log_error(f"Single attachment upload failed: {e}")
            return f"❌ **Error uploading attachment**: {str(e)}"

    def _get_email_details_for_drive_organization(self, email_id: str) -> Dict[str, str]:
        """Get email details needed for smart Drive folder organization"""
        try:
            service, _ = self.get_authenticated_service('gmail', 'v1')
            if not service:
                return {}
            
            # Get email metadata
            email = service.users().messages().get(
                userId='me',
                id=email_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in email.get('payload', {}).get('headers', [])}
            
            return {
                'sender': headers.get('From', '').lower(),
                'subject': headers.get('Subject', '').lower(),
                'date': headers.get('Date', ''),
                'email_id': email_id
            }
            
        except Exception as e:
            self.log_error(f"Failed to get email details: {e}")
            return {}

    def _determine_smart_folder(self, email_details: Dict[str, str], manual_override: str = None) -> str:
        """
        Determine smart folder organization based on email content and settings
        
        Args:
            email_details: Dictionary with sender, subject, date info
            manual_override: Manual folder specification for hybrid mode
            
        Returns:
            Folder ID for uploads
        """
        try:
            # Check for manual override first (hybrid mode)
            if manual_override:
                if manual_override.startswith('/') or '/' in manual_override:
                    return self._find_or_create_folder_path(manual_override)
                else:
                    return manual_override
            
            # Get or create base folder
            base_folder = self.valves.drive_default_folder
            if not base_folder:
                base_folder = "Open-WebUI Attachments"
            
            # Smart organization based on drive_folder_structure setting
            strategy = self.valves.drive_folder_structure
            
            if strategy == "email-organized":
                # Organize by sender domain and subject keywords
                sender = email_details.get('sender', '')
                subject = email_details.get('subject', '')
                
                # Extract domain from sender
                if '@' in sender:
                    domain = sender.split('@')[1].split()[0]  # Handle "Name <email@domain.com>"
                    domain = domain.replace('>', '').strip()
                else:
                    domain = "unknown-sender"
                
                # Detect document types from subject
                subject_lower = subject.lower()
                if any(keyword in subject_lower for keyword in ['invoice', 'bill', 'payment', 'receipt']):
                    folder_path = f"{base_folder}/Invoices/{domain}"
                elif any(keyword in subject_lower for keyword in ['tax', 'irs', '1099', 'w2', 'w-2']):
                    folder_path = f"{base_folder}/Tax Documents/{domain}"
                elif any(keyword in subject_lower for keyword in ['utility', 'electric', 'gas', 'water', 'internet']):
                    folder_path = f"{base_folder}/Utilities/{domain}"
                elif any(keyword in subject_lower for keyword in ['statement', 'bank', 'credit card', 'account']):
                    folder_path = f"{base_folder}/Financial/{domain}"
                else:
                    folder_path = f"{base_folder}/General/{domain}"
                    
            elif strategy == "date-organized":
                # Organize by year/month
                try:
                    from datetime import datetime
                    date_str = email_details.get('date', '')
                    if date_str:
                        # Parse email date (RFC 2822 format)
                        dt = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                        folder_path = f"{base_folder}/{dt.year}/{dt.strftime('%m-%B')}"
                    else:
                        dt = datetime.now()
                        folder_path = f"{base_folder}/{dt.year}/{dt.strftime('%m-%B')}"
                except:
                    # Fallback to current date
                    from datetime import datetime
                    dt = datetime.now()
                    folder_path = f"{base_folder}/{dt.year}/{dt.strftime('%m-%B')}"
                    
            elif strategy == "type-organized":
                # Organize by file type (will be determined by attachment analysis)
                folder_path = f"{base_folder}/By Type"
                
            else:
                # Default: simple base folder
                folder_path = base_folder
            
            return self._find_or_create_folder_path(folder_path)
            
        except Exception as e:
            self.log_error(f"Smart folder determination failed: {e}")
            # Fallback to base folder
            base_folder = self.valves.drive_default_folder or "Open-WebUI Attachments"
            return self._find_or_create_folder_path(base_folder)

    def get_drive_storage_info_internal(self) -> str:
        """Internal method to get Google Drive storage usage and quota information"""
        try:
            drive_service, status = self._get_drive_service()
            if drive_service is None:
                return status
            
            self.log_debug("📊 Getting Drive storage information")
            
            # Get storage quota information
            about = drive_service.about().get(fields="storageQuota,user").execute()
            storage_quota = about.get('storageQuota', {})
            user_info = about.get('user', {})
            
            # Extract storage information
            limit = int(storage_quota.get('limit', 0))
            usage = int(storage_quota.get('usage', 0))
            usage_in_drive = int(storage_quota.get('usageInDrive', 0))
            usage_in_drive_trash = int(storage_quota.get('usageInDriveTrash', 0))
            
            # Convert to human readable format
            def bytes_to_gb(bytes_val):
                return bytes_val / (1024**3)
            
            if limit > 0:
                limit_gb = bytes_to_gb(limit)
                usage_gb = bytes_to_gb(usage)
                drive_gb = bytes_to_gb(usage_in_drive)
                trash_gb = bytes_to_gb(usage_in_drive_trash)
                
                usage_percent = (usage / limit) * 100
                
                response = f"💾 **Google Drive Storage Information**\n\n"
                response += f"👤 **Account**: {user_info.get('displayName', 'Unknown')}\n"
                response += f"📧 **Email**: {user_info.get('emailAddress', 'Unknown')}\n\n"
                response += f"**📊 Storage Usage**:\n"
                response += f"• **Total Used**: {usage_gb:.2f} GB of {limit_gb:.2f} GB ({usage_percent:.1f}%)\n"
                response += f"• **Drive Files**: {drive_gb:.2f} GB\n"
                response += f"• **Trash**: {trash_gb:.2f} GB\n"
                response += f"• **Available**: {limit_gb - usage_gb:.2f} GB\n\n"
                
                # Add usage bar
                bar_length = 20
                filled_length = int(bar_length * usage_percent / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                response += f"**Usage Bar**: [{bar}] {usage_percent:.1f}%\n\n"
                
                # Storage warnings
                if usage_percent > 90:
                    response += "⚠️ **Warning**: Storage is almost full (>90%)\n"
                elif usage_percent > 75:
                    response += "📝 **Note**: Storage is getting full (>75%)\n"
                
                return response
            else:
                return "💾 **Google Drive Storage**: Unlimited storage account"
                
        except Exception as e:
            self.log_error(f"Drive storage info failed: {e}")
            return f"❌ **Error getting storage info**: {str(e)}"

    def search_contacts(self, query: str, max_results: Optional[int] = None) -> str:
        """
        Search contacts by name, email, phone, or organization
        
        Args:
            query: Search query (supports partial matching)
            max_results: Maximum results to return (default from settings)
        """
        try:
            service, auth_status = self.get_authenticated_service('people', 'v1')
            if not service:
                return auth_status

            # Use setting or parameter
            limit = max_results if max_results is not None else self.valves.max_contact_results
            
            self.log_debug(f"Searching contacts for: '{query}' (limit: {limit})")

            # Send warmup request as recommended by Google
            try:
                service.people().searchContacts(
                    query='',
                    readMask='names',
                    pageSize=1
                ).execute()
                self.log_debug("Warmup search request completed")
            except Exception as e:
                self.log_debug(f"Warmup request failed (non-critical): {e}")

            # Perform actual search
            search_request = service.people().searchContacts(
                query=query,
                readMask='names,emailAddresses,phoneNumbers,organizations',
                pageSize=limit
            )
            
            results = search_request.execute()
            contacts = results.get('results', [])
            
            if not contacts:
                return f"🔍 **No contacts found** for query: '{query}'"

            # Get display fields from settings
            display_fields = [field.strip() for field in self.valves.contact_display_fields.split(',')]
            
            response = f"👥 **Found {len(contacts)} contact(s)** matching '{query}':\n\n"
            
            for contact in contacts:
                person = contact.get('person', {})
                contact_info = []
                
                # Name
                if 'name' in display_fields:
                    names = person.get('names', [])
                    if names:
                        display_name = names[0].get('displayName', 'Unknown')
                        contact_info.append(f"**{display_name}**")
                
                # Email addresses
                if 'email' in display_fields:
                    emails = person.get('emailAddresses', [])
                    email_list = []
                    for email in emails:
                        addr = email.get('value', '')
                        if email.get('metadata', {}).get('primary'):
                            email_list.append(f"{addr} (primary)")
                        else:
                            email_list.append(addr)
                    if email_list:
                        contact_info.append(f"📧 {', '.join(email_list)}")
                
                # Phone numbers
                if 'phone' in display_fields:
                    phones = person.get('phoneNumbers', [])
                    phone_list = []
                    for phone in phones:
                        number = phone.get('value', '')
                        phone_type = phone.get('type', 'unknown')
                        phone_list.append(f"{number} ({phone_type})")
                    if phone_list:
                        contact_info.append(f"📞 {', '.join(phone_list)}")
                
                # Organization
                if 'organization' in display_fields:
                    orgs = person.get('organizations', [])
                    if orgs:
                        org = orgs[0]
                        company = org.get('name', '')
                        title = org.get('title', '')
                        org_info = company
                        if title:
                            org_info += f" ({title})"
                        if org_info:
                            contact_info.append(f"🏢 {org_info}")
                
                # Add resource name for detailed lookup
                resource_name = person.get('resourceName', '')
                if resource_name:
                    contact_info.append(f"🔗 ID: `{resource_name}`")
                
                if contact_info:
                    response += "• " + " • ".join(contact_info) + "\n"
                else:
                    response += "• Contact found but no displayable information\n"

            response += f"\n💡 **Tip**: Use `get_contact_details(ID)` for complete information about a specific contact."
            
            return response

        except Exception as e:
            self.log_error(f"Contact search failed: {e}")
            return f"❌ **Error searching contacts**: {str(e)}"

    def lookup_contact_by_email(self, email_address: str) -> str:
        """
        Find contact by specific email address
        
        Args:
            email_address: Email address to search for
        """
        try:
            service, auth_status = self.get_authenticated_service('people', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Looking up contact by email: {email_address}")

            # Send warmup request
            try:
                service.people().searchContacts(
                    query='',
                    readMask='names',
                    pageSize=1
                ).execute()
            except Exception as e:
                self.log_debug(f"Warmup request failed (non-critical): {e}")

            # Search for the email address
            search_request = service.people().searchContacts(
                query=email_address,
                readMask='names,emailAddresses,phoneNumbers,organizations',
                pageSize=10  # Should be enough for email lookup
            )
            
            results = search_request.execute()
            contacts = results.get('results', [])
            
            if not contacts:
                return f"📧 **No contact found** with email address: {email_address}"

            # Find exact email match
            exact_match = None
            for contact in contacts:
                person = contact.get('person', {})
                emails = person.get('emailAddresses', [])
                for email in emails:
                    if email.get('value', '').lower() == email_address.lower():
                        exact_match = person
                        break
                if exact_match:
                    break

            if not exact_match:
                return f"📧 **No exact match found** for email address: {email_address}"

            # Format contact information
            contact_info = []
            
            # Name
            names = exact_match.get('names', [])
            if names:
                display_name = names[0].get('displayName', 'Unknown')
                contact_info.append(f"**Name**: {display_name}")
            
            # Email addresses (showing all)
            emails = exact_match.get('emailAddresses', [])
            email_list = []
            for email in emails:
                addr = email.get('value', '')
                if email.get('metadata', {}).get('primary'):
                    email_list.append(f"{addr} (primary)")
                else:
                    email_list.append(addr)
            if email_list:
                contact_info.append(f"**Email**: {', '.join(email_list)}")
            
            # Phone numbers
            phones = exact_match.get('phoneNumbers', [])
            if phones:
                phone_list = []
                for phone in phones:
                    number = phone.get('value', '')
                    phone_type = phone.get('type', 'unknown')
                    phone_list.append(f"{number} ({phone_type})")
                contact_info.append(f"**Phone**: {', '.join(phone_list)}")
            
            # Organization
            orgs = exact_match.get('organizations', [])
            if orgs:
                org = orgs[0]
                company = org.get('name', '')
                title = org.get('title', '')
                org_info = company
                if title:
                    org_info += f" - {title}"
                if org_info:
                    contact_info.append(f"**Organization**: {org_info}")
            
            # Resource name for detailed lookup
            resource_name = exact_match.get('resourceName', '')
            if resource_name:
                contact_info.append(f"**Contact ID**: `{resource_name}`")
            
            response = f"👤 **Contact found for {email_address}**:\n\n"
            if contact_info:
                response += "\n".join(contact_info)
            else:
                response += "Contact found but no additional information available."

            return response

        except Exception as e:
            self.log_error(f"Contact lookup by email failed: {e}")
            return f"❌ **Error looking up contact by email**: {str(e)}"

    def get_contact_details(self, person_resource_name: str) -> str:
        """
        Get comprehensive details for a specific contact
        
        Args:
            person_resource_name: The resource name of the person (from search results)
        """
        try:
            service, auth_status = self.get_authenticated_service('people', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Getting contact details for: {person_resource_name}")

            # Get comprehensive contact information
            person = service.people().get(
                resourceName=person_resource_name,
                personFields='names,emailAddresses,phoneNumbers,organizations,addresses,birthdays,biographies,urls,relations,memberships'
            ).execute()
            
            if not person:
                return f"👤 **Contact not found**: {person_resource_name}"

            contact_details = []
            
            # Basic Information
            contact_details.append("## 👤 Contact Details\n")
            
            # Name information
            names = person.get('names', [])
            if names:
                name_info = names[0]
                display_name = name_info.get('displayName', 'Unknown')
                given_name = name_info.get('givenName', '')
                family_name = name_info.get('familyName', '')
                
                contact_details.append(f"**Full Name**: {display_name}")
                if given_name or family_name:
                    name_parts = []
                    if given_name:
                        name_parts.append(f"First: {given_name}")
                    if family_name:
                        name_parts.append(f"Last: {family_name}")
                    contact_details.append(f"**Name Parts**: {', '.join(name_parts)}")
            
            # Email addresses
            emails = person.get('emailAddresses', [])
            if emails:
                email_details = []
                for email in emails:
                    addr = email.get('value', '')
                    email_type = email.get('type', 'unknown')
                    if email.get('metadata', {}).get('primary'):
                        email_details.append(f"{addr} ({email_type}, primary)")
                    else:
                        email_details.append(f"{addr} ({email_type})")
                contact_details.append(f"**Email**: {', '.join(email_details)}")
            
            # Phone numbers
            phones = person.get('phoneNumbers', [])
            if phones:
                phone_details = []
                for phone in phones:
                    number = phone.get('value', '')
                    phone_type = phone.get('type', 'unknown')
                    if phone.get('metadata', {}).get('primary'):
                        phone_details.append(f"{number} ({phone_type}, primary)")
                    else:
                        phone_details.append(f"{number} ({phone_type})")
                contact_details.append(f"**Phone**: {', '.join(phone_details)}")
            
            # Organizations
            orgs = person.get('organizations', [])
            if orgs:
                org_details = []
                for org in orgs:
                    company = org.get('name', '')
                    title = org.get('title', '')
                    department = org.get('department', '')
                    
                    org_info = []
                    if company:
                        org_info.append(company)
                    if title:
                        org_info.append(f"Title: {title}")
                    if department:
                        org_info.append(f"Dept: {department}")
                    
                    if org_info:
                        org_details.append(" • ".join(org_info))
                
                if org_details:
                    contact_details.append(f"**Organization**: {' | '.join(org_details)}")
            
            # Addresses
            addresses = person.get('addresses', [])
            if addresses:
                addr_details = []
                for addr in addresses:
                    address_type = addr.get('type', 'unknown')
                    formatted_value = addr.get('formattedValue', '')
                    if formatted_value:
                        addr_details.append(f"{formatted_value} ({address_type})")
                
                if addr_details:
                    contact_details.append(f"**Address**: {' | '.join(addr_details)}")
            
            # Birthdays
            birthdays = person.get('birthdays', [])
            if birthdays:
                birthday_details = []
                for birthday in birthdays:
                    date_info = birthday.get('date', {})
                    if date_info:
                        year = date_info.get('year')
                        month = date_info.get('month')
                        day = date_info.get('day')
                        
                        if month and day:
                            date_str = f"{month}/{day}"
                            if year:
                                date_str += f"/{year}"
                            birthday_details.append(date_str)
                
                if birthday_details:
                    contact_details.append(f"**Birthday**: {', '.join(birthday_details)}")
            
            # URLs/Websites
            urls = person.get('urls', [])
            if urls:
                url_details = []
                for url in urls:
                    url_value = url.get('value', '')
                    url_type = url.get('type', 'unknown')
                    if url_value:
                        url_details.append(f"{url_value} ({url_type})")
                
                if url_details:
                    contact_details.append(f"**Websites**: {', '.join(url_details)}")
            
            # Biography/Notes
            bios = person.get('biographies', [])
            if bios:
                bio_text = bios[0].get('value', '')
                if bio_text:
                    # Truncate long biographies
                    if len(bio_text) > 200:
                        bio_text = bio_text[:197] + "..."
                    contact_details.append(f"**Notes**: {bio_text}")
            
            # Relations
            relations = person.get('relations', [])
            if relations:
                relation_details = []
                for relation in relations:
                    person_name = relation.get('person', '')
                    relation_type = relation.get('type', 'unknown')
                    if person_name:
                        relation_details.append(f"{person_name} ({relation_type})")
                
                if relation_details:
                    contact_details.append(f"**Relations**: {', '.join(relation_details)}")
            
            # Group memberships
            memberships = person.get('memberships', [])
            if memberships:
                group_details = []
                for membership in memberships:
                    group_name = membership.get('contactGroupMembership', {}).get('contactGroupId', '')
                    if group_name:
                        group_details.append(group_name)
                
                if group_details:
                    contact_details.append(f"**Groups**: {', '.join(group_details)}")
            
            # Resource name
            contact_details.append(f"**Contact ID**: `{person_resource_name}`")
            
            # Join all details
            response = "\n".join(contact_details)
            
            if len(contact_details) <= 2:  # Only header and ID
                response += "\n\nNo additional contact information available."

            return response

        except Exception as e:
            self.log_error(f"Get contact details failed: {e}")
            return f"❌ **Error getting contact details**: {str(e)}"

    def list_recent_contacts(self, limit: int = 20) -> str:
        """
        List recently added or modified contacts
        
        Args:
            limit: Maximum number of contacts to return
        """
        try:
            service, auth_status = self.get_authenticated_service('people', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Listing recent contacts (limit: {limit})")

            # Get connections (personal contacts)
            connections_request = service.people().connections().list(
                resourceName='people/me',
                pageSize=limit,
                personFields='names,emailAddresses,phoneNumbers,organizations,metadata',
                sortOrder='LAST_MODIFIED_DESCENDING'
            )
            
            connections = connections_request.execute()
            contacts = connections.get('connections', [])
            
            if not contacts:
                return "👥 **No contacts found**. Your contact list may be empty."

            # Get display fields from settings
            display_fields = [field.strip() for field in self.valves.contact_display_fields.split(',')]
            
            response = f"👥 **Recent Contacts** ({len(contacts)} found):\n\n"
            
            for contact in contacts:
                contact_info = []
                
                # Name
                if 'name' in display_fields:
                    names = contact.get('names', [])
                    if names:
                        display_name = names[0].get('displayName', 'Unknown')
                        contact_info.append(f"**{display_name}**")
                
                # Email addresses
                if 'email' in display_fields:
                    emails = contact.get('emailAddresses', [])
                    email_list = []
                    for email in emails:
                        addr = email.get('value', '')
                        if email.get('metadata', {}).get('primary'):
                            email_list.append(f"{addr} (primary)")
                        else:
                            email_list.append(addr)
                    if email_list:
                        contact_info.append(f"📧 {', '.join(email_list)}")
                
                # Phone numbers
                if 'phone' in display_fields:
                    phones = contact.get('phoneNumbers', [])
                    phone_list = []
                    for phone in phones:
                        number = phone.get('value', '')
                        phone_type = phone.get('type', 'unknown')
                        phone_list.append(f"{number} ({phone_type})")
                    if phone_list:
                        contact_info.append(f"📞 {', '.join(phone_list)}")
                
                # Organization
                if 'organization' in display_fields:
                    orgs = contact.get('organizations', [])
                    if orgs:
                        org = orgs[0]
                        company = org.get('name', '')
                        title = org.get('title', '')
                        org_info = company
                        if title:
                            org_info += f" ({title})"
                        if org_info:
                            contact_info.append(f"🏢 {org_info}")
                
                # Metadata for last modified (if available)
                metadata = contact.get('metadata', {})
                sources = metadata.get('sources', [])
                if sources:
                    # Look for update time
                    for source in sources:
                        update_time = source.get('updateTime')
                        if update_time:
                            # Format the timestamp (simplified)
                            contact_info.append(f"🕒 Modified: {update_time[:10]}")
                            break
                
                # Add resource name for detailed lookup
                resource_name = contact.get('resourceName', '')
                if resource_name:
                    contact_info.append(f"🔗 ID: `{resource_name}`")
                
                if contact_info:
                    response += "• " + " • ".join(contact_info) + "\n"
                else:
                    response += "• Contact found but no displayable information\n"

            response += f"\n💡 **Tip**: Use `search_contacts('name')` to find specific contacts or `get_contact_details(ID)` for full details."
            
            return response

        except Exception as e:
            self.log_error(f"List recent contacts failed: {e}")
            return f"❌ **Error listing recent contacts**: {str(e)}"

    def create_contact(self, name: str, email: str, phone: Optional[str] = None, 
                      organization: Optional[str] = None) -> str:
        """
        Create a new contact (write operation - use with caution)
        
        Args:
            name: Full name of the contact
            email: Primary email address
            phone: Phone number (optional)
            organization: Company/organization name (optional)
        """
        try:
            service, auth_status = self.get_authenticated_service('people', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Creating contact: {name} ({email})")

            # Check for existing contact with same email (duplicate detection)
            existing_check = self.lookup_contact_by_email(email)
            if "Contact found for" in existing_check:
                return f"⚠️ **Duplicate contact detected**!\n\nA contact with email `{email}` already exists:\n{existing_check}\n\n💡 **Options**: \n• Use a different email address\n• Add a suffix to the name (e.g., '{name} (Work)')\n• Proceed anyway if this is intentionally a different contact"

            # Build contact data
            contact_data = {
                'names': [{'displayName': name}],
                'emailAddresses': [{'value': email, 'type': 'work'}]
            }

            # Add phone if provided
            if phone:
                contact_data['phoneNumbers'] = [{'value': phone, 'type': 'mobile'}]

            # Add organization if provided
            if organization:
                contact_data['organizations'] = [{'name': organization}]

            # Create the contact
            person = service.people().createContact(body=contact_data).execute()

            if not person:
                return f"❌ **Contact creation failed** for unknown reasons."

            # Get the created contact details for confirmation
            resource_name = person.get('resourceName', '')
            
            response = f"✅ **Contact created successfully**!\n\n"
            response += f"**Name**: {name}\n"
            response += f"**Email**: {email}\n"
            
            if phone:
                response += f"**Phone**: {phone}\n"
            if organization:
                response += f"**Organization**: {organization}\n"
                
            response += f"**Contact ID**: `{resource_name}`\n"
            response += f"\n💡 **Tip**: Use `get_contact_details('{resource_name}')` to view full contact information."

            # Log the creation
            self.log_debug(f"Contact created successfully: {resource_name}")

            return response

        except Exception as e:
            self.log_error(f"Create contact failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to contacts. Check your Google account permissions."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before creating more contacts."
            elif "invalidArgument" in error_str:
                return f"❌ **Invalid contact data**: Please check that the name and email are valid."
            else:
                return f"❌ **Error creating contact**: {error_str}"

    # ========== TASKS FUNCTIONS ==========
    
    def _validate_task_list_id(self, list_id: str) -> tuple[str, str]:
        """
        Validate and potentially fix task list ID format issues
        
        Returns:
            tuple: (actual_list_id, error_message) - error_message is empty if no error
        """
        self.log_debug(f"🔍 _validate_task_list_id() called with: '{list_id}'")
        
        if not list_id or not list_id.strip():
            self.log_debug("❌ Empty or whitespace-only ID")
            return "", "Task list ID cannot be empty"
        
        original_id = list_id.strip()
        actual_list_id = original_id
        
        self.log_debug(f"📏 ID length: {len(original_id)} characters")
        
        # Check for common ID format issues
        if len(original_id) > 100:
            self.log_debug(f"❌ ID too long: {len(original_id)} chars")
            return "", f"Task list ID is too long ({len(original_id)} characters). Expected a Google Tasks API ID (20-50 characters)."
        
        # Check if this looks like a base64-encoded ID or email-prefixed format
        if '@' in original_id:
            # Check if it's already in email-prefixed format (not base64 encoded)
            if '-' in original_id:
                email_part, list_part = original_id.split('-', 1)
                if '@' in email_part:
                    actual_list_id = list_part
                    self.log_debug(f"Converted email-prefixed ID from '{original_id}' to '{actual_list_id}'")
                    return actual_list_id, ""
            else:
                return "", f"Email-prefixed ID format not recognized. Expected format: email@domain.com-task_list_id"
        
        # Base64 decoding is no longer automatic - it will be handled as a fallback
        # when the API call fails. Just validate that it's a reasonable ID.
        self.log_debug(f"✅ Using task list ID as-is: '{original_id}'")
        
        # ID looks reasonable, use as-is
        return actual_list_id, ""

    def _looks_like_base64(self, text: str) -> bool:
        """
        Check if a string looks like it might be base64 encoded
        """
        # Base64 typically uses A-Z, a-z, 0-9, +, /, and = for padding
        # But Google often uses URL-safe base64 which uses - and _ instead of + and /
        import re
        
        # Must be reasonable length
        if len(text) < 8 or len(text) > 100:
            return False
            
        # Check if it contains characters typical of base64
        base64_pattern = re.compile(r'^[A-Za-z0-9+/\-_]+={0,2}$')
        if not base64_pattern.match(text):
            return False
            
        # Additional heuristics: base64 strings are usually longer than typical IDs
        # and have a mix of upper/lower case
        has_upper = any(c.isupper() for c in text)
        has_lower = any(c.islower() for c in text)
        has_digits = any(c.isdigit() for c in text)
        
        # Should have a mix of character types
        if not (has_upper and has_lower):
            return False
            
        return True
    
    def _looks_like_google_api_id(self, text: str) -> bool:
        """
        Check if a string looks like a valid Google API ID
        """
        # Google API IDs typically:
        # - Are 10-50 characters long
        # - Contain alphanumeric characters and sometimes underscores/hyphens
        # - Don't usually have spaces or special characters
        import re
        
        if len(text) < 5 or len(text) > 100:
            return False
            
        # Pattern for typical Google API IDs
        api_id_pattern = re.compile(r'^[A-Za-z0-9_\-]+$')
        if not api_id_pattern.match(text):
            return False
            
        # Should contain some alphanumeric characters
        has_alnum = any(c.isalnum() for c in text)
        return has_alnum

    def _validate_task_id(self, task_id: str) -> tuple[str, str]:
        """
        Validate and potentially fix task ID format issues
        
        Returns:
            tuple: (actual_task_id, error_message) - error_message is empty if no error
        """
        self.log_debug(f"🔍 _validate_task_id() called with: '{task_id}'")
        
        if not task_id or not task_id.strip():
            self.log_debug("❌ Empty or whitespace-only task ID")
            return "", "Task ID cannot be empty"
        
        original_id = task_id.strip()
        actual_task_id = original_id
        
        self.log_debug(f"📏 Task ID length: {len(original_id)} characters")
        
        # Check for common ID format issues
        if len(original_id) > 100:
            self.log_debug(f"❌ Task ID too long: {len(original_id)} chars")
            return "", f"Task ID is too long ({len(original_id)} characters). Expected a Google Tasks API ID (10-50 characters)."
        
        # Base64 decoding is no longer automatic - it will be handled as a fallback
        # when the API call fails. Just validate that it's a reasonable task ID.
        self.log_debug(f"✅ Using task ID as-is: '{original_id}'")
        
        # ID looks reasonable, use as-is
        return actual_task_id, ""

    def get_task_lists(self) -> str:
        """
        List all task lists available to the user
        """
        try:
            self.log_debug("🚀 get_task_lists() called")
            
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                self.log_debug(f"❌ Authentication failed: {auth_status}")
                return auth_status

            self.log_debug("✅ Tasks service authenticated, fetching task lists...")

            # Get all task lists
            task_lists_result = service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            
            self.log_debug(f"📋 API returned {len(task_lists)} task lists")
            if self.valves.debug_mode:
                for i, tl in enumerate(task_lists):
                    self.log_debug(f"  List {i+1}: '{tl.get('title', 'Unknown')}' (ID: {tl.get('id', 'Unknown')})")

            if not task_lists:
                self.log_debug("⚠️ No task lists found")
                return "📋 **No task lists found**. You may need to create your first task list."

            response = f"📋 **Task Lists** ({len(task_lists)} found):\n\n"
            self.log_debug(f"✅ Returning task lists response to user")

            for task_list in task_lists:
                list_id = task_list.get('id', 'unknown')
                title = task_list.get('title', 'Untitled')
                updated = task_list.get('updated', '')
                
                # Format last updated time
                updated_str = ""
                if updated:
                    try:
                        # Convert ISO timestamp to readable format
                        updated_str = f" (Updated: {updated[:10]})"
                    except:
                        pass
                
                response += f"• **{title}**{updated_str}\n"
                response += f"  🔗 ID: `{list_id}`\n"

            response += f"\n💡 **Tips**:\n"
            response += f"• Use `get_tasks('list_id')` to view tasks in a specific list\n"
            response += f"• Copy the exact ID from the 🔗 ID: line above (this is the raw Google Tasks API ID)\n"
            response += f"• These IDs work directly with all task functions"
            
            return response

        except Exception as e:
            self.log_error(f"Get task lists failed: {e}")
            return f"❌ **Error getting task lists**: {str(e)}"

    def create_task_list(self, name: str, description: Optional[str] = None) -> str:
        """
        Create a new task list
        
        Args:
            name: Name of the task list
            description: Optional description (not supported by Google Tasks API currently)
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Creating task list: {name}")

            # Build task list data
            task_list_data = {
                'title': name
            }
            
            # Note: Google Tasks API doesn't support descriptions for task lists

            # Create the task list
            task_list = service.tasklists().insert(body=task_list_data).execute()

            if not task_list:
                return f"❌ **Task list creation failed** for unknown reasons."

            list_id = task_list.get('id', 'unknown')
            title = task_list.get('title', name)
            updated = task_list.get('updated', '')

            response = f"✅ **Task list created successfully**!\n\n"
            response += f"**Name**: {title}\n"
            response += f"**List ID**: `{list_id}`\n"
            
            if updated:
                response += f"**Created**: {updated[:10]}\n"
            
            response += f"\n💡 **Tip**: Use `create_task('{list_id}', 'Task title')` to add tasks to this list."

            self.log_debug(f"Task list created successfully: {list_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Create task list failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to create task lists."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before creating more task lists."
            elif "invalidArgument" in error_str:
                return f"❌ **Invalid task list data**: Please check that the name is valid."
            else:
                return f"❌ **Error creating task list**: {error_str}"

    def update_task_list(self, list_id: str, name: str) -> str:
        """
        Update the name of an existing task list
        
        Args:
            list_id: ID of the task list to update
            name: New name for the task list
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Updating task list: {list_id}")

            # Get existing task list first
            try:
                existing_list = service.tasklists().get(tasklist=list_id).execute()
            except Exception:
                return f"❌ **Task list not found**: {list_id}"

            # Build update data
            update_data = {
                'id': list_id,
                'title': name
            }

            # Update the task list
            updated_list = service.tasklists().update(tasklist=list_id, body=update_data).execute()

            if not updated_list:
                return f"❌ **Task list update failed** for unknown reasons."

            old_title = existing_list.get('title', 'Unknown')
            new_title = updated_list.get('title', name)
            updated = updated_list.get('updated', '')

            response = f"✅ **Task list updated successfully**!\n\n"
            response += f"**Old Name**: {old_title}\n"
            response += f"**New Name**: {new_title}\n"
            response += f"**List ID**: `{list_id}`\n"
            
            if updated:
                response += f"**Updated**: {updated[:10]}\n"

            self.log_debug(f"Task list updated successfully: {list_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Update task list failed: {e}")
            return f"❌ **Error updating task list**: {str(e)}"

    def delete_task_list(self, list_id: str) -> str:
        """
        Delete a task list (WARNING: This will delete all tasks in the list!)
        
        Args:
            list_id: ID of the task list to delete
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Deleting task list: {list_id}")

            # Get task list info first for confirmation
            try:
                task_list = service.tasklists().get(tasklist=list_id).execute()
                list_title = task_list.get('title', 'Unknown')
            except Exception:
                return f"❌ **Task list not found**: {list_id}"

            # Delete the task list
            service.tasklists().delete(tasklist=list_id).execute()

            response = f"✅ **Task list deleted successfully**!\n\n"
            response += f"**Deleted List**: {list_title}\n"
            response += f"**List ID**: `{list_id}`\n"
            response += f"\n⚠️ **Note**: All tasks in this list have been permanently deleted."

            self.log_debug(f"Task list deleted successfully: {list_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Delete task list failed: {e}")
            
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task list not found**: {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have permission to delete this task list."
            else:
                return f"❌ **Error deleting task list**: {error_str}"

    def clear_completed_tasks(self, list_id: str) -> str:
        """
        Clear all completed tasks from a task list
        
        Args:
            list_id: ID of the task list to clear completed tasks from
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Clearing completed tasks from list: {list_id}")
            
            # Validate task list ID format
            actual_list_id, list_error = self._validate_task_list_id(list_id)
            if list_error:
                self.log_debug(f"❌ List ID validation failed: {list_error}")
                return f"❌ **Invalid task list ID**: {list_error}"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted list ID from '{list_id}' to '{actual_list_id}'")

            # Get task list info for confirmation
            try:
                self.log_debug(f"📋 Validating task list: {actual_list_id}")
                task_list = service.tasklists().get(tasklist=actual_list_id).execute()
                list_title = task_list.get('title', 'Unknown')
                self.log_debug(f"✅ Task list found: '{list_title}'")
            except Exception as e:
                self.log_debug(f"❌ Task list not found: {e}")
                return f"❌ **Task list not found**: {actual_list_id}"

            # First, check how many completed tasks exist
            try:
                self.log_debug(f"🔍 Checking for completed tasks before clearing...")
                completed_tasks = service.tasks().list(
                    tasklist=actual_list_id,
                    showCompleted=True,
                    showHidden=True
                ).execute()
                
                all_tasks = completed_tasks.get('items', [])
                completed_count = len([task for task in all_tasks if task.get('status') == 'completed'])
                self.log_debug(f"📊 Found {completed_count} completed tasks out of {len(all_tasks)} total tasks")
                
                if completed_count == 0:
                    return f"ℹ️ **No completed tasks to clear** in list '{list_title}'"
                    
            except Exception as e:
                self.log_debug(f"⚠️ Could not count completed tasks before clearing: {e}")

            # Clear completed tasks
            self.log_debug(f"🚀 Calling API to clear completed tasks from list: {actual_list_id}")
            try:
                service.tasks().clear(tasklist=actual_list_id).execute()
                self.log_debug(f"✅ Clear completed tasks API call completed")
                
                # Verify the clear operation worked by checking the default view (without showHidden)
                try:
                    self.log_debug(f"🔍 Verifying completed tasks were cleared from default view...")
                    after_clear_default = service.tasks().list(
                        tasklist=actual_list_id,
                        showCompleted=True,
                        showHidden=False  # Default view - should not show cleared tasks
                    ).execute()
                    
                    default_tasks = after_clear_default.get('items', [])
                    default_completed = len([task for task in default_tasks if task.get('status') == 'completed'])
                    self.log_debug(f"📊 After clearing (default view): {default_completed} completed tasks visible out of {len(default_tasks)} total")
                    
                    # Also check with showHidden=True to see hidden tasks
                    after_clear_all = service.tasks().list(
                        tasklist=actual_list_id,
                        showCompleted=True,
                        showHidden=True  # Should show cleared tasks as hidden
                    ).execute()
                    
                    all_tasks = after_clear_all.get('items', [])
                    hidden_completed = len([task for task in all_tasks if task.get('status') == 'completed' and task.get('hidden')])
                    visible_completed = len([task for task in all_tasks if task.get('status') == 'completed' and not task.get('hidden')])
                    
                    self.log_debug(f"📊 After clearing (full view): {visible_completed} visible completed, {hidden_completed} hidden completed out of {len(all_tasks)} total")
                    
                    if default_completed == 0:
                        self.log_debug(f"✅ Clear operation successful: completed tasks are hidden from default view")
                    else:
                        self.log_debug(f"⚠️ Warning: {default_completed} completed tasks still visible in default view")
                    
                except Exception as e:
                    self.log_debug(f"⚠️ Could not verify clear operation: {e}")
            except Exception as e:
                error_msg = str(e)
                self.log_debug(f"❌ Clear completed tasks API call failed: {error_msg}")
                
                # Try base64 decoding fallback if clear fails with invalid list ID
                if "invalid" in error_msg.lower() or "not found" in error_msg.lower():
                    self.log_debug(f"🔄 Trying base64 decoding fallback for clear completed tasks operation")
                    
                    # Try decoding list ID
                    if self._looks_like_base64(list_id):
                        try:
                            import base64
                            missing_padding = 4 - len(list_id) % 4
                            test_id = list_id + ('=' * missing_padding if missing_padding != 4 else '')
                            decoded_list_id = base64.b64decode(test_id).decode('utf-8')
                            self.log_debug(f"🔓 Decoded list ID available: '{list_id}' -> '{decoded_list_id}'")
                            
                            # Try clear with decoded ID
                            try:
                                self.log_debug(f"🚀 Trying decoded list ID: {decoded_list_id}")
                                service.tasks().clear(tasklist=decoded_list_id).execute()
                                self.log_debug(f"✅ Clear completed tasks succeeded with decoded list ID!")
                                # Update the ID for response
                                actual_list_id = decoded_list_id
                            except Exception as e2:
                                self.log_debug(f"❌ Decoded list ID also failed: {e2}")
                                return f"❌ **Clear completed tasks failed**: {error_msg}"
                        except Exception:
                            self.log_debug(f"🔓 Could not decode list ID: '{list_id}'")
                            return f"❌ **Clear completed tasks failed**: {error_msg}"
                    else:
                        return f"❌ **Clear completed tasks failed**: {error_msg}"
                else:
                    return f"❌ **Clear completed tasks failed**: {error_msg}"

            response = f"✅ **Completed tasks cleared successfully**!\n\n"
            response += f"**Task List**: {list_title}\n"
            response += f"**List ID**: `{list_id}`\n"
            
            # Add information about how many tasks were cleared if we have it
            if 'completed_count' in locals():
                response += f"**Tasks Cleared**: {completed_count} completed tasks\n"
            
            response += f"\n💡 **Note**: Completed tasks have been marked as 'hidden' and removed from the default view. They can still be viewed by enabling 'Show completed tasks' in Google Tasks. Active tasks remain unchanged."

            self.log_debug(f"Completed tasks cleared successfully from: {list_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Clear completed tasks failed: {e}")
            
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task list not found**: {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have permission to modify this task list."
            else:
                return f"❌ **Error clearing completed tasks**: {error_str}"

    def get_tasks(self, list_id: str, show_completed: Optional[bool] = None, show_hidden: bool = False) -> str:
        """
        Get tasks from a specific task list with filtering options
        
        Args:
            list_id: Task list ID or name (e.g., "@default", "Personal Tasks", or full ID)
            show_completed: Whether to show completed tasks (None = use default setting)
            show_hidden: Whether to show hidden tasks (default: False)
        """
        try:
            self.log_debug(f"🚀 get_tasks() called with list_id='{list_id}', show_completed={show_completed}, show_hidden={show_hidden}")
            
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                self.log_debug(f"❌ Authentication failed: {auth_status}")
                return auth_status

            # Smart resolution: Convert task list name to ID if needed
            original_list_id = list_id
            list_id = self._resolve_task_list_id(list_id)
            if list_id != original_list_id:
                self.log_debug(f"🎯 Smart resolution: '{original_list_id}' → '{list_id}'")

            # Use setting or parameter for show_completed
            if show_completed is None:
                show_completed = self.valves.show_completed_tasks_default
                self.log_debug(f"📝 Using default show_completed setting: {show_completed}")
            
            # IMPORTANT: Google Tasks marks completed tasks as hidden, so if we want completed tasks,
            # we also need to show hidden tasks unless explicitly told not to
            if show_completed and not show_hidden:
                show_hidden = True
                self.log_debug(f"🔍 Auto-enabled show_hidden=True because show_completed=True (completed tasks are marked as hidden)")
            
            self.log_debug(f"🔍 Validating task list ID: '{list_id}'")

            # Validate and fix ID format if needed
            actual_list_id, id_error = self._validate_task_list_id(list_id)
            if id_error:
                self.log_debug(f"❌ ID validation failed: {id_error}")
                return f"❌ **Invalid task list ID**: {id_error}\n\n" \
                       f"**Troubleshooting**:\n" \
                       f"• Run `get_task_lists()` to see available task lists\n" \
                       f"• Copy the exact ID from the 🔗 ID: line\n" \
                       f"• Make sure you're using the raw Google Tasks API ID\n\n" \
                       f"**Provided ID**: `{list_id}`"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted ID from '{list_id}' to '{actual_list_id}'")

            # Get task list info first
            self.log_debug(f"📋 Fetching task list info for ID: {actual_list_id}")
            try:
                task_list = service.tasklists().get(tasklist=actual_list_id).execute()
                list_title = task_list.get('title', 'Unknown')
                self.log_debug(f"✅ Task list found: '{list_title}'")
            except Exception as e:
                error_msg = str(e)
                self.log_debug(f"❌ Failed to get task list info: {error_msg}")
                
                # Try base64 decoding as fallback if original ID fails
                if ("not found" in error_msg.lower() or "invalid" in error_msg.lower()) and self._looks_like_base64(list_id):
                    self.log_debug(f"🔄 Trying base64 decoding fallback for ID: {list_id}")
                    try:
                        import base64
                        missing_padding = 4 - len(list_id) % 4
                        test_id = list_id + ('=' * missing_padding if missing_padding != 4 else '')
                        decoded_id = base64.b64decode(test_id).decode('utf-8')
                        self.log_debug(f"🔓 Base64 decoded: '{list_id}' -> '{decoded_id}'")
                        
                        # Try with decoded ID
                        task_list = service.tasklists().get(tasklist=decoded_id).execute()
                        list_title = task_list.get('title', 'Unknown')
                        actual_list_id = decoded_id  # Update to use the decoded ID
                        self.log_debug(f"✅ Task list found with decoded ID: '{list_title}'")
                    except Exception as e2:
                        self.log_debug(f"❌ Base64 fallback also failed: {e2}")
                        if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                            return f"❌ **Task list not found**: `{list_id}`\n\n" \
                                   f"**Troubleshooting**:\n" \
                                   f"• Run `get_task_lists()` to see available task lists\n" \
                                   f"• Copy the exact ID from the 🔗 ID: line\n" \
                                   f"• Make sure you're using the raw Google Tasks API ID, not a processed/encoded version\n\n" \
                                   f"**Error details**: {error_msg}"
                        else:
                            return f"❌ **Error accessing task list**: {error_msg}"
                else:
                    if "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                        return f"❌ **Task list not found**: `{list_id}`\n\n" \
                               f"**Troubleshooting**:\n" \
                               f"• Run `get_task_lists()` to see available task lists\n" \
                               f"• Copy the exact ID from the 🔗 ID: line\n" \
                               f"• Make sure you're using the raw Google Tasks API ID, not a processed/encoded version\n\n" \
                               f"**Error details**: {error_msg}"
                    else:
                        return f"❌ **Error accessing task list**: {error_msg}"

            # Build task request parameters
            max_results = self.valves.max_task_results
            self.log_debug(f"📊 Request parameters: max_results={max_results}, showCompleted={show_completed}, showHidden={show_hidden}")
            
            # Get tasks from the list
            self.log_debug(f"🔍 Fetching tasks from list '{list_title}' (ID: {actual_list_id})")
            tasks_result = service.tasks().list(
                tasklist=actual_list_id,
                maxResults=max_results,
                showCompleted=show_completed,
                showHidden=show_hidden
            ).execute()
            
            tasks = tasks_result.get('items', [])
            self.log_debug(f"📝 API returned {len(tasks)} tasks")
            
            if self.valves.debug_mode and tasks:
                for i, task in enumerate(tasks[:3]):  # Log first 3 tasks
                    self.log_debug(f"  Task {i+1}: '{task.get('title', 'Untitled')}' (Status: {task.get('status', 'unknown')})")

            if not tasks:
                completed_note = " (including completed)" if show_completed else ""
                return f"✅ **No tasks found** in '{list_title}'{completed_note}.\n\n💡 **Tip**: Use `create_task('{actual_list_id}', 'Task title')` to add your first task."

            # Get display fields from settings
            display_fields = [field.strip() for field in self.valves.task_display_fields.split(',')]
            
            # Count task types
            active_count = sum(1 for task in tasks if task.get('status') != 'completed')
            completed_count = len(tasks) - active_count

            response = f"📝 **Tasks in '{list_title}'** ({len(tasks)} total"
            if show_completed:
                response += f" - {active_count} active, {completed_count} completed"
            response += f"):\n\n"

            # Group and display tasks with hierarchy support
            for task in tasks:
                task_info = []
                task_id = task.get('id', 'unknown')
                
                # Title (with hierarchy indication)
                if 'title' in display_fields:
                    title = task.get('title', 'Untitled')
                    parent = task.get('parent')
                    
                    # Add indentation for child tasks
                    if parent:
                        title = f"    ↳ {title}"
                    
                    # Mark completed tasks
                    if task.get('status') == 'completed':
                        title = f"~~{title}~~ ✓"
                    
                    task_info.append(f"**{title}**")
                
                # Due date
                if 'due_date' in display_fields:
                    due = task.get('due')
                    if due:
                        try:
                            # Parse RFC 3339 date
                            due_date = due[:10]  # Just the date part
                            task_info.append(f"📅 Due: {due_date}")
                        except:
                            task_info.append(f"📅 Due: {due}")
                
                # Status
                if 'status' in display_fields:
                    status = task.get('status', 'needsAction')
                    if status == 'completed':
                        completed_date = task.get('completed', '')
                        if completed_date:
                            completed_str = completed_date[:10]
                            task_info.append(f"✅ Completed: {completed_str}")
                        else:
                            task_info.append(f"✅ Completed")
                    else:
                        task_info.append(f"🔄 {status}")
                
                # Notes
                if 'notes' in display_fields:
                    notes = task.get('notes', '').strip()
                    if notes:
                        # Truncate long notes
                        if len(notes) > 100:
                            notes = notes[:97] + "..."
                        task_info.append(f"📝 {notes}")
                
                # Task ID for reference
                task_info.append(f"🔗 ID: `{task_id}`")
                
                if task_info:
                    response += "• " + " • ".join(task_info) + "\n"

            response += f"\n💡 **Tips**: \n"
            response += f"• Use `create_task('{list_id}', 'title')` to add new tasks\n"
            response += f"• Use `update_task('task_id', title='new title')` to modify tasks\n"
            response += f"• Use `mark_task_complete('task_id')` to complete tasks"

            return response

        except Exception as e:
            self.log_error(f"Get tasks failed: {e}")
            return f"❌ **Error getting tasks**: {str(e)}"

    def create_task_with_smart_list_selection(self, title: str, notes: Optional[str] = None, 
                                             due_date: Optional[str] = None, list_hint: Optional[str] = None,
                                             parent_id: Optional[str] = None) -> str:
        """
        Create a task with smart list selection (similar to smart calendar selection)
        
        Args:
            title: Task title
            notes: Task notes (optional)
            due_date: Due date in various formats (optional)
            list_hint: Hint for task list selection (optional)
            parent_id: Parent task ID for hierarchy (optional)
        """
        try:
            self.log_debug(f"🚀 create_task_with_smart_list_selection() called with title='{title}', list_hint='{list_hint}', notes='{notes}', due_date='{due_date}', parent_id='{parent_id}'")
            
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                self.log_debug(f"❌ Authentication failed: {auth_status}")
                return auth_status

            self.log_debug("✅ Tasks service authenticated")
            self.log_debug(f"🎯 Starting smart list selection for task: {title}")

            # Get all task lists for smart selection
            self.log_debug("📋 Fetching all task lists for smart selection")
            task_lists_result = service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            
            self.log_debug(f"📊 Found {len(task_lists)} task lists for selection")
            if self.valves.debug_mode:
                for i, tl in enumerate(task_lists):
                    self.log_debug(f"  List {i+1}: '{tl.get('title', 'Unknown')}' (ID: {tl.get('id', 'Unknown')})")
            
            if not task_lists:
                self.log_debug("❌ No task lists found")
                return "❌ **No task lists found**. Please create a task list first using `create_task_list()`."

            # Smart list selection logic
            selected_list = None
            
            if list_hint:
                self.log_debug(f"🔍 Smart matching with hint: '{list_hint}'")
                # Try to find matching list by name (fuzzy matching)
                hint_lower = list_hint.lower()
                
                # First try exact match
                self.log_debug("🎯 Trying exact name match...")
                for tl in task_lists:
                    if tl.get('title', '').lower() == hint_lower:
                        selected_list = tl
                        self.log_debug(f"✅ Exact match found: '{tl.get('title')}'")
                        break
                
                # Then try partial match
                if not selected_list:
                    self.log_debug("🔍 Trying partial name match...")
                    for tl in task_lists:
                        if hint_lower in tl.get('title', '').lower():
                            selected_list = tl
                            self.log_debug(f"✅ Partial match found: '{tl.get('title')}'")
                            break
                
                if not selected_list:
                    self.log_debug(f"⚠️ No match found for hint: '{list_hint}'")
            
            # If no hint or no match, use default list or first list
            if not selected_list:
                self.log_debug("🎯 No hint match, trying default task list from settings")
                # Try to use default list from settings
                default_name = self.valves.default_task_list_name.strip()
                if default_name:
                    self.log_debug(f"🔍 Looking for default list: '{default_name}'")
                    for tl in task_lists:
                        if default_name.lower() in tl.get('title', '').lower():
                            selected_list = tl
                            self.log_debug(f"✅ Default list found: '{tl.get('title')}'")
                            break
                
                # Fall back to first list
                if not selected_list:
                    selected_list = task_lists[0]
                    self.log_debug(f"📌 Using first available list: '{selected_list.get('title')}'")

            list_id = selected_list.get('id')
            list_title = selected_list.get('title', 'Unknown')
            
            self.log_debug(f"🎯 Final selection: '{list_title}' (ID: {list_id})")
            
            # Create the task using the selected list
            self.log_debug(f"➡️ Delegating to create_task() with list_id={list_id}")
            return self.create_task(list_id, title, notes, due_date, parent_id, list_title)

        except Exception as e:
            self.log_debug(f"❌ Smart task creation failed: {e}")
            self.log_error(f"Smart task creation failed: {e}")
            return f"❌ **Error creating task**: {str(e)}"

    def create_task(self, list_id: str, title: str, notes: Optional[str] = None, 
                   due_date: Optional[str] = None, parent_id: Optional[str] = None,
                   list_title: Optional[str] = None) -> str:
        """
        Create a task in a specific task list
        
        Args:
            list_id: ID of the task list
            title: Task title
            notes: Task notes (optional)
            due_date: Due date in various formats (optional)
            parent_id: Parent task ID for hierarchy (optional)
            list_title: Task list title (for display, optional)
        """
        try:
            self.log_debug(f"🚀 create_task() called with list_id='{list_id}', title='{title}', notes='{notes}', due_date='{due_date}', parent_id='{parent_id}'")
            
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                self.log_debug(f"❌ Authentication failed: {auth_status}")
                return auth_status

            self.log_debug("✅ Tasks service authenticated")

            # Validate and fix ID format if needed
            self.log_debug(f"🔍 Validating task list ID: '{list_id}'")
            actual_list_id, id_error = self._validate_task_list_id(list_id)
            if id_error:
                self.log_debug(f"❌ ID validation failed: {id_error}")
                return f"❌ **Invalid task list ID**: {id_error}\n\n" \
                       f"💡 **Tip**: Use `get_task_lists()` to see available task lists and copy the correct ID."

            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted ID from '{list_id}' to '{actual_list_id}'")

            self.log_debug(f"📝 Creating task '{title}' in list {actual_list_id}")

            # Get task list info if not provided
            if not list_title:
                self.log_debug(f"📋 Fetching task list info for validation")
                try:
                    task_list = service.tasklists().get(tasklist=actual_list_id).execute()
                    list_title = task_list.get('title', 'Unknown')
                    self.log_debug(f"✅ Task list found: '{list_title}'")
                except Exception as e:
                    self.log_debug(f"❌ Failed to get task list info: {e}")
                    return f"❌ **Task list not found**: {actual_list_id}"

            # Validate parent_id if provided
            actual_parent_id = None
            if parent_id:
                actual_parent_id, parent_error = self._validate_task_id(parent_id)
                if parent_error:
                    self.log_debug(f"❌ Parent task ID validation failed: {parent_error}")
                    return f"❌ **Invalid parent task ID**: {parent_error}"
                
                if actual_parent_id != parent_id:
                    self.log_debug(f"🔄 Converted parent task ID from '{parent_id}' to '{actual_parent_id}'")

            # Build task data
            self.log_debug(f"🛠️ Building task data structure")
            task_data = {
                'title': title
            }
            
            # Add notes if provided
            if notes:
                task_data['notes'] = notes
                self.log_debug(f"📝 Added notes: '{notes[:50]}{'...' if len(notes) > 50 else ''}'")
            
            # Add parent for hierarchy if provided
            if actual_parent_id:
                task_data['parent'] = actual_parent_id
                self.log_debug(f"👨‍👩‍👧‍👦 Set parent task: {actual_parent_id}")
            
            # Parse and add due date if provided
            if due_date:
                self.log_debug(f"📅 Parsing due date: '{due_date}'")
                try:
                    # Use existing date parsing logic (import from calendar functions)
                    parsed_date = self.parse_datetime_flexible(due_date)
                    if parsed_date:
                        # Google Tasks API expects RFC 3339 date format (date only, no time)
                        due_date_str = parsed_date.strftime('%Y-%m-%dT00:00:00.000Z')
                        task_data['due'] = due_date_str
                        self.log_debug(f"✅ Due date parsed successfully: {due_date_str}")
                    else:
                        self.log_debug(f"⚠️ Due date parsing returned None")
                except Exception as e:
                    # If date parsing fails, continue without due date but warn user
                    self.log_debug(f"❌ Date parsing failed for '{due_date}': {e}")

            # Log the final task data structure
            if self.valves.debug_mode:
                self.log_debug(f"📦 Final task data: {task_data}")

            # Create the task
            self.log_debug(f"🚀 Calling Google Tasks API to create task in list {actual_list_id}")
            task = service.tasks().insert(tasklist=actual_list_id, body=task_data).execute()
            
            self.log_debug(f"✅ Task created successfully! Task ID: {task.get('id', 'unknown')}")

            if not task:
                return f"❌ **Task creation failed** for unknown reasons."

            task_id = task.get('id', 'unknown')
            created_title = task.get('title', title)
            updated = task.get('updated', '')
            parent = task.get('parent')

            response = f"✅ **Task created successfully**!\n\n"
            response += f"**Title**: {created_title}\n"
            response += f"**Task List**: {list_title}\n"
            response += f"**Task ID**: `{task_id}`\n"
            
            if notes:
                response += f"**Notes**: {notes[:100]}{'...' if len(notes) > 100 else ''}\n"
            
            if due_date and 'due' in task_data:
                response += f"**Due Date**: {due_date}\n"
            elif due_date:
                response += f"**Due Date**: ⚠️ Could not parse '{due_date}' - use formats like 'tomorrow', '2024-01-15', or 'next Friday'\n"
            
            if parent:
                response += f"**Parent Task**: {parent}\n"
            
            if updated:
                response += f"**Created**: {updated[:10]}\n"

            response += f"\n💡 **Tips**: \n"
            response += f"• Use `update_task('{task_id}', title='new title')` to modify this task\n"
            response += f"• Use `create_task('{list_id}', 'subtask title', parent_id='{task_id}')` to create subtasks"

            self.log_debug(f"Task created successfully: {task_id}")
            
            return response

        except Exception as e:
            self.log_debug(f"❌ Task creation failed: {e}")
            self.log_error(f"Create task failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task list not found**: {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to this task list."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before creating more tasks."
            elif "invalidArgument" in error_str:
                return f"❌ **Invalid task data**: Please check that the title and other fields are valid."
            else:
                return f"❌ **Error creating task**: {error_str}"

    def update_task(self, list_id: str, task_id: str, title: Optional[str] = None, 
                   notes: Optional[str] = None, due_date: Optional[str] = None, 
                   status: Optional[str] = None) -> str:
        """
        Update an existing task
        
        Args:
            list_id: ID of the task list containing the task
            task_id: ID of the task to update
            title: New title for the task
            notes: New notes/description for the task
            due_date: New due date in natural language or ISO format
            status: Task status ('needsAction', 'completed')
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Updating task: {task_id} in list: {list_id}")
            
            # Validate task list ID format
            actual_list_id, list_error = self._validate_task_list_id(list_id)
            if list_error:
                self.log_debug(f"❌ List ID validation failed: {list_error}")
                return f"❌ **Invalid task list ID**: {list_error}"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted list ID from '{list_id}' to '{actual_list_id}'")

            # Validate task ID format
            actual_task_id, task_error = self._validate_task_id(task_id)
            if task_error:
                self.log_debug(f"❌ Task ID validation failed: {task_error}")
                return f"❌ **Invalid task ID**: {task_error}"
            
            if actual_task_id != task_id:
                self.log_debug(f"🔄 Converted task ID from '{task_id}' to '{actual_task_id}'")

            # Add debugging for task ID
            self.log_debug(f"📝 Task ID format: length={len(actual_task_id)}, contains_special_chars={'@' in actual_task_id or '=' in actual_task_id}")

            # Get existing task first
            try:
                self.log_debug(f"🔍 Getting existing task with list_id={actual_list_id}, task_id={actual_task_id}")
                existing_task = service.tasks().get(tasklist=actual_list_id, task=actual_task_id).execute()
                self.log_debug(f"✅ Found task: '{existing_task.get('title', 'Untitled')}'")
            except Exception as e:
                self.log_debug(f"❌ Failed to get existing task: {e}")
                return f"❌ **Task not found**: {task_id} in list {actual_list_id}\n**Error**: {str(e)}"

            # Build update data - only include fields that are being changed
            # IMPORTANT: Include the task ID in the request body (required for updates)
            task_data = {
                'id': actual_task_id
            }
            changes = []
            
            if title is not None:
                task_data['title'] = title
                changes.append(f"title to '{title}'")
            
            if notes is not None:
                task_data['notes'] = notes
                changes.append("notes")
            
            if status is not None:
                if status.lower() in ['completed', 'complete', 'done']:
                    task_data['status'] = 'completed'
                    changes.append("status to completed")
                elif status.lower() in ['needsaction', 'needs_action', 'pending', 'todo']:
                    task_data['status'] = 'needsAction'
                    changes.append("status to needs action")
                else:
                    return f"❌ **Invalid status**: '{status}'. Use 'completed' or 'needsAction'"
            
            if due_date is not None:
                # Parse due date using existing calendar logic
                if due_date.lower() in ['none', 'clear', 'remove', '']:
                    task_data['due'] = None
                    changes.append("removed due date")
                else:
                    try:
                        parsed_date = self.parse_date_time(due_date, default_time="23:59")
                        if parsed_date:
                            # Google Tasks uses RFC 3339 date format (YYYY-MM-DD)
                            due_rfc3339 = parsed_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                            task_data['due'] = due_rfc3339
                            readable_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                            changes.append(f"due date to {readable_date}")
                        else:
                            return f"❌ **Invalid due date format**: '{due_date}'. Try 'tomorrow', '2024-01-15', or 'next Monday'"
                    except Exception as e:
                        return f"❌ **Error parsing due date**: {str(e)}"

            if not task_data:
                return f"❌ **No changes specified**. Provide title, notes, due_date, or status to update."

            # Update the task
            self.log_debug(f"🚀 Calling API to update task: list={actual_list_id}, task={actual_task_id}, data={task_data}")
            try:
                updated_task = service.tasks().update(
                    tasklist=actual_list_id,
                    task=actual_task_id,
                    body=task_data
                ).execute()
            except Exception as e:
                error_msg = str(e)
                self.log_debug(f"❌ Update API call failed: {error_msg}")
                
                # Try base64 decoding fallback combinations if update fails
                if "missing task id" in error_msg.lower() or "invalid" in error_msg.lower():
                    self.log_debug(f"🔄 Trying base64 decoding fallback combinations for update operation")
                    
                    # Prepare decoded versions
                    decoded_list_id = None
                    decoded_task_id = None
                    
                    if self._looks_like_base64(list_id):
                        try:
                            import base64
                            missing_padding = 4 - len(list_id) % 4
                            test_id = list_id + ('=' * missing_padding if missing_padding != 4 else '')
                            decoded_list_id = base64.b64decode(test_id).decode('utf-8')
                            self.log_debug(f"🔓 Decoded list ID available: '{list_id}' -> '{decoded_list_id}'")
                        except Exception:
                            self.log_debug(f"🔓 Could not decode list ID: '{list_id}'")
                    
                    if self._looks_like_base64(task_id):
                        try:
                            import base64
                            missing_padding = 4 - len(task_id) % 4
                            test_id = task_id + ('=' * missing_padding if missing_padding != 4 else '')
                            decoded_task_id = base64.b64decode(test_id).decode('utf-8')
                            self.log_debug(f"🔓 Decoded task ID available: '{task_id}' -> '{decoded_task_id}'")
                        except Exception:
                            self.log_debug(f"🔓 Could not decode task ID: '{task_id}'")
                    
                    # Try different combinations in order of likelihood
                    combinations = [
                        (actual_list_id, decoded_task_id, "original list + decoded task"),
                        (decoded_list_id, actual_task_id, "decoded list + original task"),
                        (decoded_list_id, decoded_task_id, "decoded list + decoded task")
                    ]
                    
                    for test_list_id, test_task_id, description in combinations:
                        if test_list_id is None or test_task_id is None:
                            continue
                            
                        try:
                            self.log_debug(f"🚀 Trying {description}: list={test_list_id}, task={test_task_id}")
                            self.log_debug(f"📦 Request body: {task_data}")
                            self.log_debug(f"🌐 Full URL would be: https://tasks.googleapis.com/tasks/v1/lists/{test_list_id}/tasks/{test_task_id}")
                            updated_task = service.tasks().update(
                                tasklist=test_list_id,
                                task=test_task_id,
                                body=task_data
                            ).execute()
                            self.log_debug(f"✅ Update succeeded with {description}!")
                            # Update the IDs for response
                            actual_list_id = test_list_id
                            actual_task_id = test_task_id
                            break
                        except Exception as e2:
                            error_details = str(e2)
                            self.log_debug(f"❌ {description} failed: {error_details}")
                            # Log more details about the failure
                            if hasattr(e2, 'resp'):
                                self.log_debug(f"📄 Response status: {getattr(e2.resp, 'status', 'unknown')}")
                            continue
                    else:
                        # All combinations failed
                        self.log_debug(f"❌ All base64 fallback combinations failed")
                        return f"❌ **Task update failed**: {error_msg}"
                else:
                    return f"❌ **Task update failed**: {error_msg}"

            if not updated_task:
                return f"❌ **Task update failed** for unknown reasons."

            # Format response
            task_title = updated_task.get('title', 'Untitled Task')
            updated_time = updated_task.get('updated', '')
            
            response = f"✅ **Task updated successfully**!\n\n"
            response += f"**Task**: {task_title}\n"
            response += f"**Changes**: {', '.join(changes)}\n"
            response += f"**Task ID**: `{actual_task_id}`\n"
            
            if updated_time:
                response += f"**Updated**: {updated_time[:10]}\n"

            response += f"\n💡 **Tip**: Use `get_tasks('{list_id}')` to view all tasks in this list."

            self.log_debug(f"Task updated successfully: {task_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Update task failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task or list not found**: Check the task ID {task_id} and list ID {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to this task list."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before updating more tasks."
            elif "invalidArgument" in error_str:
                return f"❌ **Invalid task data**: Please check that all fields are valid."
            else:
                return f"❌ **Error updating task**: {error_str}"

    def move_task(self, list_id: str, task_id: str, parent_id: Optional[str] = None, 
                  previous_sibling_id: Optional[str] = None) -> str:
        """
        Move a task to a different position or make it a subtask
        
        Args:
            list_id: ID of the task list containing the task
            task_id: ID of the task to move
            parent_id: ID of the parent task (to make this a subtask), or None for top-level
            previous_sibling_id: ID of the task that should come before this one
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Moving task: {task_id} in list: {list_id}")

            # Validate task list ID format
            actual_list_id, list_error = self._validate_task_list_id(list_id)
            if list_error:
                self.log_debug(f"❌ List ID validation failed: {list_error}")
                return f"❌ **Invalid task list ID**: {list_error}"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted list ID from '{list_id}' to '{actual_list_id}'")

            # Validate task ID format
            actual_task_id, task_error = self._validate_task_id(task_id)
            if task_error:
                self.log_debug(f"❌ Task ID validation failed: {task_error}")
                return f"❌ **Invalid task ID**: {task_error}"
            
            if actual_task_id != task_id:
                self.log_debug(f"🔄 Converted task ID from '{task_id}' to '{actual_task_id}'")

            # Validate parent_id if provided
            actual_parent_id = None
            if parent_id:
                actual_parent_id, parent_error = self._validate_task_id(parent_id)
                if parent_error:
                    self.log_debug(f"❌ Parent task ID validation failed: {parent_error}")
                    return f"❌ **Invalid parent task ID**: {parent_error}"
                
                if actual_parent_id != parent_id:
                    self.log_debug(f"🔄 Converted parent task ID from '{parent_id}' to '{actual_parent_id}'")

            # Validate previous_sibling_id if provided
            actual_previous_id = None
            if previous_sibling_id:
                actual_previous_id, previous_error = self._validate_task_id(previous_sibling_id)
                if previous_error:
                    self.log_debug(f"❌ Previous sibling task ID validation failed: {previous_error}")
                    return f"❌ **Invalid previous sibling task ID**: {previous_error}"
                
                if actual_previous_id != previous_sibling_id:
                    self.log_debug(f"🔄 Converted previous sibling task ID from '{previous_sibling_id}' to '{actual_previous_id}'")

            # Get existing task first to show current position
            try:
                existing_task = service.tasks().get(tasklist=actual_list_id, task=actual_task_id).execute()
                task_title = existing_task.get('title', 'Untitled Task')
            except Exception:
                return f"❌ **Task not found**: {actual_task_id} in list {actual_list_id}"

            # Move the task
            moved_task = service.tasks().move(
                tasklist=actual_list_id,
                task=actual_task_id,
                parent=actual_parent_id,
                previous=actual_previous_id
            ).execute()

            if not moved_task:
                return f"❌ **Task move failed** for unknown reasons."

            # Format response based on move type
            response = f"✅ **Task moved successfully**!\n\n"
            response += f"**Task**: {task_title}\n"
            response += f"**Task ID**: `{actual_task_id}`\n"
            
            if actual_parent_id:
                # Try to get parent task title for better user feedback
                try:
                    parent_task = service.tasks().get(tasklist=actual_list_id, task=actual_parent_id).execute()
                    parent_title = parent_task.get('title', 'Unknown Task')
                    response += f"**Action**: Moved as subtask under '{parent_title}'\n"
                except:
                    response += f"**Action**: Moved as subtask under task `{actual_parent_id}`\n"
            else:
                response += f"**Action**: Moved to top level\n"
            
            if actual_previous_id:
                try:
                    sibling_task = service.tasks().get(tasklist=actual_list_id, task=actual_previous_id).execute()
                    sibling_title = sibling_task.get('title', 'Unknown Task')
                    response += f"**Position**: After '{sibling_title}'\n"
                except:
                    response += f"**Position**: After task `{previous_sibling_id}`\n"

            response += f"\n💡 **Tip**: Use `get_tasks('{list_id}')` to see the updated task hierarchy."

            self.log_debug(f"Task moved successfully: {task_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Move task failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task or reference not found**: Check task ID {task_id}, parent ID, and sibling ID"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to this task list."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before moving more tasks."
            elif "invalidArgument" in error_str:
                return f"❌ **Invalid move operation**: Check that parent and sibling tasks exist and are in the same list."
            else:
                return f"❌ **Error moving task**: {error_str}"

    def delete_task(self, list_id: str, task_id: str) -> str:
        """
        Delete a task (and all its subtasks)
        
        Args:
            list_id: ID of the task list containing the task
            task_id: ID of the task to delete
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Deleting task: {task_id} from list: {list_id}")

            # Validate task list ID format
            actual_list_id, list_error = self._validate_task_list_id(list_id)
            if list_error:
                self.log_debug(f"❌ List ID validation failed: {list_error}")
                return f"❌ **Invalid task list ID**: {list_error}"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted list ID from '{list_id}' to '{actual_list_id}'")

            # Validate task ID format
            actual_task_id, task_error = self._validate_task_id(task_id)
            if task_error:
                self.log_debug(f"❌ Task ID validation failed: {task_error}")
                return f"❌ **Invalid task ID**: {task_error}"
            
            if actual_task_id != task_id:
                self.log_debug(f"🔄 Converted task ID from '{task_id}' to '{actual_task_id}'")

            # Get existing task first to show what's being deleted
            try:
                existing_task = service.tasks().get(tasklist=actual_list_id, task=actual_task_id).execute()
                task_title = existing_task.get('title', 'Untitled Task')
                task_status = existing_task.get('status', 'needsAction')
            except Exception:
                return f"❌ **Task not found**: {actual_task_id} in list {actual_list_id}"

            # Check if task has subtasks by listing tasks and looking for children
            subtask_count = 0
            try:
                all_tasks = service.tasks().list(tasklist=actual_list_id, showCompleted=True, showHidden=True).execute()
                tasks = all_tasks.get('items', [])
                
                for task in tasks:
                    if task.get('parent') == actual_task_id:
                        subtask_count += 1
            except:
                # If we can't check subtasks, proceed anyway
                pass

            # Delete the task
            service.tasks().delete(tasklist=actual_list_id, task=actual_task_id).execute()

            # Format response
            response = f"✅ **Task deleted successfully**!\n\n"
            response += f"**Deleted Task**: {task_title}\n"
            response += f"**Task ID**: `{actual_task_id}`\n"
            response += f"**Status**: {task_status}\n"
            
            if subtask_count > 0:
                response += f"**Subtasks**: {subtask_count} subtask(s) also deleted\n"
                response += f"\n⚠️  **Note**: Deleting a parent task also removes all its subtasks permanently."

            response += f"\n💡 **Tip**: Use `get_tasks('{list_id}')` to see the updated task list."

            self.log_debug(f"Task deleted successfully: {actual_task_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Delete task failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task not found**: {task_id} in list {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to this task list."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before deleting more tasks."
            else:
                return f"❌ **Error deleting task**: {error_str}"

    def mark_task_complete(self, list_id: str, task_id: str) -> str:
        """
        Mark a task as completed
        
        Args:
            list_id: ID of the task list containing the task
            task_id: ID of the task to mark as complete
        """
        try:
            service, auth_status = self.get_authenticated_service('tasks', 'v1')
            if not service:
                return auth_status

            self.log_debug(f"Marking task complete: {task_id} in list: {list_id}")
            
            # Validate task list ID format
            actual_list_id, list_error = self._validate_task_list_id(list_id)
            if list_error:
                self.log_debug(f"❌ List ID validation failed: {list_error}")
                return f"❌ **Invalid task list ID**: {list_error}"
            
            if actual_list_id != list_id:
                self.log_debug(f"🔄 Converted list ID from '{list_id}' to '{actual_list_id}'")

            # Validate task ID format
            actual_task_id, task_error = self._validate_task_id(task_id)
            if task_error:
                self.log_debug(f"❌ Task ID validation failed: {task_error}")
                return f"❌ **Invalid task ID**: {task_error}"
            
            if actual_task_id != task_id:
                self.log_debug(f"🔄 Converted task ID from '{task_id}' to '{actual_task_id}'")

            # Add debugging for task ID
            self.log_debug(f"📝 Task ID format: length={len(actual_task_id)}, contains_special_chars={'@' in actual_task_id or '=' in actual_task_id}")
            
            # Get existing task first
            try:
                self.log_debug(f"🔍 Getting existing task with list_id={actual_list_id}, task_id={actual_task_id}")
                existing_task = service.tasks().get(tasklist=actual_list_id, task=actual_task_id).execute()
                task_title = existing_task.get('title', 'Untitled Task')
                current_status = existing_task.get('status', 'needsAction')
                self.log_debug(f"✅ Found task: '{task_title}' with status: {current_status}")
            except Exception as e:
                self.log_debug(f"❌ Failed to get existing task: {e}")
                return f"❌ **Task not found**: {actual_task_id} in list {actual_list_id}\n**Error**: {str(e)}"

            # Check if already completed
            if current_status == 'completed':
                return f"ℹ️  **Task already completed**: '{task_title}'"

            # Update task status to completed
            # IMPORTANT: Include the task ID and title in the request body (required for updates)
            task_data = {
                'id': actual_task_id,
                'title': task_title,
                'status': 'completed'
            }

            self.log_debug(f"🚀 Calling API to mark task complete: list={actual_list_id}, task={actual_task_id}")
            try:
                updated_task = service.tasks().update(
                    tasklist=actual_list_id,
                    task=actual_task_id,
                    body=task_data
                ).execute()
            except Exception as e:
                error_msg = str(e)
                self.log_debug(f"❌ Mark complete API call failed: {error_msg}")
                
                # Try base64 decoding fallback combinations if mark complete fails
                if "missing task id" in error_msg.lower() or "invalid" in error_msg.lower():
                    self.log_debug(f"🔄 Trying base64 decoding fallback combinations for mark complete operation")
                    
                    # Prepare decoded versions
                    decoded_list_id = None
                    decoded_task_id = None
                    
                    if self._looks_like_base64(list_id):
                        try:
                            import base64
                            missing_padding = 4 - len(list_id) % 4
                            test_id = list_id + ('=' * missing_padding if missing_padding != 4 else '')
                            decoded_list_id = base64.b64decode(test_id).decode('utf-8')
                            self.log_debug(f"🔓 Decoded list ID available: '{list_id}' -> '{decoded_list_id}'")
                        except Exception:
                            self.log_debug(f"🔓 Could not decode list ID: '{list_id}'")
                    
                    if self._looks_like_base64(task_id):
                        try:
                            import base64
                            missing_padding = 4 - len(task_id) % 4
                            test_id = task_id + ('=' * missing_padding if missing_padding != 4 else '')
                            decoded_task_id = base64.b64decode(test_id).decode('utf-8')
                            self.log_debug(f"🔓 Decoded task ID available: '{task_id}' -> '{decoded_task_id}'")
                        except Exception:
                            self.log_debug(f"🔓 Could not decode task ID: '{task_id}'")
                    
                    # Try different combinations in order of likelihood
                    combinations = [
                        (actual_list_id, decoded_task_id, "original list + decoded task"),
                        (decoded_list_id, actual_task_id, "decoded list + original task"),
                        (decoded_list_id, decoded_task_id, "decoded list + decoded task")
                    ]
                    
                    for test_list_id, test_task_id, description in combinations:
                        if test_list_id is None or test_task_id is None:
                            continue
                            
                        try:
                            self.log_debug(f"🚀 Trying {description}: list={test_list_id}, task={test_task_id}")
                            updated_task = service.tasks().update(
                                tasklist=test_list_id,
                                task=test_task_id,
                                body=task_data
                            ).execute()
                            self.log_debug(f"✅ Mark complete succeeded with {description}!")
                            # Update the IDs for response
                            actual_list_id = test_list_id
                            actual_task_id = test_task_id
                            break
                        except Exception as e2:
                            self.log_debug(f"❌ {description} failed: {e2}")
                            continue
                    else:
                        # All combinations failed
                        self.log_debug(f"❌ All base64 fallback combinations failed")
                        return f"❌ **Task completion failed**: {error_msg}"
                else:
                    return f"❌ **Task completion failed**: {error_msg}"

            if not updated_task:
                return f"❌ **Task completion failed** for unknown reasons."

            # Format response
            completed_time = updated_task.get('completed', '')
            
            response = f"✅ **Task marked as completed**!\n\n"
            response += f"**Task**: {task_title}\n"
            response += f"**Task ID**: `{actual_task_id}`\n"
            response += f"**Status**: completed ✓\n"
            
            if completed_time:
                response += f"**Completed**: {completed_time[:10]}\n"

            response += f"\n💡 **Tips**:\n"
            response += f"• Use `get_tasks('{list_id}', show_completed=True)` to see completed tasks\n"
            response += f"• Use `update_task('{list_id}', '{actual_task_id}', status='needsAction')` to reopen this task"

            self.log_debug(f"Task marked complete successfully: {actual_task_id}")
            
            return response

        except Exception as e:
            self.log_error(f"Mark task complete failed: {e}")
            
            # Handle specific errors
            error_str = str(e)
            if "notFound" in error_str:
                return f"❌ **Task not found**: {task_id} in list {list_id}"
            elif "insufficientPermissions" in error_str:
                return f"❌ **Permission denied**: You may not have write access to this task list."
            elif "quotaExceeded" in error_str:
                return f"❌ **Quota exceeded**: Too many API requests. Please wait before updating more tasks."
            else:
                return f"❌ **Error marking task complete**: {error_str}"

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

    def smart_attachment_organizer(
        self,
        search_query: str = None,
        classification_prompt: str = None,
        target_folder: str = None,
        dry_run: bool = True,
        max_emails: int = 10,
        attachment_filter: str = None,
        date_range_days: int = 30
    ) -> str:
        """
        Phase 1: Smart Attachment Organizer with LLM-powered classification
        
        Automatically search emails, identify relevant attachments using LLM classification,
        and upload them to Drive folders with comprehensive reporting.
        
        Args:
            search_query: Gmail search query (e.g., "invoice OR receipt", "has:attachment project")
            classification_prompt: Custom LLM prompt for attachment classification (optional)
            target_folder: Target Drive folder name/path/ID (optional, enables auto-upload)
            dry_run: If True, only show what would be uploaded without actually uploading
            max_emails: Maximum emails to process (1-50, default: 10)
            attachment_filter: File type filter (e.g., "pdf", "image", "spreadsheet")
            date_range_days: Limit search to emails from last N days (default: 30)
            
        Examples:
            # Preview tax documents (dry run)
            smart_attachment_organizer("tax OR invoice OR receipt", dry_run=True)
            
            # Upload invoices with custom classification
            smart_attachment_organizer(
                search_query="invoice", 
                classification_prompt="Identify invoices and receipts for business expenses",
                target_folder="Business Expenses/2024",
                dry_run=False
            )
            
            # Process project attachments
            smart_attachment_organizer(
                search_query="project alpha has:attachment",
                target_folder="Projects/Alpha/Documents",
                attachment_filter="pdf"
            )
        """
        try:
            # Validate inputs
            max_emails = max(1, min(50, max_emails))
            date_range_days = max(1, min(365, date_range_days))
            
            if not search_query:
                search_query = "has:attachment"
                
            self.log_debug(f"🔍 Smart Organizer starting with query: '{search_query}'")
            
            # Phase 1 Implementation: Email search and attachment enumeration
            return self._phase1_search_and_enumerate(
                search_query, classification_prompt, target_folder,
                dry_run, max_emails, attachment_filter, date_range_days
            )
            
        except Exception as e:
            self.log_error(f"Smart organizer failed: {e}")
            return f"❌ **Smart Organizer Error**: {str(e)}"

    def _phase1_search_and_enumerate(
        self,
        search_query: str,
        classification_prompt: str,
        target_folder: str,
        dry_run: bool,
        max_emails: int,
        attachment_filter: str,
        date_range_days: int
    ) -> str:
        """Phase 1: Search emails and enumerate attachments with preview"""
        try:
            # Step 1: Search for emails with attachments
            if self.valves.organizer_enable_progress_logging:
                self.log_debug("📧 Step 1: Searching for emails with attachments")
            
            # Add date filter to search query (only if not already present)
            has_date_filter = any(keyword in search_query.lower() for keyword in 
                                ['after:', 'before:', 'newer_than:', 'older_than:'])
            
            if has_date_filter:
                # User provided their own date filters, just ensure has:attachment is included
                if 'has:attachment' not in search_query.lower():
                    enhanced_query = f"{search_query} has:attachment"
                else:
                    enhanced_query = search_query
            else:
                # Add our default date filter
                date_filter = f" newer_than:{date_range_days}d"
                enhanced_query = f"{search_query} has:attachment{date_filter}"
            
            self.log_debug(f"🔍 Enhanced search query: '{enhanced_query}'")
            
            # Search emails
            search_result = self.search_emails(enhanced_query, max_emails, show_attachments=True)
            if search_result.startswith("❌"):
                return search_result
                
            # Parse email results from search output
            self.log_debug(f"📧 Search result to parse:\n{search_result[:500]}...")
            emails = self._parse_email_search_results(search_result)
            
            if not emails:
                return f"📭 **No emails found** matching query: '{search_query}'\n\nTry a broader search or check the date range ({date_range_days} days)."
            
            # Step 2: Enumerate attachments across all emails
            if self.valves.organizer_enable_progress_logging:
                self.log_debug(f"📎 Step 2: Enumerating attachments from {len(emails)} emails")
            
            total_attachments = 0
            organized_attachments = []
            
            # Process emails in batches for better performance
            batch_size = self.valves.organizer_batch_size
            for i in range(0, len(emails), batch_size):
                batch = emails[i:i + batch_size]
                batch_result = self._process_email_batch_for_attachments(
                    batch, attachment_filter, classification_prompt
                )
                
                if batch_result:
                    organized_attachments.extend(batch_result)
                    total_attachments += len(batch_result)
            
            # Step 3: Generate comprehensive preview report
            if self.valves.organizer_enable_progress_logging:
                self.log_debug(f"📊 Step 3: Generating preview report for {total_attachments} attachments")
            
            preview_report = self._generate_attachment_preview_report(
                organized_attachments, search_query, target_folder, dry_run, attachment_filter
            )
            
            # Step 4: Execute uploads if not dry run and target folder specified
            if not dry_run and target_folder and organized_attachments:
                upload_report = self._execute_attachment_uploads(organized_attachments, target_folder)
                return f"{preview_report}\n\n{upload_report}"
            
            return preview_report
            
        except Exception as e:
            self.log_error(f"Phase 1 processing failed: {e}")
            return f"❌ **Phase 1 Error**: {str(e)}"

    def _parse_email_search_results(self, search_output: str) -> List[Dict[str, str]]:
        """Parse email search results into structured data for processing"""
        try:
            emails = []
            lines = search_output.split('\n')
            current_email = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for numbered email entries like "1. **Subject**📎 2 files (1.2MB)"
                if re.match(r'^\d+\.\s+\*\*.*\*\*', line):
                    if current_email:  # Save previous email
                        emails.append(current_email)
                    current_email = {}
                    
                    # Extract subject (everything between ** and ** before any 📎)
                    subject_match = re.search(r'\*\*(.*?)\*\*', line)
                    if subject_match:
                        current_email['subject'] = subject_match.group(1).strip()
                    
                    # Extract attachment info if present
                    if '📎' in line:
                        attachment_match = re.search(r'📎\s+(\d+)\s+files?\s*\(([^)]+)\)', line)
                        if attachment_match:
                            current_email['attachment_summary'] = f"📎 {attachment_match.group(1)} files ({attachment_match.group(2)})"
                
                elif line.startswith('From:') and current_email:
                    current_email['from'] = line.replace('From:', '').strip()
                elif line.startswith('Date:') and current_email:
                    current_email['date'] = line.replace('Date:', '').strip()
                elif line.startswith('ID:') and current_email:
                    # Extract ID from backticks: ID: `email_id_here`
                    id_match = re.search(r'`([^`]+)`', line)
                    if id_match:
                        current_email['id'] = id_match.group(1).strip()
            
            # Don't forget the last email
            if current_email:
                emails.append(current_email)
            
            self.log_debug(f"Parsed {len(emails)} emails from search results")
            return emails
            
        except Exception as e:
            self.log_error(f"Failed to parse email search results: {e}")
            return []

    def _process_email_batch_for_attachments(
        self, 
        emails: List[Dict[str, str]], 
        attachment_filter: str, 
        classification_prompt: str
    ) -> List[Dict]:
        """Process a batch of emails to extract and classify attachments"""
        try:
            batch_attachments = []
            
            for email in emails:
                email_id = email.get('id')
                if not email_id:
                    continue
                    
                # Get attachment list for this email
                attachments_result = self.list_email_attachments(email_id)
                if attachments_result.startswith("❌"):
                    self.log_debug(f"Skipping email {email_id}: {attachments_result}")
                    continue
                
                # Parse attachments from the output
                self.log_debug(f"📎 Attachment list output for {email_id}:\n{attachments_result[:500]}...")
                attachments = self._parse_attachment_list(attachments_result, email_id)
                
                # Debug the parsed attachments
                for att in attachments:
                    self.log_debug(f"📎 Parsed attachment: {att.get('filename', 'unknown')} -> ID: {att.get('attachment_id', 'missing')[:50]}...")
                
                # Apply attachment filter if specified
                if attachment_filter:
                    attachments = self._filter_attachments_by_type(attachments, attachment_filter)
                
                # Add email context to each attachment
                for attachment in attachments:
                    attachment['email_context'] = {
                        'id': email_id,
                        'from': email.get('from', 'Unknown'),
                        'subject': email.get('subject', 'No Subject'),
                        'date': email.get('date', 'Unknown'),
                        'attachment_summary': email.get('attachment_summary', '')
                    }
                    
                    # Add LLM classification if enabled and prompt provided
                    if self.valves.llm_enabled and classification_prompt:
                        attachment['classification'] = self._classify_attachment_with_llm(
                            attachment, classification_prompt
                        )
                    
                    batch_attachments.append(attachment)
            
            self.log_debug(f"Processed batch: {len(batch_attachments)} attachments from {len(emails)} emails")
            return batch_attachments
            
        except Exception as e:
            self.log_error(f"Batch processing failed: {e}")
            return []

    def _parse_attachment_list(self, attachments_output: str, email_id: str) -> List[Dict]:
        """Parse attachment list output into structured data"""
        try:
            attachments = []
            lines = attachments_output.split('\n')
            current_attachment = {'email_id': email_id}
            
            self.log_debug(f"📎 Parsing {len(lines)} lines of attachment output")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Look for numbered attachment entries like "1. **filename.pdf**"
                if re.match(r'^\d+\.\s+\*\*.*\*\*', line):
                    if current_attachment.get('filename'):  # Save previous
                        attachments.append(current_attachment.copy())
                    current_attachment = {'email_id': email_id}
                    
                    # Extract filename (everything between ** and **)
                    filename_match = re.search(r'\*\*(.*?)\*\*', line)
                    if filename_match:
                        current_attachment['filename'] = filename_match.group(1).strip()
                    
                    # Extract index from the number
                    index_match = re.match(r'^(\d+)\.', line)
                    if index_match:
                        current_attachment['index'] = str(int(index_match.group(1)) - 1)  # Convert to 0-based
                
                elif line.startswith('📄 Type:') and current_attachment:
                    current_attachment['type'] = line.replace('📄 Type:', '').strip()
                elif line.startswith('📊 Size:') and current_attachment:
                    # Extract size, ignoring warnings
                    size_text = line.replace('📊 Size:', '').strip()
                    if '⚠️' in size_text:
                        size_text = size_text.split('⚠️')[0].strip()
                    current_attachment['size'] = size_text
                elif line.startswith('🔗 Attachment ID:') and current_attachment:
                    # Extract attachment ID from backticks - be very specific about the format
                    self.log_debug(f"📎 Line {line_num}: Processing attachment ID line: '{line}'")
                    id_match = re.search(r'🔗 Attachment ID:\s*`([^`]+)`', line)
                    if id_match:
                        attachment_id = id_match.group(1).strip()
                        # Debug log the found attachment ID
                        self.log_debug(f"📎 Found attachment ID: '{attachment_id}' (length: {len(attachment_id)})")
                        current_attachment['attachment_id'] = attachment_id
                    else:
                        self.log_debug(f"📎 No attachment ID match found in line: '{line}'")
                elif line.startswith('💾 Use:') and not current_attachment.get('attachment_id'):
                    # For inline attachments, extract the index from the usage line
                    # Format: 💾 Use: `download_email_attachment('email_id', '0', 'filename')`
                    use_match = re.search(r"download_email_attachment\('[^']*',\s*'([^']*)'", line)
                    if use_match:
                        attachment_id = use_match.group(1).strip()
                        current_attachment['attachment_id'] = attachment_id
                        self.log_debug(f"📎 Found inline attachment index from use line: '{attachment_id}'")
            
            # Don't forget the last attachment
            if current_attachment.get('filename'):
                attachments.append(current_attachment)
            
            self.log_debug(f"📎 Parsed {len(attachments)} attachments from output")
            return attachments
            
        except Exception as e:
            self.log_error(f"Failed to parse attachment list: {e}")
            return []

    def _filter_attachments_by_type(self, attachments: List[Dict], filter_type: str) -> List[Dict]:
        """Filter attachments by file type"""
        if not filter_type:
            return attachments
            
        filter_type = filter_type.lower()
        filtered = []
        
        for attachment in attachments:
            filename = attachment.get('filename', '').lower()
            file_type = attachment.get('type', '').lower()
            
            # Simple type matching
            if filter_type == 'pdf' and (filename.endswith('.pdf') or 'pdf' in file_type):
                filtered.append(attachment)
            elif filter_type == 'image' and any(ext in filename for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                filtered.append(attachment)
            elif filter_type == 'spreadsheet' and any(ext in filename for ext in ['.xlsx', '.xls', '.csv']):
                filtered.append(attachment)
            elif filter_type == 'document' and any(ext in filename for ext in ['.docx', '.doc', '.txt']):
                filtered.append(attachment)
            elif filter_type in filename or filter_type in file_type:
                filtered.append(attachment)
        
        return filtered

    def _call_llm_provider(self, prompt: str, context: Dict = None) -> Dict:
        """
        Unified LLM communication method supporting multiple providers
        
        Args:
            prompt: The prompt to send to the LLM
            context: Additional context for the request
            
        Returns:
            Dict with 'success', 'response', 'error' keys
        """
        if not self.valves.llm_enabled:
            return {
                'success': False,
                'response': None,
                'error': 'LLM integration is disabled'
            }
        
        try:
            provider = self.valves.llm_provider.lower()
            
            if provider == 'openai':
                return self._call_openai(prompt, context)
            elif provider == 'anthropic':
                return self._call_anthropic(prompt, context)
            elif provider == 'ollama':
                return self._call_ollama(prompt, context)
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Unsupported LLM provider: {provider}'
                }
                
        except Exception as e:
            self.log_error(f"LLM provider call failed: {e}")
            return {
                'success': False,
                'response': None,
                'error': str(e)
            }
    
    def _call_openai(self, prompt: str, context: Dict = None) -> Dict:
        """Call OpenAI-compatible API for attachment classification (supports OpenAI, Gemini, OpenRouter, etc.)"""
        try:
            import requests
            import json
            
            if not self.valves.llm_api_key:
                return {
                    'success': False,
                    'response': None,
                    'error': 'API key not configured'
                }
            
            # Determine API endpoint and authentication format
            base_api_url = self.valves.llm_api_url or "https://api.openai.com/v1/chat/completions"
            
            # Handle different authentication formats
            headers = {'Content-Type': 'application/json'}
            
            # Build the correct API URL first, before adding query parameters
            if 'googleapis.com' in base_api_url:
                # Google Gemini with OpenAI compatibility layer
                if not base_api_url.endswith('/chat/completions'):
                    if '/openai' in base_api_url:
                        api_url = base_api_url.rstrip('/') + '/chat/completions'
                    else:
                        api_url = base_api_url.rstrip('/') + '/openai/chat/completions'
                else:
                    api_url = base_api_url
                
                # Add Google API authentication
                headers['Authorization'] = f'Bearer {self.valves.llm_api_key}'
                # Add API key as query parameter for Gemini
                if '?' not in api_url:
                    api_url += f'?key={self.valves.llm_api_key}'
                else:
                    api_url += f'&key={self.valves.llm_api_key}'
                    
            elif 'openrouter.ai' in base_api_url:
                # OpenRouter authentication
                api_url = base_api_url if base_api_url.endswith('/chat/completions') else base_api_url.rstrip('/') + '/chat/completions'
                headers['Authorization'] = f'Bearer {self.valves.llm_api_key}'
                headers['HTTP-Referer'] = 'https://github.com/anthropics/claude-code'
                headers['X-Title'] = 'Google Workspace Smart Organizer'
            else:
                # Standard OpenAI-compatible authentication (OpenAI, local providers, etc.)
                api_url = base_api_url if base_api_url.endswith('/chat/completions') else base_api_url.rstrip('/') + '/v1/chat/completions'
                headers['Authorization'] = f'Bearer {self.valves.llm_api_key}'
            
            data = {
                'model': self.valves.llm_model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert document classifier. Analyze email attachments and provide structured responses in JSON format.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.1,
                'max_tokens': 500
            }
            
            self.log_debug(f"📡 Making LLM API call to: {api_url}")
            self.log_debug(f"📡 Model: {self.valves.llm_model}")
            self.log_debug(f"📡 Headers: {list(headers.keys())}")
            self.log_debug(f"📡 Request data keys: {list(data.keys())}")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=self.valves.llm_timeout_seconds
            )
            
            self.log_debug(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.log_debug(f"📡 Response structure: {list(result.keys())}")
                
                # Handle different response formats
                content = None
                if 'choices' in result and result['choices']:
                    # Standard OpenAI format
                    content = result['choices'][0]['message']['content']
                elif 'candidates' in result and result['candidates']:
                    # Google Gemini format
                    content = result['candidates'][0]['content']['parts'][0]['text']
                elif 'response' in result:
                    # Some other format
                    content = result['response']
                
                if content:
                    self.log_debug(f"📡 LLM Response content: {content[:200]}...")
                    return {
                        'success': True,
                        'response': content,
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'response': None,
                        'error': f'Unknown response format: {result}'
                    }
            else:
                error_text = response.text
                try:
                    error_json = response.json()
                    if 'error' in error_json:
                        error_text = str(error_json['error'])
                except:
                    pass
                
                return {
                    'success': False,
                    'response': None,
                    'error': f'API error ({response.status_code}): {error_text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'API call failed: {str(e)}'
            }
    
    def _call_anthropic(self, prompt: str, context: Dict = None) -> Dict:
        """Call Anthropic API for attachment classification"""
        try:
            import requests
            import json
            
            if not self.valves.llm_api_key:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Anthropic API key not configured'
                }
            
            headers = {
                'x-api-key': self.valves.llm_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.valves.llm_model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.1
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=self.valves.llm_timeout_seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                return {
                    'success': True,
                    'response': content,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Anthropic API error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Anthropic call failed: {str(e)}'
            }
    
    def _call_ollama(self, prompt: str, context: Dict = None) -> Dict:
        """Call Ollama API for attachment classification"""
        try:
            import requests
            import json
            
            api_url = self.valves.llm_api_url or "http://localhost:11434"
            if not api_url.endswith('/api/generate'):
                api_url = f"{api_url.rstrip('/')}/api/generate"
            
            data = {
                'model': self.valves.llm_model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 500
                }
            }
            
            response = requests.post(
                api_url,
                json=data,
                timeout=self.valves.llm_timeout_seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                return {
                    'success': True,
                    'response': content,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Ollama API error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Ollama call failed: {str(e)}'
            }
    
    def _build_classification_prompt(self, email_content: Dict, attachments: list) -> str:
        """Build optimized prompt for attachment classification"""
        
        # Extract key email information
        subject = email_content.get('subject', 'No subject')
        sender = email_content.get('sender', 'Unknown sender')
        body_preview = email_content.get('body_preview', '')[:self.valves.organizer_email_context_chars]
        
        # Build attachment summary
        attachment_summary = []
        for i, att in enumerate(attachments):
            filename = att.get('filename', f'attachment_{i}')
            filetype = att.get('type', 'unknown')
            size = att.get('size', 'unknown size')
            attachment_summary.append(f"- {filename} ({filetype}, {size})")
        
        prompt = f"""Analyze this email and its attachments to determine relevance for document organization.

EMAIL CONTEXT:
Subject: {subject}
From: {sender}
Body Preview: {body_preview}

ATTACHMENTS:
{chr(10).join(attachment_summary)}

CLASSIFICATION RULES (STRICT):
1. **FILENAME IS KING**: For PDFs, prioritize filename content over email subject
2. **AUTO-EXCLUDE**: Files with "banner", "logo", "advert", "advertisement", "promo", "marketing" in filename are NOT relevant
3. **NUMERICAL PATTERNS**: Look for account numbers, reference numbers, or dates in filenames (e.g., "12345_20240721.pdf")
4. **SINGLE BEST MATCH**: If multiple attachments, identify the ONE most likely invoice/statement/document
5. **BE CONSERVATIVE**: When in doubt, mark as not relevant rather than guessing

RELEVANT DOCUMENT TYPES:
- Statements with account numbers in filename
- Invoices with reference numbers
- Bills with clear identifying patterns
- Tax documents with official formatting
- Receipts with transaction details

Analyze each attachment and respond with valid JSON in this exact format:
{{
  "classifications": [
    {{
      "filename": "exact_filename_here",
      "relevant": true/false,
      "confidence": 0.0-1.0,
      "reasoning": "brief explanation focusing on filename analysis",
      "suggested_folder": "recommended/folder/path"
    }}
  ]
}}

FOLDER SUGGESTIONS:
- Statements → "Statements/[Provider]"
- Invoices → "Finance/Invoices/YYYY" 
- Tax docs → "Tax Documents/YYYY"
- Receipts → "Finance/Receipts/YYYY"
- Bills → "Bills/[Utility]/YYYY"

Respond only with valid JSON, no additional text."""

        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse and validate LLM JSON response"""
        try:
            import json
            import re
            
            self.log_debug(f"🔍 Parsing LLM response: {response[:300]}...")
            
            # Try to extract JSON from response (handle potential markdown formatting)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                self.log_debug(f"🔍 Extracted JSON: {json_str[:200]}...")
            else:
                json_str = response.strip()
                self.log_debug(f"🔍 Using full response as JSON: {json_str[:200]}...")
            
            # Parse the JSON
            parsed = json.loads(json_str)
            self.log_debug(f"🔍 Parsed JSON structure: {list(parsed.keys())}")
            
            # Handle both array format and single object format
            if 'classifications' in parsed:
                # Standard array format: {"classifications": [...]}
                classifications = parsed['classifications']
                if not isinstance(classifications, list):
                    return None
                    
                # Validate each classification
                for classification in classifications:
                    required_keys = ['relevant', 'confidence', 'reasoning']
                    if not all(key in classification for key in required_keys):
                        return None
                    
                    # Ensure confidence is in valid range
                    confidence = classification.get('confidence', 0.0)
                    if not (0.0 <= confidence <= 1.0):
                        classification['confidence'] = max(0.0, min(1.0, confidence))
                
                return parsed
                
            elif all(key in parsed for key in ['relevant', 'confidence', 'reasoning']):
                # Single object format: {"relevant": true, "confidence": 0.95, ...}
                self.log_debug("🔍 Converting single classification to array format")
                
                # Ensure confidence is in valid range
                confidence = parsed.get('confidence', 0.0)
                if not (0.0 <= confidence <= 1.0):
                    parsed['confidence'] = max(0.0, min(1.0, confidence))
                
                # Convert to array format
                return {
                    'classifications': [parsed]
                }
            else:
                self.log_debug(f"🔍 Invalid structure - missing required keys. Found: {list(parsed.keys())}")
                return None
            
        except Exception as e:
            self.log_error(f"Failed to parse LLM response: {e}")
            return None
    
    def _suggest_folder_path(self, classification: Dict, target_folder: str = None) -> str:
        """Determine optimal folder path based on classification, user preferences, and context"""
        
        # Get LLM suggestion
        suggested_folder = classification.get('suggested_folder')
        confidence = classification.get('confidence', 0.0)
        
        # If user specified a target folder, respect their choice
        if target_folder:
            if self.valves.llm_smart_folders and confidence >= self.valves.llm_confidence_threshold and suggested_folder:
                # Smart folders enabled + high confidence: use LLM suggestion as subfolder
                return f"{target_folder.rstrip('/')}/{suggested_folder.split('/')[-1]}"
            else:
                # User specified folder takes precedence (keeps statements together)
                return target_folder
        
        # No target folder specified - use LLM suggestions if available and enabled
        if self.valves.llm_smart_folders and confidence >= self.valves.llm_confidence_threshold and suggested_folder:
            return suggested_folder
        
        # Fallback to default folder from valves or date-based organization
        if hasattr(self.valves, 'drive_default_folder') and self.valves.drive_default_folder:
            return self.valves.drive_default_folder
        
        # Last resort: use date-based organization
        from datetime import datetime
        current_year = datetime.now().year
        return f"Attachments/{current_year}"
    
    def _classify_attachment_with_llm(self, attachment: Dict, classification_prompt: str) -> Dict:
        """Classify attachment using LLM with enhanced Phase 2 implementation"""
        
        # Check if LLM is enabled
        if not self.valves.llm_enabled:
            # Phase 1 fallback
            return {
                'relevant': True,
                'confidence': 0.6,
                'reasoning': 'LLM disabled - using Phase 1 fallback (assumed relevant)',
                'suggested_folder': None
            }
        
        try:
            # Get email context from attachment
            email_context = attachment.get('email_context', {})
            
            # Build classification prompt if not provided
            if not classification_prompt:
                prompt = self._build_classification_prompt(email_context, [attachment])
            else:
                # Use custom prompt format
                filename = attachment.get('filename', 'unknown')
                filetype = attachment.get('type', 'unknown')
                subject = email_context.get('subject', 'No subject')
                sender = email_context.get('sender', 'Unknown')
                
                prompt = f"""{classification_prompt}

EMAIL: From {sender}, Subject: "{subject}"
ATTACHMENT: {filename} ({filetype})

Respond with JSON: {{"relevant": true/false, "confidence": 0.0-1.0, "reasoning": "explanation", "suggested_folder": "path/to/folder"}}"""
            
            # Call LLM
            llm_result = self._call_llm_provider(prompt)
            
            if not llm_result['success']:
                # LLM failed - use Phase 1 fallback
                return {
                    'relevant': True,
                    'confidence': 0.5,
                    'reasoning': f'LLM call failed: {llm_result["error"]} - using fallback',
                    'suggested_folder': None
                }
            
            # Parse LLM response
            parsed_response = self._parse_llm_response(llm_result['response'])
            
            if parsed_response and 'classifications' in parsed_response:
                classifications = parsed_response['classifications']
                if classifications:
                    # Return first classification (single attachment)
                    classification = classifications[0]
                    return {
                        'relevant': classification.get('relevant', True),
                        'confidence': classification.get('confidence', 0.7),
                        'reasoning': classification.get('reasoning', 'LLM classification'),
                        'suggested_folder': classification.get('suggested_folder')
                    }
            
            # Parsing failed - try simple JSON extraction
            try:
                import json
                simple_response = json.loads(llm_result['response'])
                return {
                    'relevant': simple_response.get('relevant', True),
                    'confidence': simple_response.get('confidence', 0.7),
                    'reasoning': simple_response.get('reasoning', 'LLM classification'),
                    'suggested_folder': simple_response.get('suggested_folder')
                }
            except:
                pass
            
            # All parsing failed - use Phase 1 fallback
            return {
                'relevant': True,
                'confidence': 0.5,
                'reasoning': 'LLM response parsing failed - using fallback',
                'suggested_folder': None
            }
            
        except Exception as e:
            self.log_error(f"LLM classification error: {e}")
            return {
                'relevant': True,
                'confidence': 0.4,
                'reasoning': f'LLM error: {str(e)} - using fallback',
                'suggested_folder': None
            }

    def _generate_attachment_preview_report(
        self,
        attachments: List[Dict],
        search_query: str,
        target_folder: str,
        dry_run: bool,
        attachment_filter: str
    ) -> str:
        """Generate comprehensive preview report for found attachments"""
        try:
            if not attachments:
                return f"📭 **No attachments found** matching criteria\n\n**Search**: {search_query}\n**Filter**: {attachment_filter or 'None'}"
            
            # Group attachments by email for better organization
            emails_with_attachments = {}
            total_size = 0
            
            for attachment in attachments:
                email_context = attachment.get('email_context', {})
                email_id = email_context.get('id', 'unknown')
                
                if email_id not in emails_with_attachments:
                    emails_with_attachments[email_id] = {
                        'email_info': email_context,
                        'attachments': []
                    }
                
                emails_with_attachments[email_id]['attachments'].append(attachment)
                
                # Calculate total size
                size_str = attachment.get('size', '0 B')
                try:
                    if 'MB' in size_str:
                        total_size += float(size_str.replace(' MB', ''))
                    elif 'KB' in size_str:
                        total_size += float(size_str.replace(' KB', '')) / 1024
                except:
                    pass
            
            # Calculate LLM insights for summary
            llm_relevant = 0
            llm_high_confidence = 0
            llm_suggested_folders = 0
            
            for attachment in attachments:
                classification = attachment.get('classification', {})
                if classification.get('relevant', True):
                    llm_relevant += 1
                if classification.get('confidence', 0.6) >= self.valves.llm_confidence_threshold:
                    llm_high_confidence += 1
                if classification.get('suggested_folder'):
                    llm_suggested_folders += 1
            
            # Generate enhanced report
            report = f"🔍 **Smart Attachment Organizer Preview (Phase 2)**\n\n"
            report += f"**Search Query**: {search_query}\n"
            report += f"**Filter Applied**: {attachment_filter or 'None'}\n"
            report += f"**Target Folder**: {target_folder or 'Auto-suggest based on LLM'}\n"
            report += f"**LLM Classification**: {'Enabled' if self.valves.llm_enabled else 'Disabled (Phase 1 fallback)'}\n"
            report += f"**Mode**: {'🔍 Dry Run (Preview Only)' if dry_run else '📤 Upload Mode'}\n\n"
            
            report += f"**📊 Discovery Summary**:\n"
            report += f"• **Emails processed**: {len(emails_with_attachments)}\n"
            report += f"• **Attachments found**: {len(attachments)}\n"
            report += f"• **Total size**: ~{total_size:.1f} MB\n\n"
            
            # Add LLM insights if enabled
            if self.valves.llm_enabled:
                report += f"**🤖 LLM Classification Summary**:\n"
                report += f"• **Relevant attachments**: {llm_relevant}/{len(attachments)}\n"
                report += f"• **High confidence classifications**: {llm_high_confidence}/{len(attachments)}\n"
                report += f"• **Smart folder suggestions**: {llm_suggested_folders}/{len(attachments)}\n"
                report += f"• **Confidence threshold**: {self.valves.llm_confidence_threshold}\n\n"
            
            # Detailed attachment listing
            report += f"**📎 Detailed Attachment List**:\n\n"
            
            for email_id, email_data in emails_with_attachments.items():
                email_info = email_data['email_info']
                email_attachments = email_data['attachments']
                
                report += f"**Email**: {email_info.get('subject', 'No Subject')}\n"
                report += f"• **From**: {email_info.get('from', 'Unknown')}\n"
                report += f"• **Date**: {email_info.get('date', 'Unknown')}\n"
                report += f"• **Message ID**: `{email_id}`\n"
                report += f"• **Attachments**: {len(email_attachments)} files\n\n"
                
                for i, attachment in enumerate(email_attachments, 1):
                    filename = attachment.get('filename', 'unknown')
                    size = attachment.get('size', 'unknown')
                    file_type = attachment.get('type', 'unknown')
                    
                    report += f"  **{i}.** `{filename}`\n"
                    report += f"     • **Size**: {size}\n"
                    report += f"     • **Type**: {file_type}\n"
                    
                    # Enhanced LLM classification info
                    classification = attachment.get('classification', {})
                    if self.valves.llm_enabled and classification:
                        relevant = classification.get('relevant', True)
                        confidence = classification.get('confidence', 0.6)
                        reasoning = classification.get('reasoning', 'No reasoning provided')
                        suggested_folder = classification.get('suggested_folder')
                        
                        # Relevance with confidence indicator
                        relevance_icon = "✅" if relevant else "❌"
                        confidence_icon = "🎯" if confidence >= self.valves.llm_confidence_threshold else "⚡"
                        
                        report += f"     • **LLM Analysis**: {relevance_icon} {'Relevant' if relevant else 'Not relevant'} {confidence_icon} ({confidence:.0%} confidence)\n"
                        report += f"     • **Reasoning**: {reasoning}\n"
                        
                        if suggested_folder:
                            report += f"     • **Suggested Folder**: `{suggested_folder}`\n"
                        
                        # Upload action indicator
                        if dry_run:
                            if not relevant and confidence >= 0.7:
                                # High confidence that file is not relevant - would skip
                                upload_action = f"⏭️ Would skip (not relevant, {confidence:.0%} confidence)"
                            else:
                                # Would upload (either relevant, or low confidence about irrelevance)
                                upload_action = "🔄 Would upload"
                                final_folder = self._suggest_folder_path(classification, target_folder)
                                if final_folder and final_folder != target_folder:
                                    upload_action += f" to `{final_folder}`"
                            report += f"     • **Action**: {upload_action}\n"
                    
                    elif not self.valves.llm_enabled:
                        report += f"     • **Classification**: Phase 1 fallback (assumed relevant)\n"
                    
                    report += "\n"
                
                report += "---\n\n"
            
            # Action summary
            if dry_run:
                report += f"🔍 **This is a preview only**. Use `dry_run=False` and specify a `target_folder` to actually upload files.\n\n"
                report += f"**Next Steps**:\n"
                report += f"1. Review the attachments above\n"
                report += f"2. Specify a target folder (folder name, path, or ID)\n"
                report += f"3. Set `dry_run=False` to execute uploads\n"
            elif not target_folder:
                report += f"⚠️ **No target folder specified**. Files will not be uploaded. Please specify a `target_folder` parameter.\n"
            else:
                report += f"📤 **Ready to upload** {len(attachments)} attachments to: `{target_folder}`\n"
            
            return report
            
        except Exception as e:
            self.log_error(f"Failed to generate preview report: {e}")
            return f"❌ **Error generating preview**: {str(e)}"

    def _execute_attachment_uploads(self, attachments: List[Dict], target_folder: str) -> str:
        """Execute the actual upload of attachments to Drive with LLM-enhanced folder assignment"""
        try:
            if not attachments:
                return "📭 **No attachments to upload**"
            
            upload_report = f"📤 **Executing Smart Attachment Uploads (Phase 2)**\n\n"
            upload_report += f"**Base Target Folder**: {target_folder or 'Auto-suggest based on LLM'}\n"
            upload_report += f"**LLM Classification**: {'Enabled' if self.valves.llm_enabled else 'Disabled (Phase 1 fallback)'}\n"
            upload_report += f"**Attachments to process**: {len(attachments)}\n\n"
            
            successful_uploads = 0
            failed_uploads = 0
            skipped_uploads = 0
            upload_details = []
            llm_insights = []
            
            # Process uploads one by one with enhanced LLM logic
            for i, attachment in enumerate(attachments, 1):
                try:
                    email_id = attachment.get('email_id')
                    attachment_id = attachment.get('attachment_id')
                    filename = attachment.get('filename', f'attachment_{i}')
                    classification = attachment.get('classification', {})
                    
                    if not email_id or not attachment_id:
                        failed_uploads += 1
                        upload_details.append(f"❌ **{i}.** `{filename}` - Missing email or attachment ID")
                        continue
                    
                    # Get LLM classification data
                    relevant = classification.get('relevant', True)
                    confidence = classification.get('confidence', 0.6)
                    reasoning = classification.get('reasoning', 'No classification available')
                    suggested_folder = classification.get('suggested_folder')
                    
                    # Enhanced progress logging with LLM data
                    if self.valves.organizer_enable_progress_logging:
                        self.log_debug(f"🚀 Processing {i}/{len(attachments)}: {filename}")
                        self.log_debug(f"   📧 Email ID: {email_id}")
                        self.log_debug(f"   📎 Attachment ID: {attachment_id[:50]}...")
                        self.log_debug(f"   🤖 LLM Relevant: {relevant}, Confidence: {confidence:.2f}")
                        self.log_debug(f"   🤖 LLM Reasoning: {reasoning}")
                        self.log_debug(f"   📁 LLM Suggested Folder: {suggested_folder}")
                    
                    # Confidence-based upload decision
                    if not relevant and confidence >= 0.7:
                        # High confidence that file is not relevant - skip it
                        skipped_uploads += 1
                        if self.valves.organizer_enable_progress_logging:
                            self.log_debug(f"   ⏭️ SKIPPING: Not relevant with high confidence ({confidence:.2f})")
                        upload_details.append(
                            f"⏭️ **{i}.** `{filename}` - Skipped (LLM confidence {confidence:.2f}: {reasoning})"
                        )
                        continue
                    
                    # Determine optimal upload folder
                    upload_folder = self._suggest_folder_path(classification, target_folder)
                    
                    # Add LLM insight for reporting
                    llm_insights.append({
                        'filename': filename,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'suggested_folder': suggested_folder,
                        'final_folder': upload_folder,
                        'relevant': relevant
                    })
                    
                    if self.valves.organizer_enable_progress_logging:
                        self.log_debug(f"   📁 Final upload folder: {upload_folder}")
                    
                    # Use index instead of attachment_id since Gmail IDs change between calls
                    attachment_index = attachment.get('index', '0')
                    upload_result = self.upload_attachment_to_drive(
                        email_id, attachment_index, upload_folder, filename
                    )
                    
                    # Enhanced result logging with LLM context
                    if self.valves.organizer_enable_progress_logging:
                        self.log_debug(f"📤 Upload result for {filename}: {upload_result[:200]}...")
                    
                    if upload_result.startswith("✅"):
                        successful_uploads += 1
                        confidence_indicator = "🎯" if confidence >= self.valves.llm_confidence_threshold else "⚡"
                        folder_note = f" → `{upload_folder}`" if upload_folder != target_folder else ""
                        upload_details.append(
                            f"✅ **{i}.** `{filename}` {confidence_indicator} (confidence: {confidence:.2f}){folder_note}"
                        )
                    else:
                        failed_uploads += 1
                        # Extract more detailed error message
                        if "**Error" in upload_result:
                            error_msg = upload_result.split("**Error")[-1].strip()
                        elif "❌" in upload_result:
                            error_msg = upload_result.split("❌")[-1].strip()
                        else:
                            error_msg = upload_result.strip()
                        
                        # Log the full error for debugging
                        if self.valves.organizer_enable_progress_logging:
                            self.log_debug(f"❌ Upload failed for {filename}: {upload_result}")
                        
                        upload_details.append(f"❌ **{i}.** `{filename}` - {error_msg[:100]}...")
                        
                except Exception as e:
                    failed_uploads += 1
                    upload_details.append(f"❌ **{i}.** `{filename}` - Exception: {str(e)}")
            
            # Generate enhanced final report with LLM insights
            upload_report += f"**📊 Enhanced Upload Results**:\n"
            upload_report += f"• **Successful**: {successful_uploads}\n"
            upload_report += f"• **Failed**: {failed_uploads}\n"
            upload_report += f"• **Skipped**: {skipped_uploads} (not relevant per LLM)\n"
            total_processed = successful_uploads + failed_uploads + skipped_uploads
            if total_processed > 0:
                upload_report += f"• **Success Rate**: {(successful_uploads/total_processed*100):.1f}%\n\n"
            
            # Add LLM insights section if enabled
            if self.valves.llm_enabled and llm_insights:
                upload_report += f"**🤖 LLM Classification Insights**:\n"
                high_confidence = sum(1 for insight in llm_insights if insight['confidence'] >= self.valves.llm_confidence_threshold)
                avg_confidence = sum(insight['confidence'] for insight in llm_insights) / len(llm_insights)
                upload_report += f"• **High Confidence Classifications**: {high_confidence}/{len(llm_insights)}\n"
                upload_report += f"• **Average Confidence**: {avg_confidence:.2f}\n"
                upload_report += f"• **Smart Folder Suggestions**: {sum(1 for insight in llm_insights if insight['suggested_folder'])}\n\n"
            
            upload_report += f"**📋 Detailed Results**:\n"
            for detail in upload_details:
                upload_report += f"{detail}\n"
            
            # Enhanced status messages
            if failed_uploads > 0:
                upload_report += f"\n⚠️ **{failed_uploads} uploads failed**. Check the details above for specific error messages."
            
            if skipped_uploads > 0:
                upload_report += f"\n💡 **{skipped_uploads} files skipped** based on LLM relevance analysis. Adjust `llm_confidence_threshold` if needed."
            
            if self.valves.llm_enabled and successful_uploads > 0:
                upload_report += f"\n🎯 **Smart folder organization** used LLM suggestions for optimal file placement."
            
            return upload_report
            
        except Exception as e:
            self.log_error(f"Enhanced upload execution failed: {e}")
            return f"❌ **Enhanced upload execution error**: {str(e)}"

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

def get_recent_emails(count: int = 20, hours_back: int = 24, show_attachments: bool = True) -> str:
    """Get recent emails from Gmail inbox with optional attachment indicators"""
    tool = Tools()
    return tool.get_recent_emails(count, hours_back, show_attachments)

def search_emails(query: str, max_results: int = 10, show_attachments: bool = True) -> str:
    """Search emails using Gmail search syntax (use 'has:attachment' to find emails with attachments)"""
    tool = Tools()
    return tool.search_emails(query, max_results, show_attachments)

def get_email_content(email_id: str = None, subject_contains: str = None, from_sender: str = None) -> str:
    """
    Get full content of a specific email - supports smart searching
    
    Args:
        email_id: Gmail message ID (if provided, other params ignored)  
        subject_contains: Search for emails containing this text in subject
        from_sender: Search for emails from this sender
        
    Examples:
        get_email_content("1abc123")  # By ID
        get_email_content(subject_contains="meeting")  # By subject
        get_email_content(from_sender="john@company.com", subject_contains="project")  # Combined
    """
    tool = Tools()
    return tool.get_email_content(email_id, subject_contains, from_sender)

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

# Attachment functions
def list_email_attachments(email_id: str) -> str:
    """List all attachments in a specific email with metadata"""
    tool = Tools()
    return tool.list_email_attachments(email_id)

def download_email_attachment(email_id: str, attachment_identifier: str, filename: str = None) -> str:
    """Download a specific attachment from an email by ID or index"""
    tool = Tools()
    return tool.download_email_attachment(email_id, attachment_identifier, filename)

def extract_all_attachments(email_id: str) -> str:
    """Extract and download all attachments from an email"""
    tool = Tools()
    return tool.extract_all_attachments(email_id)

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

def create_event_smart(title: str, start_time: str, end_time: str = None, 
                      calendar_hint: str = None, description: str = None, 
                      location: str = None) -> str:
    """Create an event with smart calendar selection"""
    tool = Tools()
    return tool.create_event_smart(title, start_time, end_time, calendar_hint, description, location)

def search_calendar_events(query: str, days_back: int = 30, days_ahead: int = 30, 
                          calendar_names: str = None) -> str:
    """Search for events across calendars using text query"""
    tool = Tools()
    return tool.search_calendar_events(query, days_back, days_ahead, calendar_names)

def get_todays_schedule() -> str:
    """Get today's schedule with imminent event warnings for daily briefings"""
    tool = Tools()
    return tool.get_todays_schedule()

def search_contacts(query: str, max_results: int = 10) -> str:
    """Search contacts by name, email, phone, or organization"""
    tool = Tools()
    return tool.search_contacts(query, max_results)

def lookup_contact_by_email(email_address: str) -> str:
    """Find contact by specific email address"""
    tool = Tools()
    return tool.lookup_contact_by_email(email_address)

def get_contact_details(person_resource_name: str) -> str:
    """Get comprehensive details for a specific contact by resource name"""
    tool = Tools()
    return tool.get_contact_details(person_resource_name)

def list_recent_contacts(limit: int = 20) -> str:
    """List recently added or modified contacts"""
    tool = Tools()
    return tool.list_recent_contacts(limit)

def create_contact(name: str, email: str, phone: str = None, organization: str = None) -> str:
    """Create a new contact (write operation - includes duplicate detection)"""
    tool = Tools()
    return tool.create_contact(name, email, phone, organization)

# ========== TASKS PUBLIC FUNCTIONS ==========

def get_task_lists() -> str:
    """List all task lists available to the user"""
    tool = Tools()
    return tool.get_task_lists()

def create_task_list(name: str, description: str = None) -> str:
    """Create a new task list"""
    tool = Tools()
    return tool.create_task_list(name, description)

def update_task_list(list_id: str, name: str) -> str:
    """Update the name of an existing task list"""
    tool = Tools()
    return tool.update_task_list(list_id, name)

def delete_task_list(list_id: str) -> str:
    """Delete a task list (WARNING: This will delete all tasks in the list!)"""
    tool = Tools()
    return tool.delete_task_list(list_id)

def clear_completed_tasks(list_id: str) -> str:
    """Clear all completed tasks from a task list"""
    tool = Tools()
    return tool.clear_completed_tasks(list_id)

def get_tasks(list_id: str, show_completed: bool = None, show_hidden: bool = False) -> str:
    """
    Get tasks from a specific task list with filtering options
    
    Args:
        list_id: Task list ID or name (e.g., "@default", "Personal Tasks", or full ID)
        show_completed: Whether to show completed tasks
        show_hidden: Whether to show hidden tasks
        
    Examples:
        get_tasks("@default")  # Default list
        get_tasks("Personal")  # Find list by name  
        get_tasks("Work Tasks", show_completed=True)  # Include completed
    """
    tool = Tools()
    return tool.get_tasks(list_id, show_completed, show_hidden)

def create_task_with_smart_list_selection(title: str, notes: str = None, due_date: str = None, 
                                        list_hint: str = None, parent_id: str = None) -> str:
    """Create a task with smart list selection (similar to smart calendar selection)"""
    tool = Tools()
    return tool.create_task_with_smart_list_selection(title, notes, due_date, list_hint, parent_id)

def create_task(list_id: str, title: str, notes: str = None, due_date: str = None, parent_id: str = None) -> str:
    """Create a task in a specific task list"""
    tool = Tools()
    return tool.create_task(list_id, title, notes, due_date, parent_id)

def update_task(list_id: str, task_id: str, title: str = None, notes: str = None, 
               due_date: str = None, status: str = None) -> str:
    """Update an existing task with new title, notes, due date, or status"""
    tool = Tools()
    return tool.update_task(list_id, task_id, title, notes, due_date, status)

def move_task(list_id: str, task_id: str, parent_id: str = None, previous_sibling_id: str = None) -> str:
    """Move a task to a different position or make it a subtask"""
    tool = Tools()
    return tool.move_task(list_id, task_id, parent_id, previous_sibling_id)

def delete_task(list_id: str, task_id: str) -> str:
    """Delete a task and all its subtasks"""
    tool = Tools()
    return tool.delete_task(list_id, task_id)

def mark_task_complete(list_id: str, task_id: str) -> str:
    """Mark a task as completed"""
    tool = Tools()
    return tool.mark_task_complete(list_id, task_id)

# ========== DRIVE PUBLIC FUNCTIONS ==========

def search_drive(query: str, max_results: int = 20) -> str:
    """Search for files in Google Drive using query syntax"""
    tool = Tools()
    return tool.search_drive_files(query, max_results)

def list_drive_folder(folder_name_or_id: str = None, max_results: int = 50) -> str:
    """List files in a specific Drive folder or root folder"""
    tool = Tools()
    if folder_name_or_id and not folder_name_or_id.startswith('1'):
        # Looks like a folder name, try to find it first
        search_result = tool.search_drive_files(f"name='{folder_name_or_id}' and mimeType='application/vnd.google-apps.folder'", 5)
        if "No files found" in search_result:
            return f"📁 **Folder not found**: {folder_name_or_id}"
        # For simplicity, just use the search result instead of extracting ID
        return search_result
    return tool.list_drive_files(folder_name_or_id, max_results)

def get_drive_file_details(file_id: str) -> str:
    """
    Get comprehensive details for a specific Drive file
    
    Args:
        file_id: Google Drive file ID or filename (will search by name if not an ID)
        
    Examples:
        get_drive_file_details("1BxiMVs0XRA...")  # By ID
        get_drive_file_details("Budget 2024.xlsx")  # By filename
    """
    tool = Tools()
    return tool.get_drive_file_details(file_id)

def download_drive_file(file_id: str, local_filename: str = None) -> str:
    """
    Download a file from Google Drive to local storage
    
    Args:
        file_id: Google Drive file ID or filename (will search by name if not an ID)
        local_filename: Optional custom filename for local storage
        
    Examples:
        download_drive_file("1BxiMVs0XRA...")  # By ID
        download_drive_file("quarterly-report.pdf")  # By filename
    """
    tool = Tools()
    return tool.download_drive_file(file_id, local_filename)

def upload_file_to_drive(local_path: str, parent_folder_id: str = None, filename: str = None) -> str:
    """Upload a local file to Google Drive"""
    tool = Tools()
    return tool.upload_file_to_drive(local_path, parent_folder_id, filename)

def create_drive_folder(folder_name: str, parent_folder_id: str = None) -> str:
    """Create a new folder in Google Drive"""
    tool = Tools()
    return tool.create_drive_folder(folder_name, parent_folder_id)

def get_drive_folders(parent_folder_id: str = None) -> str:
    """List folders in Drive or within a specific parent folder"""
    tool = Tools()
    return tool.get_drive_folders(parent_folder_id)

def upload_attachments_to_drive(email_id: str, folder_strategy: str = "auto", target_folder: str = None) -> str:
    """Upload all email attachments to Google Drive with smart organization"""
    tool = Tools()
    return tool.upload_email_attachments_to_drive(email_id, folder_strategy, target_folder)

def upload_attachment_to_drive(email_id: str, attachment_identifier: str, target_folder: str = None, custom_filename: str = None) -> str:
    """
    Upload a specific email attachment to Google Drive
    
    Args:
        email_id: Gmail message ID
        attachment_identifier: Attachment ID, index (0-based), filename, or position ("first", "last", etc.)
        target_folder: Drive folder ID, folder name, or path (None for auto organization)
        custom_filename: Custom filename for Drive (optional)
        
    Examples:
        upload_attachment_to_drive("email123", "0")  # First attachment by index
        upload_attachment_to_drive("email123", "invoice.pdf")  # By filename
        upload_attachment_to_drive("email123", "first", "Invoices")  # Simple folder name
        upload_attachment_to_drive("email123", "last", "Tax Documents/2024")  # Folder path
        upload_attachment_to_drive("email123", "0", "1BxiMVs0XRA...")  # Folder ID
    """
    tool = Tools()
    return tool.upload_attachment_to_drive(email_id, attachment_identifier, target_folder, custom_filename)

def get_drive_storage_info() -> str:
    """Get Google Drive storage usage and quota information"""
    tool = Tools()
    return tool.get_drive_storage_info_internal()

def smart_attachment_organizer(
    search_query: str = None,
    classification_prompt: str = None,
    target_folder: str = None,
    dry_run: bool = True,
    max_emails: int = 10,
    attachment_filter: str = None,
    date_range_days: int = 30
) -> str:
    """
    Phase 2: Smart Attachment Organizer with Enhanced LLM Classification
    
    Automatically search emails, use AI to classify attachment relevance and suggest 
    optimal folder organization, then upload to Drive with intelligent automation.
    
    Phase 2 Features:
    - Multi-provider LLM support (OpenAI, Anthropic, Ollama)
    - Intelligent relevance classification with confidence scoring
    - Smart folder path suggestions based on email content and attachment types
    - Confidence-based upload decisions (skip low-relevance files)
    - Enhanced reporting with LLM insights and reasoning
    
    Args:
        search_query: Gmail search query (e.g., "invoice OR receipt", "has:attachment project")
        classification_prompt: Custom LLM prompt for attachment classification (optional)
        target_folder: Base Drive folder (LLM can suggest subfolders for better organization)
        dry_run: If True, preview with AI analysis without uploading (default: True)
        max_emails: Maximum emails to process (1-50, default: 10)
        attachment_filter: File type filter (e.g., "pdf", "image", "spreadsheet")
        date_range_days: Limit search to emails from last N days (default: 30)
        
    LLM Configuration (in tool settings):
        llm_enabled: Enable AI classification (set to True for Phase 2 features)
        llm_provider: "openai", "anthropic", or "ollama" 
        llm_api_key: API key for cloud providers (OpenAI/Anthropic)
        llm_model: Model name (e.g., "gpt-3.5-turbo", "claude-3-haiku", "llama2")
        llm_confidence_threshold: Minimum confidence for auto-upload (0.0-1.0, default: 0.7)
        llm_smart_folders: Enable AI folder suggestions (default: True, disable to keep all files in target_folder)
        
    Examples:
        # Phase 2: AI-powered preview with smart folder suggestions
        smart_attachment_organizer("tax documents OR receipts", dry_run=True)
        
        # Phase 2: AI classification with auto-skip irrelevant files
        smart_attachment_organizer(
            search_query="invoice OR receipt", 
            target_folder="Finance/2024",
            dry_run=False  # LLM will suggest optimal subfolders
        )
        
        # Phase 2: Custom AI prompt for specialized classification
        smart_attachment_organizer(
            search_query="contract OR agreement",
            classification_prompt="Identify legal contracts and categorize by contract type",
            target_folder="Legal/Contracts",
            dry_run=False
        )
        
        # Keep all statements together (disable smart folders)
        smart_attachment_organizer(
            search_query="statement OR bill",
            target_folder="Financial/Statements/2024",
            dry_run=False  # All relevant files go to specified folder
        )
        
        # Phase 1 fallback: Works without LLM when llm_enabled=False
        smart_attachment_organizer("project files", target_folder="Projects", dry_run=False)
    """
    tool = Tools()
    return tool.smart_attachment_organizer(
        search_query, classification_prompt, target_folder,
        dry_run, max_emails, attachment_filter, date_range_days
    )

