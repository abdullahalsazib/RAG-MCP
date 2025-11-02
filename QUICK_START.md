# 🚀 Quick Start Guide - Dynamic MCP Servers

## TL;DR

You can now pass MCP server URLs as an **array** in 4 different ways!

```python
# Method 1: Direct in code
mcp_servers = [
    {"name": "Math", "url": "https://mcp-test-kset.onrender.com/math/mcp"},
    {"name": "Jack", "url": "https://mcp-test-kset.onrender.com/jack/mcp"},
]
```

---

## 📁 Files Overview

| File | Purpose | Best For |
|------|---------|----------|
| `ai_mcp.py` | Original - servers hardcoded | Simple, single-purpose agents |
| `ai_mcp_dynamic.py` | Dynamic - load from multiple sources | Production, testing, flexibility |
| `mcp_servers.json` | Server configuration file | Easy editing, version control |
| `MCP_USAGE.md` | Complete documentation | Learning all features |

---

## 🎯 Common Use Cases

### 1. Quick Test (Use `ai_mcp.py`)
```bash
uv run python ai_mcp.py
```

### 2. Production Deployment (Use `ai_mcp_dynamic.py` + JSON)

Edit `mcp_servers.json`:
```json
[
  {"name": "Math", "url": "https://mcp-test-kset.onrender.com/math/mcp"},
  {"name": "Jack", "url": "https://mcp-test-kset.onrender.com/jack/mcp"}
]
```

Run:
```bash
uv run python ai_mcp_dynamic.py
```

### 3. Test New Server Without Changing Code
```bash
uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"NewServer","url":"https://new-server.com/mcp"}' \
  --query "Test this new server"
```

### 4. Environment-Based Configuration (Dev/Prod)

**.env.dev:**
```env
MCP_SERVERS=[{"name":"DevMath","url":"https://dev-math.com/mcp"}]
```

**.env.prod:**
```env
MCP_SERVERS=[{"name":"ProdMath","url":"https://prod-math.com/mcp"}]
```

Run:
```bash
# Development
cp .env.dev .env
uv run python ai_mcp_dynamic.py

# Production
cp .env.prod .env
uv run python ai_mcp_dynamic.py
```

---

## ⚡ Quick Commands

```bash
# Default run (uses mcp_servers.json)
uv run python ai_mcp_dynamic.py

# Custom query
uv run python ai_mcp_dynamic.py --query "Add 5 and 10"

# Add server dynamically
uv run python ai_mcp_dynamic.py --add-server '{"name":"Test","url":"https://test.com/mcp"}'

# Multiple servers
uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"Server1","url":"https://s1.com/mcp"}' \
  --add-server '{"name":"Server2","url":"https://s2.com/mcp"}'
```

---

## 🔑 Adding Authentication

```json
{
  "name": "SecureServer",
  "url": "https://secure-server.com/mcp",
  "headers": {
    "X-Api-Key": "your_key_here",
    "Authorization": "Bearer token123"
  }
}
```

---

## 📊 Current Setup

### Your MCP Servers
1. **Math** (`/math/mcp`) - 4 tools
   - addNumber, addSub, addMul, addDiv

2. **Jack** (`/jack/mcp`) - 1 tool
   - showHello

### Example Queries
```bash
# Math operations
uv run python ai_mcp_dynamic.py --query "Add 100 and 50"
uv run python ai_mcp_dynamic.py --query "Multiply 12 by 8"
uv run python ai_mcp_dynamic.py --query "Divide 100 by 4"

# Greeting
uv run python ai_mcp_dynamic.py --query "Say hello to Alice"

# Combined
uv run python ai_mcp_dynamic.py --query "Add 5 and 3, then say hello to Jack"

# With DosiBlog RAG
uv run python ai_mcp_dynamic.py --query "What is DosiBlog?"
```

---

## 🎨 How It Works Internally

```
User Request
    ↓
Load Server Config (JSON/Env/CLI)
    ↓
Connect to Each MCP Server
    ↓
Load All Tools from Servers
    ↓
Create Agent with All Tools
    ↓
Process User Query
    ↓
Agent Calls Appropriate Tools
    ↓
Return Answer
    ↓
Close All Sessions
```

---

## 🔥 Pro Tips

1. **Start with JSON config** - Easiest to manage
2. **Use `--add-server` for testing** - Don't modify files
3. **Environment variables for secrets** - Keep API keys safe
4. **Name servers clearly** - Helps with debugging
5. **Test one server at a time** - Easier to troubleshoot

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Server won't load | Check URL is accessible, try in browser |
| No tools found | Verify server implements MCP protocol |
| Auth errors | Check API key and header format |
| Import error "mcp" | Delete any local `mcp.py` file |
| Connection timeout | Increase timeout or check firewall |

---

## 📝 Next Steps

1. ✅ Test both files work
2. ✅ Modify `mcp_servers.json` for your setup
3. ✅ Try adding a server via command line
4. ✅ Test with your own queries
5. 📚 Read `MCP_USAGE.md` for advanced features

---

## 💬 Example Output

```
============================================================
🚀 Initializing AI Agent with Dynamic MCP Tools
============================================================

Loading tools from Math MCP server...
✓ Loaded 4 tool(s) from Math MCP server
  - addNumber: Add two numbers
  - addSub: Subtract two numbers
  - addMul: Multiply two numbers
  - addDiv: Divide two numbers

Loading tools from Jack MCP server...
✓ Loaded 1 tool(s) from Jack MCP server
  - showHello: Show a hello message

📦 Total tools available: 6
   • Local tools: 1 (DosiBlog RAG)
   • Remote MCP tools: 5

User Query: Add 10 and 5
🤖 Agent calling tool: addNumber
✅ Final Answer: The result is 15.
```

---

**Happy Coding! 🎉**

