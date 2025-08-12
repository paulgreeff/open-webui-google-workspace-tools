# Installation Guide

✅ **All functions are working perfectly** - This installation guide is verified and tested.

## Prerequisites

Before installing Google Workspace Tools, ensure you have:

1. **Open-WebUI** running (version 0.1.0 or later)
2. **Python dependencies** for Google APIs
3. **Google Cloud Console** access for API credentials

## Step 1: Install Python Dependencies

The tool requires several Google API client libraries. Install them in your Open-WebUI environment:

```bash
# Recommended: Use the requirements file
pip install -r requirements.txt

# Or install manually:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil pytz pydantic
```

## Step 2: Download the Tool

1. Download `google_workspace_tools.py` from this repository
2. Place it in your Open-WebUI tools directory (typically `/app/backend/tools/` in Docker installations)

## Step 3: Import in Open-WebUI

1. Open Open-WebUI admin panel
2. Navigate to **Tools** section
3. Click **Import Tool**
4. Select the `google_workspace_tools.py` file
5. Click **Import**

## Step 4: Verify Installation

The tool should now appear in your tools list as **Google Workspace Tools**. You'll see configuration options in the tool settings including:

- Authentication status
- Enabled services (gmail,calendar by default)
- Gmail settings (email count, content limits)
- Calendar settings (timezone, event duration)
- Debug options

## Next Steps

After installation, proceed to [Authentication Setup](authentication.md) to connect your Google account.

## Troubleshooting

### Import Errors
- **"No Tools class found"**: Ensure the file is named correctly and contains the `Tools` class
- **"Google API libraries not available"**: Install the required Python packages listed above

### Permission Issues
- Ensure the file is readable by the Open-WebUI process
- Check that your Open-WebUI installation allows custom tools

### Docker Installations
If running Open-WebUI in Docker, you may need to:
1. Mount the tools directory as a volume
2. Install Python packages in the container
3. Restart the container after adding the tool

For more help, see the main [README](../README.md) or check the [troubleshooting section](usage_examples.md#troubleshooting).