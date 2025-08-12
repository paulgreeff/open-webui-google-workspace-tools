# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ✅ **Current Status**: All Gmail and Calendar functions are fully working and production-ready with proper timezone handling.

## Project Overview

This is a Google Workspace integration tool for Open-WebUI, providing AI assistants with Gmail, Calendar, and Google Drive functionality. The project consists of a single Python module (`google_workspace_tools.py`) that implements a comprehensive Google Workspace API integration.

**Working Features:**
- ✅ Gmail: Full email management (read, search, create drafts, reply)
- ✅ Calendar: Complete calendar integration (events, scheduling, timezone-aware)
- 🚧 Future: Drive, Tasks, Contacts (planned)

## Architecture

### Core Components

- **Tools Class** (`google_workspace_tools.py:28-750`): Main integration class containing all Google Workspace functionality
- **Valves Class** (`google_workspace_tools.py:38-89`): Configuration settings for authentication and feature toggles
- **Authentication System** (`google_workspace_tools.py:142-278`): OAuth2 flow with token management and refresh
- **Gmail Functions** (`google_workspace_tools.py:280-506`): Email reading, searching, and draft creation
- **Public API Functions** (`google_workspace_tools.py:673-750`): Wrapper functions for LLM integration

### Key Features

1. **Authentication**: Two-step OAuth2 setup with credential management
2. **Gmail Integration**: Read emails, search, create drafts with threading support
3. **Extensible Design**: Prepared for Calendar, Drive, and Tasks integration
4. **Error Handling**: Comprehensive error handling with user-friendly messages
5. **Token Management**: Automatic token refresh and secure storage

### Data Storage

- Configuration and tokens stored in `/app/backend/data/google_tools/`
- Credentials saved as `credentials.json`
- OAuth tokens saved as `token.json`

## Development

### Dependencies

This is a Python tool requiring Google API client libraries:
- `google-auth`
- `google-auth-oauthlib` 
- `google-auth-httplib2`
- `google-api-python-client`

### Testing

No formal test framework is configured. The tool includes:
- Built-in authentication status checking
- Debug logging when `debug_mode` is enabled
- Error handling with detailed error messages

### Configuration

All configuration is handled through the `Valves` class including:
- Google OAuth2 credentials
- Enabled services (gmail, calendar, drive, tasks)
- Email fetch limits and content truncation
- Debug settings

## Open-WebUI Integration

This tool is designed as an Open-WebUI plugin where:
- The `Tools` class provides the main functionality
- Public functions at the bottom serve as the LLM-callable interface
- The `Valves` system handles user configuration through the Open-WebUI interface