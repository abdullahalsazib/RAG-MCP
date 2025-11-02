# Project Architecture - AI MCP Dynamic Agent

## 📁 Project Structure

```
mcp-server/
├── src/                          # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration & environment
│   ├── history.py               # Conversation history management
│   ├── rag.py                   # RAG system with FAISS
│   ├── tools.py                 # Tool definitions
│   ├── mcp_client.py            # MCP client manager
│   └── agent.py                 # Agent creation & execution
│
├── ai_mcp_dynamic.py            # Main entry point (CLI)
├── example_usage.py             # Usage examples
├── run.sh                       # Convenience script
│
├── mcp_servers.json             # MCP server configuration
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables

OLD FILES (backup):
├── ai_mcp_dynamic_old.py        # Original monolithic version
```

---

## 🏗️ Module Responsibilities

### 1. `src/config.py` - Configuration Management
**Purpose**: Centralized configuration and environment variable management

**Key Classes**:
- `Config`: Application-wide settings

**Responsibilities**:
- Load environment variables (.env file)
- Parse MCP server configurations
- Provide configuration constants

**Key Methods**:
```python
Config.load_mcp_servers(additional_servers) → list[dict]
# Loads MCP servers from:
# 1. Environment variable (MCP_SERVERS)
# 2. Config file (mcp_servers.json)
# 3. Additional servers passed as arguments
```

---

### 2. `src/history.py` - Conversation History
**Purpose**: Manages conversation history across multiple sessions

**Key Classes**:
- `ConversationHistoryManager`: Multi-session history management

**Responsibilities**:
- Store messages per session
- Retrieve conversation history
- Clear sessions
- Display session information

**Key Methods**:
```python
history_manager.get_session_history(session_id) → ChatMessageHistory
history_manager.get_session_messages(session_id) → List[BaseMessage]
history_manager.clear_session(session_id) → None
history_manager.show_session_info(session_id) → None
```

**Global Instance**:
```python
history_manager = ConversationHistoryManager()
```

---

### 3. `src/rag.py` - RAG System
**Purpose**: Retrieval Augmented Generation with FAISS vectorstore

**Key Classes**:
- `EnhancedRAGSystem`: RAG with history-aware retrieval

**Responsibilities**:
- Initialize FAISS vectorstore with DosiBlog knowledge
- Retrieve relevant context for queries
- Handle history-aware queries using LangChain

**Knowledge Base**:
- DosiBlog project information
- Creator details (Abdullah Al Sazib)
- Technology stack (Node.js, Express, MongoDB)
- Features and timeline

**Key Methods**:
```python
rag_system.retrieve_context(query) → str
# Simple context retrieval

rag_system.query_with_history(query, session_id, llm) → str
# History-aware RAG query
```

**Global Instance**:
```python
rag_system = EnhancedRAGSystem()
```

---

### 4. `src/tools.py` - Tool Definitions
**Purpose**: Define tools available to the agent

**Tools**:
- `retrieve_dosiblog_context`: RAG tool for DosiBlog queries

**Example**:
```python
@tool("retrieve_dosiblog_context")
def retrieve_dosiblog_context(query: str) -> str:
    """Retrieves relevant context about DosiBlog projects"""
    return rag_system.retrieve_context(query)
```

---

### 5. `src/mcp_client.py` - MCP Client Management
**Purpose**: Manage connections to external MCP servers

**Key Classes**:
- `MCPClientManager`: Context manager for MCP sessions

**Responsibilities**:
- Connect to MCP servers (HTTP/HTTPS)
- Load tools from MCP servers
- Manage session lifecycle
- Handle errors gracefully

**Usage**:
```python
async with MCPClientManager(mcp_servers) as mcp_tools:
    # mcp_tools contains all loaded tools
    ...
```

**Features**:
- Async context manager
- Auto cleanup on exit
- Support for custom headers
- Error handling per server

---

### 6. `src/agent.py` - Agent Logic
**Purpose**: Agent creation and query execution

**Key Functions**:
- `run_agent_query()`: Execute query with agent + history
- `run_rag_query()`: Execute RAG-only query
- `run_agent_mode()`: Full agent mode with MCP tools
- `run_rag_mode()`: RAG-only mode

