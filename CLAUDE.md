# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ✅ **Current Status**: Gmail and Calendar fully working. Starting Phase 1: Google Contacts integration.

## Project Overview

This is a comprehensive Google Workspace integration tool for Open-WebUI, enabling AI assistants to manage Gmail, Calendar, Contacts, and planned future services. The project consists of a single Python module (`google_workspace_tools.py`) following Open-WebUI patterns.

**Working Features:**
- ✅ Gmail: Full email management (read, search, create drafts, reply)
- ✅ Calendar: Complete calendar integration (events, scheduling, timezone-aware)
- 🚧 **Phase 1 (In Progress)**: Google Contacts (People API) integration
- 🚧 **Phase 2 (Planned)**: Google Keep & Tasks for life organization
- 🚧 **Phase 3 (Planned)**: Google Drive for file management
- 🚧 **Phase 4 (Planned)**: Advanced features & multi-user support

## 📋 Development Roadmap

### Phase 1: Google Contacts Integration (CURRENT)
**Goal**: Enhance Gmail functionality with contact management
- **API**: Google People API with read-mostly approach
- **Functions**: `search_contacts()`, `lookup_contact_by_email()`, `get_contact_details()`, `create_contact()`
- **Strategy**: Standalone functions, user-controlled Gmail integration via prompts
- **Development**: `feature/contacts-integration` branch

### Phase 2: Life Organization Tools  
**Goal**: Productivity and task management
- **Google Keep API**: Notes management, email-to-notes, calendar reminders
- **Google Tasks API**: Todo management, calendar integration, email-to-tasks

### Phase 3: File Management
**Goal**: Document and file workflow automation
- **Google Drive API**: File search, upload, download, Gmail attachment integration

### Phase 4: Advanced Features
**Goal**: Complete productivity suite
- **Google Docs/Sheets/Slides**: Document automation
- **Google Meet/Chat**: Communication management  
- **Multi-user support**: Enterprise features
- **AI-powered insights**: Cross-service automation

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

Comprehensive test suite available in `tests/` directory:
- **Interactive test runner**: `python tests/test_runner.py`
- **Gmail function tests**: `python tests/test_gmail.py`
- **Calendar function tests**: `python tests/test_calendar.py`
- **Contacts tests**: `python tests/test_contacts.py` (Phase 1)
- **Framework**: Credential loading, authentication validation
- **Coverage**: All Gmail and Calendar functions verified working

Built-in diagnostics:
- Authentication status checking
- Debug logging when `debug_mode` is enabled
- Comprehensive error handling with user-friendly messages

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

## Development Strategy

### Branching Approach
- **`main` branch**: Stable, working code only
- **Feature branches**: `feature/[service]-integration` for each phase
- **Testing**: Comprehensive testing before merging to main
- **Commits**: Each phase committed separately with full functionality

### Phase-by-Phase Development
1. **Complete implementation** of all functions for a service
2. **Comprehensive testing** with dedicated test files
3. **Documentation updates** reflecting new functionality
4. **User validation** and feedback incorporation
5. **Commit to main** only when phase is fully working
6. **Assessment and planning** for next phase

### Current Development
- **Active branch**: `feature/contacts-integration`
- **Focus**: Google People API integration
- **Approach**: Read-mostly, standalone functions, user-controlled integration