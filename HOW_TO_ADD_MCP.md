# 🚀 How to Add MCP Servers from Frontend

## Quick Start Guide

### Step 1: Start the Server
```bash
./start_server.sh
```

### Step 2: Open Your Browser
```
http://localhost:8000
```

### Step 3: Click "🔧 MCP Servers" Button
Look for the button in the header (between mode selector and Clear button)

### Step 4: Fill in the Form

```
┌─────────────────────────────────────────────┐
│  🔧 MCP Server Management            ✕      │
├─────────────────────────────────────────────┤
│                                             │
│  Add New MCP Server                         │
│  ┌───────────────────────────────────────┐ │
│  │ Server Name:                          │ │
│  │ [Weather API___________________]      │ │
│  │                                       │ │
│  │ Server URL:                           │ │
│  │ [https://weather-api.com/mcp__]       │ │
│  │                                       │ │
│  │         [➕ Add Server]                │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Configured Servers (2)                     │
│  ┌───────────────────────────────────────┐ │
│  │ 🔧 Math                               │ │
│  │ https://mcp-test-kset.onrender...     │ │
│  │                      [🗑️ Delete]      │ │
│  ├───────────────────────────────────────┤ │
│  │ 🔧 Jack                               │ │
│  │ https://mcp-test-kset.onrender...     │ │
│  │                      [🗑️ Delete]      │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Step 5: Click "➕ Add Server"

You'll see a success message in the chat:

```
┌─────────────────────────────────────────┐
│  ✅ MCP Server Added!                   │
│  Server "Weather API" has been added    │
│  successfully. The agent can now use    │
│  its tools!                             │
└─────────────────────────────────────────┘
```

### Step 6: Start Using the New Server!

Close the panel and ask questions that use the new tools:

```
You: What's the weather in Paris?

AI: 🔧 Using tool: getWeather
    
    The current weather in Paris is...
```

---

## 📝 Important Notes

### ✅ What Happens When You Add a Server

1. **Frontend** sends request to `/api/mcp-servers`
2. **Backend** validates the data
3. **Backend** saves to `mcp_servers.json`
4. **Frontend** shows success notification
5. **Next chat** loads the new server automatically
6. **Agent** connects and uses the new tools

### ⚡ Instant Availability

**No restart needed!** The agent loads MCP servers at the start of each chat request, so your new server is available immediately for the next question.

### 🛡️ Validation

The system prevents:
- ❌ Duplicate server names
- ❌ Duplicate server URLs
- ❌ Empty names or URLs
- ❌ Invalid URL formats

### 🔧 MCP Server Requirements

Your MCP server must:
1. Be accessible via HTTP/HTTPS
2. Implement the MCP protocol
3. Respond to MCP handshake requests
4. Provide tool definitions

---

## 🎯 Example Use Cases

### 1. Add a Weather Service
```
Name: Weather
URL: https://weather-api.com/mcp

→ Agent can now get weather data
```

### 2. Add a Database Service
```
Name: Database
URL: https://your-db-api.com/mcp

→ Agent can now query your database
```

### 3. Add a Custom Tool
```
Name: MyCustomTool
URL: https://my-server.com/mcp

→ Agent can use your custom functionality
```

### 4. Test Local Development
```
Name: LocalTest
URL: http://localhost:3000/mcp

→ Test your MCP server in development
```

---

## 🧪 Testing Your New Server

After adding a server, test it with a simple query:

1. **Add the server** via UI
2. **Close the panel**
3. **Ask a question** that would use the new tools
4. **Watch for tool indicators**: 🔧 Using tool: toolName
5. **Verify the response** uses the new tools

---

## 🔄 Managing Servers

### View All Servers
Click "🔧 MCP Servers" to see all configured servers

### Delete a Server
1. Open MCP panel
2. Find the server in the list
3. Click "🗑️ Delete"
4. Confirm deletion

### Edit a Server
Currently:
1. Delete the old server
2. Add it again with new details

(Update endpoint available via API: `PUT /api/mcp-servers/{name}`)

---

## 📊 API Reference

### List Servers
```bash
GET /api/mcp-servers
```

### Add Server
```bash
POST /api/mcp-servers
Content-Type: application/json

{
  "name": "ServerName",
  "url": "https://server.com/mcp"
}
```

### Delete Server
```bash
DELETE /api/mcp-servers/{serverName}
```

### Update Server
```bash
PUT /api/mcp-servers/{serverName}
Content-Type: application/json

{
  "name": "NewName",
  "url": "https://new-url.com/mcp"
}
```

---

## 💡 Tips

### ✅ Best Practices
- Use descriptive server names
- Test the URL before adding
- Remove unused servers
- Document your MCP servers
- Check server is online before adding

### ⚠️ Common Issues
- **Server URL not responding**: Check server is online
- **Duplicate error**: Server already exists
- **Agent not using tools**: Check server implements MCP correctly
- **Connection timeout**: Check server URL is accessible

---

## 🎉 Success!

You now know how to:
- ✅ Add MCP servers from the UI
- ✅ View configured servers
- ✅ Delete servers
- ✅ Use the new servers immediately
- ✅ Troubleshoot common issues

**Just click "🔧 MCP Servers" and start adding!** 🚀

---

*Last Updated: November 2, 2025*