**Agent Flow**:
```
1. Load conversation history
2. Build messages with history context
3. Stream agent responses
4. Handle tool calls
5. Save response to history
```

---

### 7. `ai_mcp_dynamic.py` - Main Entry Point
**Purpose**: CLI interface and orchestration

**Responsibilities**:
- Parse command-line arguments
- Route to appropriate mode (agent/rag)
- Handle history commands
- Coordinate all modules

**CLI Arguments**:
```bash
--query, -q          Query to send
--mode, -m          Mode: agent/rag
--session-id        Session identifier
--show-history      Display history
--clear-history     Clear history
--add-server, -s    Add MCP server (JSON)
```

---

## 🔄 Data Flow

### Agent Mode Flow:
```
User Query
    ↓
CLI Parser (ai_mcp_dynamic.py)
    ↓
Config.load_mcp_servers() → Load MCP servers
    ↓
MCPClientManager → Connect to MCP servers
    ↓
Combine tools (local RAG + MCP tools)
    ↓
create_agent() → Create LangChain agent
    ↓
run_agent_query() → Execute with history
    ↓
Agent decides which tools to call
    ↓
Tools execute → Return results
    ↓
Agent formulates answer
    ↓
Save to history_manager
    ↓
Return answer to user
```

### RAG Mode Flow:
```
User Query
    ↓
CLI Parser
    ↓
run_rag_query()
    ↓
Get conversation history
    ↓
rag_system.query_with_history()
    ↓
Create history-aware retriever
    ↓
Retrieve relevant docs from FAISS
    ↓
Generate answer with context
    ↓
Save to history
    ↓
Return answer
```

---

## 🎯 Design Patterns

### 1. **Singleton Pattern**
- `history_manager`: Global instance for all sessions
- `rag_system`: Global RAG system instance

### 2. **Context Manager Pattern**
- `MCPClientManager`: Manages MCP session lifecycle

### 3. **Factory Pattern**
- `create_agent()`: Creates configured agent instances

### 4. **Strategy Pattern**
- Agent mode vs RAG mode selection

---

## 📊 Module Dependencies

```
ai_mcp_dynamic.py
    ↓
    ├── src.config (Config)
    ├── src.history (history_manager)
    └── src.agent
            ↓
            ├── src.config (Config)
            ├── src.history (history_manager)
            ├── src.rag (rag_system)
            ├── src.tools (retrieve_dosiblog_context)
            └── src.mcp_client (MCPClientManager)
                    ↓
                    └── MCP + LangChain libraries
```

---

## 🔧 Configuration Files

### `mcp_servers.json`
```json
[
  {
    "name": "ServerName",
    "url": "https://server.com/mcp",
    "headers": {  // Optional
      "Authorization": "Bearer token"
    }
  }
]
```

### `.env`
```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
```

---

## 📚 Technology Stack

**Core**:
- Python 3.13+
- LangChain 1.0.3
- LangChain Classic 1.0.0
- OpenAI API

**Storage**:
- FAISS (vectorstore)
- In-memory history (ChatMessageHistory)

**MCP**:
- MCP Protocol
- langchain-mcp-adapters
- streamable_http client

---

## ✅ Advantages of Modular Architecture

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Modules can be tested independently
3. **Reusability**: Import and use modules in other projects
4. **Readability**: Clear separation of concerns
5. **Scalability**: Easy to add new features
6. **Debugging**: Isolated issues to specific modules

---

## 🚀 Getting Started

### Basic Usage:
```bash
# RAG mode
python ai_mcp_dynamic.py --mode rag --query "What is DosiBlog?"

# Agent mode with MCP tools
python ai_mcp_dynamic.py --query "What is DosiBlog?"

# With session
python ai_mcp_dynamic.py --query "My name is Jack" --session-id user1
python ai_mcp_dynamic.py --query "What is my name?" --session-id user1
```

### Programmatic Usage:
```python
from ai_mcp_dynamic import main

await main(
    query="What is DosiBlog?",
    session_id="test",
    mode="agent"
)
```

---

*Architecture Version: 2.0 (Modular)*  
*Last Updated: November 2, 2025*

