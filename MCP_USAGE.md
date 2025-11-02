# Dynamic MCP Server Configuration Guide

This guide shows you how to pass multiple MCP server URLs dynamically to your AI agent.

## 📚 Three Ways to Configure MCP Servers

### Method 1: Direct Array in Code (`ai_mcp.py`)

Edit the `mcp_servers` array directly in the code:

```python
mcp_servers = [
    {
        "name": "Math",
        "url": "https://mcp-test-kset.onrender.com/math/mcp",
    },
    {
        "name": "Jack",
        "url": "https://mcp-test-kset.onrender.com/jack/mcp",
    },
    {
        "name": "Finance",
        "url": "https://mcp-finance-agent.xxx.us.langgraph.app/mcp",
        "headers": {"X-Api-Key": "lsv2_pt_your_api_key"}
    },
]
```

**Run:**
```bash
uv run python ai_mcp.py
```

---

### Method 2: JSON Config File (`ai_mcp_dynamic.py`)

Create or edit `mcp_servers.json`:

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
    "name": "Finance",
    "url": "https://mcp-finance-agent.xxx.us.langgraph.app/mcp",
    "headers": {
      "X-Api-Key": "lsv2_pt_your_api_key"
    }
  }
]
```

**Run:**
```bash
uv run python ai_mcp_dynamic.py
```

---

### Method 3: Environment Variable

Set the `MCP_SERVERS` environment variable:

**Linux/Mac:**
```bash
export MCP_SERVERS='[{"name":"Math","url":"https://mcp-test-kset.onrender.com/math/mcp"},{"name":"Jack","url":"https://mcp-test-kset.onrender.com/jack/mcp"}]'
uv run python ai_mcp_dynamic.py
```

**Windows (PowerShell):**
```powershell
$env:MCP_SERVERS='[{"name":"Math","url":"https://mcp-test-kset.onrender.com/math/mcp"}]'
uv run python ai_mcp_dynamic.py
```

**Or add to `.env` file:**
```env
MCP_SERVERS=[{"name":"Math","url":"https://mcp-test-kset.onrender.com/math/mcp"},{"name":"Jack","url":"https://mcp-test-kset.onrender.com/jack/mcp"}]
```

---

### Method 4: Command Line Arguments

Add servers dynamically via command line:

```bash
# Add a single server
uv run python ai_mcp_dynamic.py --add-server '{"name":"NewServer","url":"https://example.com/mcp"}'

# Add multiple servers
uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"Server1","url":"https://example1.com/mcp"}' \
  --add-server '{"name":"Server2","url":"https://example2.com/mcp"}'

# Add server with authentication
uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"Finance","url":"https://finance.com/mcp","headers":{"X-Api-Key":"your_key"}}'

# Custom query
uv run python ai_mcp_dynamic.py --query "Add 5 and 10, then say hello to Alice"
```

---

## 🔧 Server Configuration Format

Each server configuration requires:

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `name` | ✅ Yes | Display name for the server | `"Math"` |
| `url` | ✅ Yes | MCP endpoint URL | `"https://example.com/mcp"` |
| `headers` | ❌ No | HTTP headers (for authentication) | `{"X-Api-Key": "key123"}` |

---

## 📝 Complete Examples

### Example 1: Basic Math and Greeting Servers

```python
mcp_servers = [
    {"name": "Math", "url": "https://mcp-test-kset.onrender.com/math/mcp"},
    {"name": "Jack", "url": "https://mcp-test-kset.onrender.com/jack/mcp"},
]
```

**Tools Available:**
- `addNumber` - Add two numbers
- `addSub` - Subtract two numbers
- `addMul` - Multiply two numbers
- `addDiv` - Divide two numbers
- `showHello` - Show a hello message

---

### Example 2: With Authentication

```python
mcp_servers = [
    {
        "name": "Math",
        "url": "https://mcp-test-kset.onrender.com/math/mcp"
    },
    {
        "name": "Finance",
        "url": "https://mcp-finance-agent.xxx.us.langgraph.app/mcp",
        "headers": {
            "X-Api-Key": "lsv2_pt_your_api_key",
            "Authorization": "Bearer token123"
        }
    }
]
```

---

### Example 3: Multiple Servers from Different Sources

```bash
# Servers from config file + environment + command line
export MCP_SERVERS='[{"name":"EnvServer","url":"https://env.com/mcp"}]'

uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"CLI Server","url":"https://cli.com/mcp"}'
```

This will load servers from:
1. `mcp_servers.json` (if exists)
2. Environment variable `MCP_SERVERS`
3. Command line `--add-server`

---

## 🚀 Usage Examples

### Run with Default Configuration
```bash
uv run python ai_mcp.py
```

### Run with Custom Query
```bash
uv run python ai_mcp_dynamic.py --query "What is DosiBlog and add 5 plus 3?"
```

### Test a New MCP Server
```bash
uv run python ai_mcp_dynamic.py \
  --add-server '{"name":"TestServer","url":"https://test-server.com/mcp"}' \
  --query "Test query here"
```

---

## 🎯 Benefits of Dynamic Configuration

1. **Easy to Add/Remove Servers** - Just edit the array
2. **Support Multiple Environments** - Use different configs for dev/prod
3. **Command Line Testing** - Quickly test new MCP servers
4. **Secure Authentication** - Store API keys in environment variables
5. **Flexible Deployment** - Configure via env vars in production

---

## 📊 Your Current MCP Servers

### Math MCP Server
- **URL:** https://mcp-test-kset.onrender.com/math/mcp
- **Tools:**
  - `addNumber(a, b)` - Add two numbers
  - `addSub(a, b)` - Subtract two numbers
  - `addMul(a, b)` - Multiply two numbers
  - `addDiv(a, b)` - Divide two numbers

### Jack MCP Server
- **URL:** https://mcp-test-kset.onrender.com/jack/mcp
- **Tools:**
  - `showHello(name)` - Show a hello message

### Local Tools
- `retrieve_dosiblog_context(query)` - DosiBlog RAG tool

---

## 🔍 Troubleshooting

### Server Not Loading
- Check URL is correct and accessible
- Verify network connectivity
- Check authentication headers if required

### Tools Not Available
- Ensure server is running
- Check MCP endpoint responds to `/tools` request
- Verify server implements MCP protocol correctly

### Authentication Errors
- Check API key is correct
- Verify headers format matches server requirements
- Use environment variables for sensitive keys

---

## 💡 Tips

1. **Start Simple** - Begin with one server and add more gradually
2. **Use Config Files** - Easier to manage than hardcoded arrays
3. **Environment Variables** - Best for production deployments
4. **Test Servers** - Use `--add-server` to test before adding to config
5. **Monitor Logs** - Watch for connection and tool loading messages

