
# 📁 AI MCP Agent - Complete Project Structure

## Overview
A complete AI agent with RAG, MCP tools, FastAPI backend, and beautiful chat UI.

---

## 📂 Directory Structure

```
mcp-server/
├── backend/                      # FastAPI Backend
│   ├── __init__.py
│   └── api.py                   # Main FastAPI app with streaming
│
├── frontend/                     # Frontend assets (reserved)
│
├── src/                          # Core Agent Modules
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── history.py               # Conversation history
│   ├── rag.py                   # RAG system with FAISS
│   ├── tools.py                 # Tool definitions
│   ├── mcp_client.py            # MCP client manager
│   └── agent.py                 # Agent logic
│
├── static/                       # Static Web Assets
│   ├── css/
│   │   └── style.css            # Beautiful chat UI styles
│   └── js/
│       └── app.js               # Interactive chat client
│
├── templates/                    # HTML Templates
│   └── index.html               # Main chat interface
│
├── tests/                        # Test Scripts
│   ├── test_complex_query.py
│   ├── test_mcp_servers.py
│   └── verify_everything.py
│
├── ai_mcp_dynamic.py            # CLI Entry Point
├── example_usage.py             # Usage examples
├── start_server.sh              # Server startup script ✨ NEW
├── run.sh                       # CLI convenience script
│
├── mcp_servers.json             # MCP server configuration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
│
└── docs/                        # Documentation
    ├── ARCHITECTURE.md
    ├── MCP_SERVERS_GUIDE.md
    ├── PROOF_AND_GUIDE.md
    └── TEST_RESULTS.md
```

---

## 🎯 Components Breakdown

### 1. **Backend (`backend/`)**

#### `api.py` - FastAPI Application
**Purpose**: RESTful API with streaming support

**Endpoints**:
```
GET  /                      → Chat UI (HTML)
GET  /health                → Health check
POST /api/chat              → Non-streaming chat
POST /api/chat/stream       → Streaming chat (SSE) ✨
GET  /api/session/{id}      → Get session info
DELETE /api/session/{id}    → Clear session
GET  /api/sessions          → List all sessions
GET  /api/tools             → Get available tools info
```

**Features**:
- ✅ Server-Sent Events (SSE) for streaming
- ✅ CORS enabled
- ✅ Session management
- ✅ Real-time typing indicators
- ✅ Tool usage tracking

---

### 2. **Core Modules (`src/`)**

#### `config.py` - Configuration
- Environment variables
- MCP server loading (JSON, ENV, CLI)
- Application settings

#### `history.py` - Conversation Memory
- Multi-session history
- Message storage and retrieval
- Session management

#### `rag.py` - RAG System
- FAISS vectorstore
- DosiBlog knowledge base
- History-aware retrieval

#### `tools.py` - Tool Definitions
- RAG tools
- Custom tool wrappers

#### `mcp_client.py` - MCP Integration
- Connect to external MCP servers
- Load remote tools
- Session lifecycle management

#### `agent.py` - Agent Logic
- Agent creation
- Query execution
- Tool coordination
- Streaming support

---

### 3. **Frontend (`static/` + `templates/`)**

#### `templates/index.html` - Chat Interface
**Features**:
- 🎨 Modern, responsive design
- 💬 Real-time chat interface
- 🔄 Mode switching (Agent/RAG)
- ℹ️ Info panel with help
- 📊 Status bar with metrics
- ⚡ Typing indicators

#### `static/css/style.css` - Styling
**Features**:
- Beautiful gradient design
- Smooth animations
- Responsive layout
- Dark/light message bubbles
- Tool usage badges
- Loading indicators

#### `static/js/app.js` - Client Logic
**Features**:
- ✅ Real-time streaming with EventSource
- ✅ Chunk-by-chunk response display
- ✅ Tool usage indicators
- ✅ Session management
- ✅ Mode switching
- ✅ Auto-scroll
- ✅ Message formatting (Markdown-like)

---

## 🚀 How to Run

### Method 1: Start Web Server (Recommended)
```bash
chmod +x start_server.sh
./start_server.sh
```

Then open: **http://localhost:8000**

### Method 2: CLI Mode
```bash
./run.sh --query "Your question" --mode agent
```

### Method 3: Python Script
```python
python example_usage.py
```

---

## 🔌 API Usage Examples

### 1. Non-Streaming Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is DosiBlog?",
    "session_id": "user123",
    "mode": "agent"
  }'
```

**Response**:
```json
{
  "response": "DosiBlog is a web development project...",
  "session_id": "user123",
  "mode": "agent",
  "tools_used": ["retrieve_dosiblog_context"]
}
```

### 2. Streaming Chat (SSE)
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 5 + 3",
    "session_id": "user123",
    "mode": "agent"
  }'
```

