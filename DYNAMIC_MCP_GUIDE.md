# 🔧 Dynamic MCP Server Management Guide

## ✨ **NEW FEATURE: Add MCP Servers from Frontend!**

You can now add, view, and delete MCP servers **directly from the web interface** without editing JSON files!

---

## 🎯 How It Works

### 1. **Open MCP Management Panel**

Click the **"🔧 MCP Servers"** button in the header

### 2. **View Current Servers**

See all configured MCP servers with their names and URLs

### 3. **Add New Server**

Fill in the form:
- **Server Name**: e.g., "Weather", "Database", "Custom Tool"
- **Server URL**: Full URL to the MCP endpoint (e.g., `https://your-server.com/mcp`)

Click **"➕ Add Server"**

### 4. **Delete Server**

Click the **"🗑️ Delete"** button next to any server

---

## 📊 API Endpoints Created

### 1. **GET /api/mcp-servers**
List all configured MCP servers

```bash
curl http://localhost:8000/api/mcp-servers
```

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "servers": [
    {
      "name": "Math",
      "url": "https://mcp-test-kset.onrender.com/math/mcp"
    },
    {
      "name": "Jack",
      "url": "https://mcp-test-kset.onrender.com/jack/mcp"
    }
  ]
}
```

### 2. **POST /api/mcp-servers**
Add a new MCP server

```bash
curl -X POST http://localhost:8000/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weather",
    "url": "https://weather-server.com/mcp"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "MCP server 'Weather' added successfully",
  "server": {
    "name": "Weather",
    "url": "https://weather-server.com/mcp"
  },
  "total_servers": 3
}
```

### 3. **DELETE /api/mcp-servers/{server_name}**
Delete an MCP server

```bash
curl -X DELETE http://localhost:8000/api/mcp-servers/Weather
```

**Response:**
```json
{
  "status": "success",
  "message": "MCP server 'Weather' deleted successfully",
  "remaining_servers": 2
}
```

### 4. **PUT /api/mcp-servers/{server_name}**
Update an existing MCP server

```bash
curl -X PUT http://localhost:8000/api/mcp-servers/Weather \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weather",
    "url": "https://new-weather-server.com/mcp"
  }'
```

---

## 🎨 UI Features

### **MCP Management Panel**
- **Yellow theme** to distinguish from info panel
- **Scrollable** if many servers
- **Real-time updates** after add/delete
- **Success notifications** in chat area

### **Add Server Form**
- **Name field**: Human-readable identifier
- **URL field**: Full MCP endpoint URL
- **Validation**: Checks for duplicates
- **Auto-clear**: Form resets after successful add

### **Server List**
- **Server cards** with name and URL
- **Delete button** for each server
- **Empty state** when no servers configured
- **Loading state** while fetching

---

## 🔄 How Agent Uses New Servers

1. **You add a server** via the UI
2. **Server saved** to `mcp_servers.json`
3. **Next chat request** loads updated servers
4. **Agent connects** to all configured servers
5. **Tools available** immediately for use

**Note:** The agent loads MCP servers at the start of each chat request, so new servers are available immediately!

---

## 💡 Example Workflow

### Scenario: Adding a Weather MCP Server

1. **Click "🔧 MCP Servers"** button
2. **Fill in form:**
   - Name: `Weather`
   - URL: `https://weather-api.com/mcp`
3. **Click "➕ Add Server"**
4. **See success message** in chat
5. **Close panel** and ask: "What's the weather in New York?"
6. **Agent uses Weather tools** automatically!

---

## 🛡️ Validation & Security

### Validation Rules
- ✅ **Name required**: Must provide server name
- ✅ **URL required**: Must provide valid URL
- ✅ **No duplicates**: Name and URL must be unique
- ✅ **URL format**: Must be valid HTTP/HTTPS URL

### Error Handling
- Duplicate name/URL → Shows error alert
- Invalid URL → Browser validation
- Network error → Shows error message
- Server error → Shows error alert

---

## 📝 JSON File Format

When you add servers via UI, they're saved to `mcp_servers.json`:

```json
[
  {
    "name": "Math",
    "url": "https://mcp-test-kset.onrender.com/math/mcp"
  },
  {
    "name": "Jack",
    "url": "https://mcp-test-kset.onrender.com/jack/mcp"
  },
  {
    "name": "Weather",
    "url": "https://weather-api.com/mcp"
  }
]
```

You can still edit this file manually if preferred!

---

## 🧪 Testing Dynamic MCP Addition

### Test via UI:
1. Start server: `./start_server.sh`
2. Open: http://localhost:8000
3. Click "🔧 MCP Servers"
4. Add a test server:
   - Name: `Test`
   - URL: `https://example.com/mcp`
5. Verify it appears in list
6. Delete it
7. Verify it's removed

### Test via API:
```bash
# Add server
curl -X POST http://localhost:8000/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","url":"https://example.com/mcp"}'

# List servers
curl http://localhost:8000/api/mcp-servers

# Delete server
curl -X DELETE http://localhost:8000/api/mcp-servers/Test
```

---

## 🎯 Use Cases

### 1. **Add Custom Business Tools**
```
Name: CRM
URL: https://your-company.com/crm-mcp
→ Agent can query customer data
```

### 2. **Add External APIs**
```
Name: Database
URL: https://db-api.com/mcp
→ Agent can run database queries
```

### 3. **Add Third-Party Services**
```
Name: EmailService
URL: https://email-provider.com/mcp
→ Agent can send emails
```

### 4. **Testing New MCP Servers**
```
Name: TestServer
URL: http://localhost:3000/mcp
→ Test local MCP development
```

---

## 🚀 Best Practices

### ✅ **DO:**
- Use descriptive server names
- Verify URL is accessible before adding
- Test new servers with simple queries
- Keep server list organized
- Delete unused servers

### ❌ **DON'T:**
- Add duplicate servers
- Use invalid URLs
- Add servers without testing them
- Keep broken/offline servers
- Add too many similar servers

---

## 🔧 Technical Details

### Backend Implementation
- **FastAPI endpoints** handle CRUD operations
- **File-based storage** in `mcp_servers.json`
- **Validation** prevents duplicates
- **Error handling** for all edge cases

### Frontend Implementation
- **Vanilla JavaScript** (no frameworks)
- **Fetch API** for HTTP requests
- **Dynamic rendering** of server list
- **Real-time updates** after changes
- **Success notifications** in chat

### Agent Integration
- Loads servers at **each request start**
- Connects to **all configured servers**
- Makes tools **immediately available**
- Handles **connection failures** gracefully

---

## 📊 Summary

### What You Can Do:
✅ Add MCP servers from UI  
✅ View all configured servers  
✅ Delete servers with one click  
✅ See real-time updates  
✅ Get instant tool availability  
✅ Use API endpoints programmatically  

### Benefits:
🎯 No need to edit JSON files manually  
🎯 Instant updates without restart  
🎯 User-friendly interface  
🎯 Validation prevents errors  
🎯 Success notifications  
🎯 Full API access  

---

**You can now dynamically manage MCP servers and use them immediately in your agent conversations!** 🎉

---

*Guide Version: 1.0*  
*Last Updated: November 2, 2025*

