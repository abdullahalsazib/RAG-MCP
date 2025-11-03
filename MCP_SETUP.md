# MCP Server Setup

## Installation

The MCP servers require the following packages to be installed:

```bash
pip install mcp>=1.20.0 fastmcp>=2.13.0.2 httpx>=0.28.1
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Naming Conflict Resolution

The local `mcp/` folder was renamed to `mcp_servers/` to avoid conflicts with the installed `mcp` package.

## Available MCP Servers

- **math** - Mathematical operations (add, subtract, multiply, divide, calculate, sin, cos, etc.)
- **weather** - Weather API integration (by city or coordinates)
- **web** - Web utilities (search, scrape, crawl using Firecrawl)
- **people** - People information (DosiBridge team members)
- **jack** - Jack Sparrow information tool

## Endpoints

- `GET /api/mcp-servers/available` - List all available local MCP servers
- `GET /api/mcp/{server_name}/info` - Get information about a specific MCP server
- `GET/POST /api/mcp/{server_name}/*` - Access individual MCP server endpoints

## Example Usage

```bash
# List available servers
curl http://localhost:8000/api/mcp-servers/available

# Get math server info
curl http://localhost:8000/api/mcp/math/info

# Access math server directly
curl -X POST http://localhost:8000/api/mcp/math/ \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "add", "arguments": {"a": 2, "b": 3}}}'
```

