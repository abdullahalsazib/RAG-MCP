# 🌐 AI MCP Agent - Web Application Guide

## ✅ **COMPLETE FULL-STACK APPLICATION**

Your AI agent now has a beautiful web interface with streaming responses!

---

## 🚀 Quick Start

### 1. Start the Server
```bash
./start_server.sh
```

### 2. Open Your Browser
```
http://localhost:8000
```

### 3. Start Chatting!
Type your questions and watch responses stream in real-time ⚡

---

## 🎨 Features

### ✨ **Real-Time Streaming**
- Responses appear word-by-word as they're generated
- See exactly which tools the agent is using
- Smooth, natural chat experience

### 🧠 **Intelligent Agent**
- **RAG System**: Access to DosiBlog knowledge base
- **MCP Tools**: Math operations, greetings, and more
- **Memory**: Remembers your conversation
- **Multi-tool**: Can use multiple tools in one query

### 💬 **Beautiful UI**
- Modern gradient design with smooth animations
- Responsive layout (works on desktop & mobile)
- Typing indicators
- Tool usage badges
- Status bar with real-time metrics

### 🔄 **Mode Switching**
- **Agent Mode**: Full power with all MCP tools
- **RAG Mode**: Fast responses using knowledge base only

---

## 📊 **Screenshot of Features**

```
┌─────────────────────────────────────────────────┐
│  🤖 AI MCP Agent                      │ Agent ▼ │ Clear │ ℹ️ │
│  Intelligent assistant with RAG, MCP tools...   │
├─────────────────────────────────────────────────┤
│                                                 │
│  AI: Hello! I can help you with:               │
│      • DosiBlog information                     │
│      • Math calculations                        │
│      • And much more!                          │
│                                                 │
│  You: What is DosiBlog?                        │
│                                                 │
│  AI: 🔧 retrieve_dosiblog_context              │
│                                                 │
│      DosiBlog is a web development             │
│      project created by Abdullah Al Sazib...   │
│                                                 │
├─────────────────────────────────────────────────┤
│ [Type your message...]              │ Send │    │
├─────────────────────────────────────────────────┤
│ Mode: Agent │ Session: default │ Messages: 2    │
└─────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Chat Endpoints

#### 1. **GET /** - Web Interface
Opens the beautiful chat UI

#### 2. **POST /api/chat** - Non-Streaming Chat
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

#### 3. **POST /api/chat/stream** - Streaming Chat ⚡
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
data: {"chunk": "🔧 Using tool: addNumber\n", "done": false, "tool": "addNumber"}
data: {"chunk": "The ", "done": false}
data: {"chunk": "result ", "done": false}
data: {"chunk": "is ", "done": false}
data: {"chunk": "8", "done": false}
data: {"chunk": "", "done": true, "tools_used": ["addNumber"]}
```

### Session Endpoints

#### 4. **GET /api/session/{session_id}** - Get Session Info
```bash
curl http://localhost:8000/api/session/user123
```

**Response**:
```json
{
  "session_id": "user123",
  "message_count": 4,
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

#### 5. **DELETE /api/session/{session_id}** - Clear Session
```bash
curl -X DELETE http://localhost:8000/api/session/user123
```

#### 6. **GET /api/sessions** - List All Sessions
```bash
curl http://localhost:8000/api/sessions
```

### Utility Endpoints

#### 7. **GET /health** - Health Check
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "rag_available": true,
  "mcp_servers": 2
}
```

#### 8. **GET /api/tools** - Get Available Tools
```bash
curl http://localhost:8000/api/tools
```

**Response**:
```json
{
  "local_tools": [
    {
      "name": "retrieve_dosiblog_context",
      "description": "Retrieves information about DosiBlog",
      "type": "rag"
    }
  ],
  "mcp_servers": [
    {"name": "Math", "url": "https://...", "status": "configured"},
    {"name": "Jack", "url": "https://...", "status": "configured"}
  ]
}
```

---

## 💻 Using the Web Interface

### Basic Usage

1. **Type your message** in the input box
2. **Click Send** or press Enter
3. **Watch the response** stream in real-time
4. **See tool usage** indicated with badges
5. **Continue the conversation** with context maintained

### Example Conversations

#### Example 1: Simple Question
```
You: What is DosiBlog?

AI: 🔧 retrieve_dosiblog_context

    DosiBlog is a web development project created by 
    Abdullah Al Sazib. It includes features like user 
    authentication, blog post creation, and a commenting 
    system.
```

#### Example 2: Math with Memory
```
You: Calculate 10 + 5, then multiply by 2

AI: 🔧 addNumber
    🔧 addMul
    
    The result of (10 + 5) × 2 is 30.

You: What was my calculation?

AI: Your calculation was (10 + 5) × 2, which equals 30.
```

