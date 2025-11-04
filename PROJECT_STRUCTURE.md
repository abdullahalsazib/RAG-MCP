# Project Structure

This document describes the organized folder structure of the mcp-server project.

## Directory Structure

```
mcp-server/
├── src/                    # Core application source code
│   ├── api.py             # FastAPI application (main entry point)
│   ├── agent.py           # Agent orchestration logic
│   ├── config.py          # Configuration management
│   ├── history.py         # Conversation history management
│   ├── llm_factory.py     # LLM provider factory
│   ├── mcp_client.py      # MCP client manager
│   ├── rag.py             # RAG (Retrieval Augmented Generation) system
│   └── tools.py           # LangChain tool definitions
│
├── mcp_servers/           # Local MCP server implementations
│   ├── __init__.py        # Package initialization
│   ├── registry.py        # MCP server registry
│   ├── math_server.py     # Math operations server
│   ├── weather.py         # Weather API server
│   ├── web.py             # Web utilities server (Firecrawl)
│   ├── people.py          # People information server
│   └── jack.py            # Jack Sparrow info server
│
├── config/                # Configuration files
│   ├── llm_config.json    # LLM provider configuration
│   └── mcp_servers.json   # MCP server endpoints configuration
│
├── examples/              # Example scripts and test files
│   ├── ai_mcp_dynamic.py  # Main CLI interface for agent
│   ├── test_dynamic_mcp.py # Test script for MCP management
│   ├── example_usage.py   # Usage examples
│   └── ai_mcp_dynamic_old.py # Legacy version (for reference)
│
├── scripts/               # Utility scripts (currently empty, reserved for future use)
│
├── start_server.sh        # Start FastAPI server script
├── run.sh                 # Run CLI agent script
├── requirements.txt       # Python dependencies
├── README.md              # Main documentation
└── MCP_SETUP.md          # MCP server setup guide
```

## Key Changes from Previous Structure

1. **Consolidated Source Code**: 
   - Moved `backend/api.py` → `src/api.py` (all source code now in `src/`)
   - Removed empty `backend/` directory

2. **Organized Examples**:
   - Moved all example/test scripts to `examples/` directory
   - Added `__init__.py` to make it a proper Python package

3. **Centralized Configuration**:
   - Moved config files (`llm_config.json`, `mcp_servers.json`) to `config/` directory
   - Updated all path references in code

4. **Clear Separation**:
   - `src/` - Application code
   - `mcp_servers/` - MCP server implementations
   - `config/` - Configuration files
   - `examples/` - Example/test scripts
   - Root - Essential files (README, requirements, scripts)

## Running the Application

### Start the FastAPI Server
```bash
./start_server.sh
# Or directly:
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### Run CLI Agent
```bash
./run.sh --query "Your question here"
# Or directly:
python examples/ai_mcp_dynamic.py --query "Your question here"
```

## Import Paths

All imports should use absolute paths from project root:
- `from src.config import Config`
- `from src.api import app`
- `from mcp_servers.registry import MCP_SERVERS`

## Configuration Files

Configuration files are located in `config/`:
- `config/llm_config.json` - LLM provider settings
- `config/mcp_servers.json` - External MCP server endpoints

The code automatically resolves paths relative to project root using `Config.ROOT_DIR`.

