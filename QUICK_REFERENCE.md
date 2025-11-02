# Quick Reference Card - RAG & History Features

## 🚀 Quick Start

```bash
# Run default demo with examples
python ai_mcp_dynamic.py

# Simple RAG query
python ai_mcp_dynamic.py --mode rag --query "What is DosiBlog?"

# Query with session (remembers context)
python ai_mcp_dynamic.py --query "Hello, I'm Alice" --session-id alice
python ai_mcp_dynamic.py --query "What's my name?" --session-id alice
```

---

## 📋 Common Commands

| Task | Command |
|------|---------|
| **Ask question (agent mode)** | `python ai_mcp_dynamic.py -q "Your question"` |
| **Ask question (RAG only)** | `python ai_mcp_dynamic.py -m rag -q "Your question"` |
| **Use specific session** | `python ai_mcp_dynamic.py -q "Question" --sid mysession` |
| **View session history** | `python ai_mcp_dynamic.py --show-history --sid mysession` |
| **Clear session** | `python ai_mcp_dynamic.py --clear-history --sid mysession` |
| **List all sessions** | `python ai_mcp_dynamic.py --show-history` |

---

## 🔄 Multi-Turn Conversation Example

```bash
# Turn 1: Introduction
python ai_mcp_dynamic.py --sid user1 \
  -q "Hi, I'm John and I'm interested in DosiBlog"

# Turn 2: Follow-up (remembers "DosiBlog")
python ai_mcp_dynamic.py --sid user1 \
  -q "What technologies does it use?"

# Turn 3: Follow-up (remembers "John")
python ai_mcp_dynamic.py --sid user1 \
  -q "What was my name again?"

# View conversation
python ai_mcp_dynamic.py --show-history --sid user1
```

---

## 🎯 Mode Comparison

### Agent Mode (Default)
```bash
python ai_mcp_dynamic.py --query "Calculate 5+3 and tell me about DosiBlog"
```
- ✅ RAG retrieval
- ✅ MCP tools (math, etc.)
- ✅ Conversation history
- Best for: Complex tasks

### RAG Mode
```bash
python ai_mcp_dynamic.py --mode rag --query "What is DosiBlog?"
```
- ✅ RAG retrieval
- ✅ Conversation history
- ❌ No MCP tools
- Best for: Simple Q&A

---

## 💡 Key Concepts

### Session ID
- Unique identifier for each conversation
- Use same ID to continue conversation
- Different IDs = separate conversations

```bash
# Session A
python ai_mcp_dynamic.py --sid sessionA -q "I like Python"

# Session B (independent)
python ai_mcp_dynamic.py --sid sessionB -q "I like JavaScript"

# Back to Session A (remembers Python)
python ai_mcp_dynamic.py --sid sessionA -q "What language do I like?"
```

### History-Aware Retrieval
Automatically reformulates follow-up questions:

```
Turn 1: "What is DosiBlog?"
Turn 2: "Who created it?"
         ↓ (reformulated)
        "Who created DosiBlog?"
```

---

## 🛠️ Architecture at a Glance

```
┌─────────────────────────────────────┐
│  ConversationHistoryManager         │
│  ├── Session storage                │
│  └── Message persistence            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  EnhancedRAGSystem                  │
│  ├── FAISS vector store             │
│  ├── OpenAI embeddings              │
│  └── History-aware retrieval        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Agent Executor (optional)          │
│  ├── MCP tools                      │
│  └── Tool orchestration             │
└─────────────────────────────────────┘
```

---

## 📊 Feature Comparison

| Feature | ai_mcp_dynamic.py | dosi-engine |
|---------|-------------------|-------------|
| **RAG** | ✅ FAISS | ✅ Weaviate |
| **History** | ✅ In-memory | ✅ In-memory |
| **Multi-session** | ✅ Yes | ✅ Yes (multi-tenant) |
| **Streaming** | ❌ No | ✅ Yes |
| **Persistence** | ❌ In-memory | ✅ Weaviate DB |
| **LLM Options** | OpenAI | Gemini/DeepSeek/Ollama |
| **Extra Tools** | ✅ MCP tools | ❌ No |
| **CLI** | ✅ Yes | ❌ No |

