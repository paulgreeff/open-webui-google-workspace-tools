# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ✅ **Current Status**: Gmail (with attachments), Calendar, Contacts, Tasks, and Google Drive fully working and **production-tested**.

## Project Overview

This is a comprehensive Google Workspace integration tool for Open-WebUI, enabling AI assistants to manage Gmail, Calendar, Contacts, Tasks, and Google Drive. The project consists of a single Python module (`google_workspace_tools.py`) following Open-WebUI patterns.

**Working Features:**
- ✅ **Gmail**: Full email management (read, search, create drafts, reply, **attachment handling**)
- ✅ **Calendar**: Complete calendar integration (events, scheduling, timezone-aware)
- ✅ **Contacts**: Google People API integration (search, lookup, details, create)
- ✅ **Tasks**: Google Tasks API integration (lists, tasks, subtasks, due dates)
- ✅ **Attachments**: Download, extract, and manage email attachments with size limits
- ✅ **Google Drive**: Complete file management with smart email-to-Drive workflows **[ALL 10 FUNCTIONS TESTED ✅]**

**Completed Development Phases:**
- ✅ **Phase 1**: Google Contacts (People API) integration - COMPLETE & TESTED
- ✅ **Phase 2**: Google Tasks API for life organization - COMPLETE & TESTED
- ✅ **Attachment System**: Complete email attachment management - COMPLETE & TESTED
- ✅ **Phase 3**: Google Drive integration with smart organization - **COMPLETE & PRODUCTION-TESTED**

**Future Development:**
- 🚧 **Phase 4 (Planned)**: Google Docs/Sheets/Slides integration
- 🚧 **Phase 5 (Planned)**: Advanced features & multi-user support

## 📋 Development Roadmap

### ✅ Phase 1: Google Contacts Integration (COMPLETED)
**Goal**: Enhanced Gmail functionality with contact management
- **API**: Google People API with read-mostly approach
- **Functions**: `search_contacts()`, `lookup_contact_by_email()`, `get_contact_details()`, `create_contact()`
- **Status**: Full integration complete, all functions working

### ✅ Phase 2: Life Organization Tools (COMPLETED)
**Goal**: Productivity and task management  
- **Google Tasks API**: Complete todo management, calendar integration, subtasks
- **Functions**: Task lists, task creation/updating, smart list selection, due dates
- **Status**: Full Google Tasks integration complete

### ✅ Attachment System (COMPLETED)
**Goal**: Complete email attachment management
- **Gmail API**: Attachment detection, download, extraction with size management
- **Functions**: `list_email_attachments()`, `download_email_attachment()`, `extract_all_attachments()`
- **Integration**: Attachment indicators in all email functions (`get_recent_emails`, `search_emails`, `get_email_content`)
- **Status**: Full attachment functionality integrated and working

### ✅ Phase 3: Google Drive Integration (COMPLETED)
**Goal**: Complete Google Drive file management and smart organization
- **Google Drive API**: Full file operations (search, list, upload, download, folder management)
- **Functions**: All 10 Drive functions implemented and production-tested
  - `search_drive()` - Advanced file searching with Drive query syntax
  - `list_drive_folder()` - Browse folder contents with organized display
  - `get_drive_file_details()` - Comprehensive file metadata
  - `download_drive_file()` - Download files with Google Workspace export
  - `upload_file_to_drive()` - Upload files with resumable transfers
  - `create_drive_folder()` - Create folders with hierarchical organization
  - `get_drive_folders()` - List folder structures
  - `upload_attachments_to_drive()` - Bulk email attachment uploads with smart organization
  - `upload_attachment_to_drive()` - Individual attachment uploads
  - `get_drive_storage_info()` - Storage quota monitoring
- **Smart Organization**: Email-organized, date-organized, type-organized, and hybrid strategies
- **Status**: **COMPLETE & PRODUCTION-TESTED** - All 10 functions verified working

### 🚧 Phase 4: Advanced Features (PLANNED)
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
3. **Attachment Management**: Download and extract email attachments with size limits
4. **Extensible Design**: Prepared for Calendar, Drive, and Tasks integration
5. **Error Handling**: Comprehensive error handling with user-friendly messages
6. **Token Management**: Automatic token refresh and secure storage

### Data Storage

- Configuration and tokens stored in `/app/backend/data/google_tools/`
- Credentials saved as `credentials.json`
- OAuth tokens saved as `token.json`
- **Email attachments** saved in `/app/backend/data/google_tools/attachments/[email_id]/`

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
- **Attachment settings** (size limits, storage directory)
- Debug settings

## Gmail Attachment System

### Core Attachment Functions
- **`list_email_attachments(email_id)`**: Show detailed metadata for all attachments in an email
  - Returns filename, size, MIME type, and attachment IDs
  - Includes usage hints for downloading specific attachments
- **`download_email_attachment(email_id, attachment_id, filename=None)`**: Download specific attachment
  - Supports both attachment IDs and attachment indexes
  - Optional custom filename for saving
  - Size limit enforcement with clear error messages
- **`extract_all_attachments(email_id)`**: Download all attachments from an email
  - Batch processing with detailed success/failure reporting
  - Automatic skipping of oversized files
  - Total size and individual file reporting

### Enhanced Email Functions (Attachment Integration)
- **`get_recent_emails()`**: Now shows attachment indicators like "📎 3 files (2.5MB)"
  - Optional `show_attachments=True` parameter for performance control
  - Smart detection only when needed
- **`search_emails()`**: Same attachment indicators plus search guidance
  - Includes tip about using `has:attachment` search query
  - Performance optimized attachment detection
- **`get_email_content()`**: Always shows attachment summary section
  - Lists all attachments with sizes and types
  - Provides direct action hints for downloading

### Attachment Processing
- **Dual API Support**: Handles both inline attachments and large separate attachments
- **Smart Detection**: Uses Content-Disposition headers and filename analysis
- **Size Management**: Configurable limits (default 10MB) with clear warnings
- **Security**: Filename sanitization and organized storage structure
- **Error Handling**: Graceful fallback when attachment detection fails

### Storage Organization
```
/app/backend/data/google_tools/attachments/
├── [email_id_1]/
│   ├── document.pdf
│   └── image.jpg
├── [email_id_2]/
│   └── spreadsheet.xlsx
```

### Configuration Settings
- `max_attachment_size_mb`: Maximum file size limit (default: 10MB)
- `attachment_storage_dir`: Storage directory name (default: "attachments")

### Performance Features
- **Conditional Processing**: Attachment detection only when `show_attachments=True`
- **Format Optimization**: Uses `metadata` format when attachments not needed
- **Caching**: Single-request attachment detection during processing
- **Graceful Degradation**: Email listings work even if attachment detection fails

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

### Current Status
- **Active branch**: `main` 
- **Status**: **Complete 5-service integration ready for production use**
- **Recent completion**: Google Drive integration with full functionality (Phase 3)
- **Production testing**: All 10 Drive functions verified working
- **Next focus**: Planning advanced features (Phase 4)