**Response** (Server-Sent Events):
```
data: {"chunk": "The ", "done": false}
data: {"chunk": "result ", "done": false}
data: {"chunk": "is ", "done": false}
data: {"chunk": "8", "done": false}
data: {"chunk": "", "done": true, "tools_used": ["addNumber"]}
```

### 3. Get Session History
```bash
curl http://localhost:8000/api/session/user123
```

**Response**:
```json
{
  "session_id": "user123",
  "message_count": 4,
  "messages": [
    {"role": "user", "content": "What is DosiBlog?"},
    {"role": "assistant", "content": "DosiBlog is..."}
  ]
}
```

---

## 🎨 UI Features

### Chat Interface
- **Beautiful Design**: Gradient backgrounds, smooth animations
- **Real-time Streaming**: See responses as they're generated
- **Tool Indicators**: See which tools the agent uses
- **Mode Switching**: Toggle between Agent and RAG modes
- **Session Management**: Clear history, view status
- **Responsive**: Works on desktop and mobile

### User Experience
1. **Type message** → Press Send
2. **Typing indicator** shows AI is thinking
3. **Tool badges** appear as agent uses tools
4. **Response streams** word by word
5. **History maintained** across conversation

---

## 📊 Architecture Flow

### Streaming Chat Flow:
```
User Types Message
    ↓
Frontend (JS) → POST /api/chat/stream
    ↓
FastAPI Backend receives request
    ↓
Create Agent with tools (RAG + MCP)
    ↓
Stream responses via Server-Sent Events
    ↓
Backend yields chunks: data: {"chunk": "...", "done": false}
    ↓
Frontend EventSource receives chunks
    ↓
JavaScript updates UI in real-time
    ↓
Show tool usage badges
    ↓
Display complete response
    ↓
Save to conversation history
```

---

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
```

### MCP Servers (`mcp_servers.json`)
```json
[
  {
    "name": "Math",
    "url": "https://mcp-test-kset.onrender.com/math/mcp"
  },
  {
    "name": "Jack",
    "url": "https://mcp-test-kset.onrender.com/jack/mcp"
  }
]
```

---

## 🧪 Testing

### Test Web Interface
1. Start server: `./start_server.sh`
2. Open: http://localhost:8000
3. Try queries:
   - "What is DosiBlog?"
   - "Calculate 10 + 5"
   - "Say hello to me and tell me about the technologies"

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test","mode":"agent"}'
```

### Test CLI
```bash
python test_complex_query.py
python test_mcp_servers.py
```

---

## 📦 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server with hot reload
- **LangChain 1.0**: Agent orchestration
- **OpenAI GPT-4o**: Language model
- **FAISS**: Vector storage for RAG
- **MCP**: External tool integration

### Frontend
- **Vanilla JavaScript**: No frameworks needed
- **EventSource API**: SSE streaming
- **CSS3**: Modern styling with animations
- **HTML5**: Semantic markup

---

## ✨ Key Features

### 1. **Streaming Responses** ✨
- Real-time token streaming
- See responses as they generate
- Smooth user experience

### 2. **Multi-Tool Coordination**
- Combines RAG + MCP tools
- Intelligent tool selection
- Shows tool usage in UI

### 3. **Session Management**
- Persistent conversations
- Cross-query memory
- Session clearing

### 4. **Beautiful UI**
- Modern gradient design
- Smooth animations
- Responsive layout
- Intuitive controls

### 5. **Modular Architecture**
- Clean separation of concerns
- Easy to extend
- Well-documented
- Testable

---

## 🎯 Next Steps (Optional Enhancements)

1. **Authentication**: Add user login
2. **Database**: Persist history to PostgreSQL/Redis
3. **WebSockets**: Upgrade from SSE to WS
4. **Voice Input**: Add speech-to-text
5. **File Upload**: Process documents
6. **Deployment**: Docker + Kubernetes config

---

## 📝 Summary

**What We Built**:
- ✅ Full-stack AI agent application
- ✅ FastAPI backend with streaming
- ✅ Beautiful responsive chat UI
- ✅ RAG system with FAISS
- ✅ Multiple MCP server support
- ✅ Real-time Server-Sent Events
- ✅ Session management
- ✅ Tool usage tracking
- ✅ Modular, maintainable code

**How to Start**:
```bash
./start_server.sh
# Open http://localhost:8000
```

---

*Architecture Version: 3.0 (Full-Stack with Streaming UI)*  
*Last Updated: November 2, 2025*

