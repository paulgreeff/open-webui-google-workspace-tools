# 🐛 Google Workspace Tools - Debugging Guide

## Comprehensive Debugging Added for Tasks Functions

I've added extensive debugging logging to all the key tasks functions to help you troubleshoot issues. Here's what's now available:

### 🔧 How to Enable Debug Mode

1. In Open-WebUI, go to **Tools → Google Workspace Tools → Settings**
2. Turn on **`debug_mode`** 
3. Save settings

All debug messages will now appear in your Open-WebUI logs and console.

---

## 📋 Functions with Comprehensive Debugging

### **`get_task_lists()`**
**What it logs:**
- 🚀 Function entry  
- ✅ Authentication success/failure
- 📋 Number of task lists returned from API
- 📊 List details (in debug mode: names and IDs of each list)
- ⚠️ When no task lists found

### **`get_tasks(list_id)`**  
**What it logs:**
- 🚀 Function entry with all parameters
- 🔍 ID validation process
- 🔄 ID format conversion (when needed)
- 📋 Task list validation 
- 📊 API request parameters  
- 🔍 Number of tasks returned
- 📝 First 3 tasks details (in debug mode)

### **`create_task_with_smart_list_selection()`**
**What it logs:**
- 🚀 Function entry with all parameters
- ✅ Authentication status
- 📋 All available task lists for selection
- 🎯 Smart matching process (exact → partial → default → fallback)
- ✅ Which list was selected and why
- ➡️ Delegation to create_task()

### **`create_task()`**
**What it logs:**
- 🚀 Function entry with all parameters
- ✅ Authentication status  
- 🔍 ID validation and conversion
- 📋 Task list validation
- 🛠️ Task data structure building
- 📝 Notes truncation (first 50 chars)
- 👨‍👩‍👧‍👦 Parent task assignment
- 📅 Due date parsing (success/failure)
- 📦 Final task data sent to API (in debug mode)
- 🚀 API call execution
- ✅ Task creation success with Task ID
- ❌ Detailed error information

### **`_validate_task_list_id()`**
**What it logs:**
- 🔍 Function entry with provided ID
- 📏 ID length analysis
- ❌ Format validation errors
- 🔄 Email-prefixed ID conversion
- 🔓 Base64 decoding attempts

---

## 🕵️ Example Debug Output

When you create a task, you'll see logs like this:

```
🚀 create_task_with_smart_list_selection() called with title='Buy groceries', list_hint='personal', notes='milk, bread, eggs', due_date='tomorrow', parent_id=None
✅ Tasks service authenticated  
🎯 Starting smart list selection for task: Buy groceries
📋 Fetching all task lists for smart selection
📊 Found 3 task lists for selection
  List 1: 'My Tasks' (ID: MTEzOTQ1NjgyMDc4NzM4NDcyODQ)
  List 2: 'Personal Tasks' (ID: MTIzNDU2Nzg5MDEyMzQ1Njc4)  
  List 3: 'Work Tasks' (ID: OTg3NjU0MzIxMDk4NzY1NDM)
🔍 Smart matching with hint: 'personal'
🎯 Trying exact name match...
🔍 Trying partial name match...
✅ Partial match found: 'Personal Tasks'
🎯 Final selection: 'Personal Tasks' (ID: MTIzNDU2Nzg5MDEyMzQ1Njc4)
➡️ Delegating to create_task() with list_id=MTIzNDU2Nzg5MDEyMzQ1Njc4

🚀 create_task() called with list_id='MTIzNDU2Nzg5MDEyMzQ1Njc4', title='Buy groceries', notes='milk, bread, eggs', due_date='tomorrow', parent_id=None
✅ Tasks service authenticated
🔍 Validating task list ID: 'MTIzNDU2Nzg5MDEyMzQ1Njc4'
📏 ID length: 32 characters
📋 Fetching task list info for validation
✅ Task list found: 'Personal Tasks'
🛠️ Building task data structure
📝 Added notes: 'milk, bread, eggs'
📅 Parsing due date: 'tomorrow'
✅ Due date parsed successfully: 2024-08-13T00:00:00.000Z
📦 Final task data: {'title': 'Buy groceries', 'notes': 'milk, bread, eggs', 'due': '2024-08-13T00:00:00.000Z'}
🚀 Calling Google Tasks API to create task in list MTIzNDU2Nzg5MDEyMzQ1Njc4
✅ Task created successfully! Task ID: abc123xyz789
```

---

## 🚨 Common Issues the Debugging Will Reveal

### **Authentication Problems**
- Look for: `❌ Authentication failed: [details]`
- Solution: Re-authenticate in Open-WebUI

### **Task List ID Issues**  
- Look for: `❌ ID validation failed: [details]`
- Look for: `🔄 Converted ID from 'X' to 'Y'`
- Solution: Use correct ID from `get_task_lists()`

### **API Permission Problems**
- Look for: `❌ Failed to get task list info: [error]`
- Look for: `insufficientPermissions` in error messages
- Solution: Check Google Tasks API permissions

### **Date Parsing Issues**
- Look for: `❌ Date parsing failed for 'X': [error]`
- Look for: `⚠️ Due date parsing returned None`
- Solution: Use formats like 'tomorrow', '2024-01-15', 'next Monday'

### **Smart List Selection Issues**
- Look for: `⚠️ No match found for hint: 'X'`
- Look for: `📌 Using first available list: 'Y'`
- Solution: Check available task lists and hint accuracy

---

## 🔍 How to Read the Debug Logs

**Emojis indicate log types:**
- 🚀 = Function entry
- ✅ = Success  
- ❌ = Error/failure
- 🔍 = Processing/searching
- 📋 = Data retrieval 
- 📊 = Statistics/counts
- 🛠️ = Data building
- 🔄 = Data conversion
- ➡️ = Function delegation
- 💡 = Information/tip
- ⚠️ = Warning

**Information flow:**
1. Function entry (🚀)
2. Authentication (✅/❌)
3. Validation (🔍)
4. Data processing (🛠️/📋)
5. API calls (🚀)
6. Results (✅/❌)

---

## 🎯 Next Steps

1. **Enable debug mode** in your Google Workspace Tools settings
2. **Try creating a task** and check the logs
3. **Look for the specific error patterns** mentioned above
4. **Share the relevant debug logs** if you need further help

The debugging will show you exactly where the process is failing and provide specific error details to help resolve the issue!