#### Example 3: Multi-Tool Query
```
You: Say hello to Jack, calculate 5+3, and tell me about DosiBlog

AI: 🔧 showHello
    🔧 addNumber
    🔧 retrieve_dosiblog_context
    
    Hello, Jack!
    
    5 + 3 = 8
    
    DosiBlog is a web development project...
```

---

## 🎨 UI Components

### Header
- **Title & Description**
- **Mode Selector**: Switch between Agent/RAG
- **Clear Button**: Reset conversation
- **Info Button**: Show/hide help panel

### Chat Area
- **Message History**: Scrollable conversation
- **User Messages**: Right-aligned with gradient
- **AI Messages**: Left-aligned with context
- **Tool Badges**: Show which tools were used
- **Auto-scroll**: Follows conversation

### Input Area
- **Typing Indicator**: Shows when AI is thinking
- **Message Input**: Type your questions
- **Send Button**: Submit message
- **Keyboard Support**: Enter to send

### Status Bar
- **Mode**: Current mode (Agent/RAG)
- **Session ID**: Current session
- **Message Count**: Total messages
- **Connection Status**: Server health

---

## 🔧 Configuration

### Server Settings
Edit `backend/api.py`:
```python
# Change port
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Custom port
```

### UI Customization
Edit `static/css/style.css`:
```css
/* Change color scheme */
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
}
```

### Session Configuration
Sessions are stored in-memory by default. For production:
- Add Redis for persistent sessions
- Add database for long-term storage
- Implement user authentication

---

## 🚀 Deployment

### Local Development
```bash
./start_server.sh
# Server runs on http://localhost:8000
```

### Production Deployment

#### Option 1: Direct with Uvicorn
```bash
uv run --no-project python -m uvicorn backend.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

#### Option 2: Docker (create Dockerfile)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Option 3: Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 🧪 Testing

### Test Web Interface
1. Start server: `./start_server.sh`
2. Open browser: http://localhost:8000
3. Test queries:
   - "What is DosiBlog?"
   - "Calculate (5+3)*2"
   - "Say hello to me"

### Test Streaming API
```bash
# Using curl with -N flag for streaming
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"Count to 5","session_id":"test","mode":"agent"}'
```

### Test Regular API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test","mode":"rag"}'
```

---

## 📊 Performance

### Streaming Benefits
- **Faster perceived response**: Users see output immediately
- **Better UX**: No waiting for complete response
- **Progress indication**: Tool usage shown in real-time
- **Lower latency**: Initial tokens arrive quickly

### Optimization Tips
1. **Use RAG mode** for faster responses when MCP tools aren't needed
2. **Keep sessions short** or implement cleanup
3. **Use connection pooling** for database/Redis
4. **Enable gzip compression** in production
5. **Cache common queries** if applicable

---

## 🐛 Troubleshooting

### Issue: Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python -m uvicorn backend.api:app --port 8080
```

### Issue: Streaming not working
- Check browser supports EventSource
- Verify CORS settings
- Check network tab for errors

### Issue: Tools not loading
- Verify MCP servers in `mcp_servers.json`
- Check MCP server URLs are accessible
- Look at server logs for errors

### Issue: Memory growing
- Implement session cleanup
- Limit message history per session
- Use Redis for persistent storage

---

## 🎯 Next Steps

### Immediate Enhancements
1. ✅ **Working**: Full-stack with streaming
2. 🔄 **Add**: User authentication
3. 🔄 **Add**: Save conversations to database
4. 🔄 **Add**: Export chat history
5. 🔄 **Add**: Voice input/output

### Advanced Features
1. 📊 **Analytics**: Track usage patterns
2. 🎨 **Themes**: Dark/light mode
3. 🌍 **i18n**: Multiple languages
4. 📱 **Mobile app**: React Native version
5. 🔐 **Security**: Rate limiting, API keys

---

## ✅ Summary

**What You Have Now**:
- ✅ Beautiful web interface
- ✅ Real-time streaming responses
- ✅ FastAPI backend with SSE
- ✅ Multi-tool coordination
- ✅ Conversation memory
- ✅ Modular architecture
- ✅ Production-ready code

**How to Use**:
```bash
# Start server
./start_server.sh

# Open browser
http://localhost:8000

# Start chatting!
```

**API Available**:
- 8 REST endpoints
- Streaming support
- Session management
- Tool information

---

🎉 **Congratulations! You now have a complete, production-ready AI chat application!**

---

*Version: 3.0 (Full-Stack with Streaming)*  
*Last Updated: November 2, 2025*

