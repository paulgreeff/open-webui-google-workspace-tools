# Authentication Setup

## Overview

Google Workspace Tools uses OAuth2 to securely connect to your Google account. This is a one-time setup process with guided steps.

## Step 1: Create Google Cloud Credentials

### 1.1 Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign in with your Google account
3. Create a new project or select an existing one

### 1.2 Enable APIs
Enable the following APIs for your project:
- **Gmail API** - for email functionality
- **Google Calendar API** - for calendar functionality
- **Google Drive API** - (future functionality)
- **Google Tasks API** - (future functionality)

To enable APIs:
1. Navigate to **APIs & Services** > **Library**
2. Search for each API and click **Enable**

### 1.3 Create OAuth2 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Desktop Application** as the application type
4. Give it a name (e.g., "Google Workspace Tools")
5. Click **Create**

### 1.4 Download Credentials
1. After creation, click the download button for your credentials
2. This downloads a JSON file with your client ID and secret
3. Open the JSON file and copy its entire contents

## Step 2: Configure in Open-WebUI

### 2.1 Access Tool Settings
1. In Open-WebUI, go to tool settings
2. Find **Google Workspace Tools**
3. Click on the settings/configuration icon

### 2.2 Paste Credentials
1. In the `credentials_json` field, paste the entire JSON content from Step 1.4
2. Ensure `enabled_services` includes the services you want: `gmail,calendar`
3. Set your timezone in `user_timezone` (e.g., "Europe/London", "America/New_York")
4. Save the settings

## Step 3: Complete Authentication

### 3.1 Start Authentication
1. Use the AI assistant to call: `setup_authentication()`
2. The tool will provide a Google authorization URL
3. Click the URL to open Google's permission page

### 3.2 Grant Permissions
1. Sign in to your Google account
2. Review the requested permissions:
   - Gmail: Read, compose, and modify emails
   - Calendar: Read and write calendar events
3. Click **Allow** to grant permissions
4. Copy the authorization code from the success page

### 3.3 Complete Setup
1. Paste the authorization code in the `auth_code` field in tool settings
2. Call: `complete_authentication()`
3. The tool will exchange the code for access tokens
4. You should see a success message confirming authentication

## Step 4: Verify Setup

Test your setup by running:
- `get_authentication_status()` - Should show your email address
- `get_calendars()` - Should list your calendars
- `get_recent_emails()` - Should show recent emails

## Security Notes

### Credential Storage
- Credentials are stored locally in your Open-WebUI data directory
- Files are located at `/app/backend/data/google_tools/`
- Only you have access to your credentials and tokens

### Token Refresh
- Access tokens are automatically refreshed when needed
- No re-authentication required unless you revoke access
- Refresh tokens are stored securely

### Revoking Access
To remove access:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "Google Workspace Tools" and click **Remove Access**
3. Delete the tool's data directory if desired

## Troubleshooting

### Common Issues

**"Invalid JSON in credentials field"**
- Ensure you copied the entire JSON file contents
- Check for missing brackets or quotes

**"Authorization code expired"**
- Authorization codes are single-use and expire quickly
- Generate a new URL with `setup_authentication()` and try again

**"Permission denied"**
- Verify you enabled the required APIs in Google Cloud Console
- Check that your Google account has access to the services

**"Token expired and cannot be refreshed"**
- This indicates the refresh token is invalid
- Re-run the complete authentication process

### Getting Help

If authentication fails:
1. Check the debug logs by enabling `debug_mode` in settings
2. Ensure your Google Cloud project has the correct APIs enabled
3. Verify your credentials JSON is complete and valid
4. Try the authentication process with a fresh authorization URL