---

## 🔍 Debugging

```bash
# Check what's in a session
python ai_mcp_dynamic.py --show-history --sid debug

# Clear and restart
python ai_mcp_dynamic.py --clear-history --sid debug
python ai_mcp_dynamic.py --sid debug -q "Start fresh"

# Test RAG without tools
python ai_mcp_dynamic.py --mode rag -q "Test query"
```

---

## ⚡ Performance Tips

1. **Use RAG mode** for simple queries (faster)
   ```bash
   python ai_mcp_dynamic.py -m rag -q "Quick question"
   ```

2. **Clear old sessions** to save memory
   ```bash
   python ai_mcp_dynamic.py --clear-history --sid old_session
   ```

3. **Limit context** by starting new sessions
   ```bash
   # After 20+ messages, start fresh
   python ai_mcp_dynamic.py --sid new_session_2
   ```

---

## 📚 Documentation Files

- **QUICK_START.md** - Getting started guide
- **MCP_USAGE.md** - MCP server integration
- **RAG_HISTORY_GUIDE.md** - Detailed RAG & history documentation
- **QUICK_REFERENCE.md** - This file

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| "No history found" | Check session ID or start new conversation |
| "RAG not available" | Install: `pip install faiss-cpu openai` |
| "Lost context" | Verify using same `--session-id` |
| "Out of memory" | Clear old sessions with `--clear-history` |

---

## 🎓 Learning Examples

### Example 1: Context Preservation
```bash
# Build context
python ai_mcp_dynamic.py --sid learn1 -q "I'm learning web development"
python ai_mcp_dynamic.py --sid learn1 -q "What should I learn first?"
python ai_mcp_dynamic.py --sid learn1 -q "What was I learning about?"
```

### Example 2: Multiple Users
```bash
# User Alice
python ai_mcp_dynamic.py --sid alice -q "I prefer React"

# User Bob  
python ai_mcp_dynamic.py --sid bob -q "I prefer Vue"

# Ask each their preference
python ai_mcp_dynamic.py --sid alice -q "What do I prefer?"
python ai_mcp_dynamic.py --sid bob -q "What do I prefer?"
```

### Example 3: RAG Knowledge
```bash
# Query knowledge base
python ai_mcp_dynamic.py -m rag -q "What is DosiBlog?"
python ai_mcp_dynamic.py -m rag -q "Tell me more about the creator"
python ai_mcp_dynamic.py -m rag -q "What tech stack is used?"
```

---

## 🔗 Integration

### With Python Code
```python
from ai_mcp_dynamic import rag_system, history_manager

# Query RAG
context = rag_system.retrieve_context("What is DosiBlog?")

# Manage sessions
history = history_manager.get_session_history("user123")
```

### With API (Future)
```python
# Example FastAPI integration
@app.post("/chat/{session_id}")
async def chat(session_id: str, query: str):
    return await run_rag_query(query, session_id)
```

---

## ✅ Checklist for New Users

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set OpenAI API key in `.env`
- [ ] Run default demo: `python ai_mcp_dynamic.py`
- [ ] Try RAG mode: `python ai_mcp_dynamic.py -m rag -q "Test"`
- [ ] Test history: Ask 2-3 follow-up questions with same `--sid`
- [ ] View history: `python ai_mcp_dynamic.py --show-history --sid <your-sid>`
- [ ] Clear session: `python ai_mcp_dynamic.py --clear-history --sid <your-sid>`

---

## 📞 Help

```bash
# Show all options
python ai_mcp_dynamic.py --help

# Show examples
python ai_mcp_dynamic.py --help | grep -A 20 "Examples:"
```

For detailed documentation, see **RAG_HISTORY_GUIDE.md**

