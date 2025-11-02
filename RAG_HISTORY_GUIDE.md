# RAG & History Maintenance Guide

## Overview

The enhanced `ai_mcp_dynamic.py` now includes:
1. **RAG (Retrieval-Augmented Generation)** - Context-aware question answering
2. **Conversation History Maintenance** - Session-based chat history
3. **History-Aware Retrieval** - Questions are reformulated using conversation context
4. **Multiple Operating Modes** - Agent mode with MCP tools or RAG-only mode

---

## Architecture

### 1. History Management System

```python
ConversationHistoryManager
├── store: Dict[session_id → ChatMessageHistory]
├── get_session_history(session_id)
├── get_session_messages(session_id)
├── clear_session(session_id)
├── list_sessions()
└── get_session_summary(session_id)
```

**Key Features:**
- ✅ **Session-based storage**: Each user/conversation gets a unique session ID
- ✅ **Automatic persistence**: Messages are saved after each interaction
- ✅ **Multiple sessions**: Support for concurrent conversations
- ⚠️ **In-memory storage**: History is lost when the process restarts

### 2. Enhanced RAG System

```python
EnhancedRAGSystem
├── vectorstore: FAISS with OpenAI embeddings
├── retriever: Retrieves top-k relevant documents
├── retrieve_context(query) → Simple retrieval
└── query_with_history(query, session_id, llm) → History-aware RAG
```

**Components:**
- **Vector Store**: FAISS for fast similarity search
- **Embeddings**: OpenAI embeddings for semantic understanding
- **History-Aware Retriever**: Reformulates questions using conversation context
- **Contextualization**: Converts follow-up questions to standalone queries

### 3. Query Flow with History

```
User Query → History Manager → History-Aware Retriever
                                        ↓
                                Reformulated Query
                                        ↓
                                Vector Store Search
                                        ↓
                                Retrieved Context
                                        ↓
                        LLM (with context + history)
                                        ↓
                                    Answer
                                        ↓
                        Save to History Manager
```

---

## Usage Examples

### 1. Basic RAG Query with History

```bash
# First question (creates new session)
python ai_mcp_dynamic.py \
    --mode rag \
    --query "What is DosiBlog?" \
    --session-id user123

# Follow-up question (uses history)
python ai_mcp_dynamic.py \
    --mode rag \
    --query "Who created it?" \
    --session-id user123

# Another follow-up (references "it" from history)
python ai_mcp_dynamic.py \
    --mode rag \
    --query "What technologies does it use?" \
    --session-id user123
```

**Output:**
```
🔍 RAG Query: Who created it?
📝 Session ID: user123
📚 Conversation History: 2 previous messages

✅ Answer: DosiBlog was created by Abdullah Al Sazib.
```

### 2. Agent Mode with MCP Tools + History

```bash
# Query with agent and tools
python ai_mcp_dynamic.py \
    --query "My name is Abdullah. What is DosiBlog?" \
    --session-id user123

# Follow-up that references previous context
python ai_mcp_dynamic.py \
    --query "What is my name?" \
    --session-id user123
```

**Output:**
```
💬 User Query: What is my name?
📝 Session ID: user123
📚 Conversation History: 2 previous messages

🤖 Agent calling tool: retrieve_dosiblog_context
✅ Final Answer: Your name is Abdullah, as you mentioned earlier.
```

### 3. Session Management

#### Show Session History
```bash
python ai_mcp_dynamic.py --show-history --session-id user123
```

**Output:**
```
📊 Session Information
Session: user123
Messages: 6

  1. [User] What is DosiBlog?
  2. [AI] DosiBlog is a web development project created by Abdullah Al Sazib...
  3. [User] Who created it?
  4. [AI] DosiBlog was created by Abdullah Al Sazib.
  5. [User] What technologies does it use?
  6. [AI] DosiBlog uses Node.js, Express, and MongoDB...
```

#### Clear Session History
```bash
python ai_mcp_dynamic.py --clear-history --session-id user123
```

#### List All Sessions
```bash
python ai_mcp_dynamic.py --show-history
```

**Output:**
```
📊 Session Information
Active Sessions: 3

  • Session user123: 6 messages
  • Session default: 4 messages
  • Session alice: 2 messages
```

### 4. Default Demo (No Arguments)

```bash
python ai_mcp_dynamic.py
```

Runs example queries demonstrating:
- Multi-turn conversation
- Context preservation
- History-aware responses

---

## CLI Reference

### Basic Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `--query` | `-q` | Query to send to the agent | None (runs demo) |
| `--mode` | `-m` | Operating mode: `agent` or `rag` | `agent` |
| `--session-id` | `--sid` | Session ID for history | `default` |
| `--show-history` | - | Show conversation history | False |
| `--clear-history` | - | Clear session history | False |
| `--add-server` | `-s` | Add MCP server (JSON) | None |

### Mode Comparison

| Feature | Agent Mode | RAG Mode |
|---------|-----------|----------|
| RAG Retrieval | ✅ Yes | ✅ Yes |
| History Aware | ✅ Yes | ✅ Yes |
| MCP Tools | ✅ Yes | ❌ No |
| Use Case | Complex tasks with tools | Simple Q&A |

---

## Implementation Details

### History-Aware Retrieval

The system reformulates follow-up questions using conversation history:

**Without History:**
```
User: "Who created it?"
System: [Confused - what is "it"?]
```

**With History:**
```
Previous: "What is DosiBlog?"
User: "Who created it?"
Reformulated: "Who created DosiBlog?"
System: "DosiBlog was created by Abdullah Al Sazib."
```

### Prompt Templates

#### Contextualization Prompt
```python
"Given a chat history and the latest user question, 
formulate a standalone question which can be understood 
without the chat history. Do NOT answer the question, 
just reformulate it if needed."
```

#### Answer Prompt
```python
"You are a helpful AI assistant. Use the following 
context to answer questions accurately and naturally.
Rules:
- Answer naturally without mentioning 'the context'
- If you don't know, say so honestly
- Be concise and helpful"
```

### RAG Chain Structure

```python
# History-aware retriever
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_prompt
)

# Question answering chain
question_answer_chain = create_stuff_documents_chain(
    llm, answer_prompt
)

# Retrieval chain
rag_chain = create_retrieval_chain(
    history_aware_retriever, 
    question_answer_chain
)

# Add history wrapper
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)
```

---

## Comparison with DosiBridge/dosi-engine

### Similarities

| Feature | dosi-engine | ai_mcp_dynamic.py |
|---------|-------------|-------------------|
| History Management | ✅ Session-based store | ✅ Session-based store |
| RAG System | ✅ Weaviate + HuggingFace | ✅ FAISS + OpenAI |
| History-Aware Retrieval | ✅ LangChain chains | ✅ LangChain chains |
| Multi-Session Support | ✅ Multi-tenant | ✅ Multi-session |
| Streaming Support | ✅ Async streaming | ⚠️ Not yet |

### Key Differences

#### 1. Vector Store
- **dosi-engine**: Weaviate (production-grade, persistent)
- **ai_mcp_dynamic**: FAISS (lightweight, in-memory)

#### 2. Embeddings
- **dosi-engine**: HuggingFace (`all-mpnet-base-v2`)
- **ai_mcp_dynamic**: OpenAI embeddings

#### 3. LLM Options
- **dosi-engine**: Gemini, DeepSeek, Ollama
- **ai_mcp_dynamic**: OpenAI GPT-4o

#### 4. Additional Features
- **dosi-engine**: 
  - Multi-tenancy with Weaviate
  - Document management (insert, delete by title)
  - Hybrid search with fusion
  - Streaming responses
  
- **ai_mcp_dynamic**:
  - MCP tool integration
  - Agent executor with tools
  - Command-line interface
  - Multiple operating modes

---

## Advanced Examples

### Example 1: Multi-Turn Conversation

```bash
# Session 1: Initial query
python ai_mcp_dynamic.py --mode rag --sid session1 \
    --query "What is DosiBlog?"

# Session 1: Follow-up
python ai_mcp_dynamic.py --mode rag --sid session1 \
    --query "When was it started?"

# Session 1: Another follow-up
python ai_mcp_dynamic.py --mode rag --sid session1 \
    --query "What features does it have?"

# View the conversation
python ai_mcp_dynamic.py --show-history --sid session1
```

### Example 2: Parallel Sessions

```bash
# User 1's session
python ai_mcp_dynamic.py --sid user1 \
    --query "I'm interested in web development projects"

# User 2's separate session
python ai_mcp_dynamic.py --sid user2 \
    --query "Tell me about MongoDB databases"

# Back to user 1
python ai_mcp_dynamic.py --sid user1 \
    --query "Can you recommend any?"

# Each session maintains independent history
```

### Example 3: Agent with Tools + RAG

```bash
# Agent can use both MCP tools and RAG
python ai_mcp_dynamic.py --sid technical_user \
    --query "Calculate 25 * 4 and tell me about DosiBlog"

# Follow-up using both history and tools
python ai_mcp_dynamic.py --sid technical_user \
    --query "What was that number multiplied by 2?"
```

---

## Best Practices

### 1. Session ID Naming
```bash
# ✅ Good: Descriptive session IDs
--session-id user_123
--session-id conversation_2024_11_02
--session-id support_ticket_456

# ❌ Bad: Generic or conflicting IDs
--session-id test
--session-id 1
--session-id session
```

### 2. History Management
```bash
# Clear session after conversation ends
python ai_mcp_dynamic.py --clear-history --sid user_123

# Check session before clearing
python ai_mcp_dynamic.py --show-history --sid user_123
python ai_mcp_dynamic.py --clear-history --sid user_123
```

### 3. Mode Selection
```bash
# Use RAG mode for simple Q&A (faster, no tool overhead)
python ai_mcp_dynamic.py --mode rag --query "What is DosiBlog?"

# Use agent mode when you need tools
python ai_mcp_dynamic.py --mode agent --query "Calculate 5 + 3"
```

### 4. Production Considerations

**Current Limitations (In-Memory):**
- ❌ History lost on restart
- ❌ No persistence between sessions
- ❌ Memory grows with sessions

**For Production (Like dosi-engine):**
- ✅ Use persistent storage (Weaviate, PostgreSQL, Redis)
- ✅ Implement session cleanup/expiry
- ✅ Add authentication and authorization
- ✅ Enable streaming for better UX
- ✅ Add monitoring and logging

---

## Troubleshooting

### Issue: "No conversation history found"
**Cause**: Session ID doesn't exist or was cleared  
**Solution**: Verify session ID or start a new conversation

### Issue: "RAG system not available"
**Cause**: FAISS or OpenAI embeddings not installed  
**Solution**: 
```bash
pip install faiss-cpu openai langchain-openai
```

### Issue: "Context doesn't include recent messages"
**Cause**: Using different session IDs  
**Solution**: Use the same `--session-id` for related queries

### Issue: "Agent doesn't remember previous context"
**Cause**: History not being saved properly  
**Solution**: Check that `session_id` is consistent across calls

---

## Future Enhancements

### Planned Features
1. **Persistent Storage**: Save history to database
2. **Streaming Responses**: Like `ragquery_async_stream` in dosi-engine
3. **Session Expiry**: Auto-cleanup old sessions
4. **Context Window Management**: Limit history to avoid token limits
5. **Multiple Vector Stores**: Support for Weaviate, Pinecone, etc.
6. **Advanced Retrieval**: Hybrid search, reranking
7. **Export/Import**: Save and restore conversations

### Integration Ideas
```python
# Example: Add custom RAG sources
rag_system.add_documents([
    "Your custom document content here...",
])

# Example: Use with FastAPI
@app.post("/chat")
async def chat(query: str, session_id: str):
    return await run_rag_query(query, session_id)
```

---

## Conclusion

The enhanced `ai_mcp_dynamic.py` provides:
- ✅ **Robust RAG** with context retrieval
- ✅ **Session-based history** for conversations
- ✅ **History-aware retrieval** for follow-up questions
- ✅ **Flexible modes** (agent with tools or RAG-only)
- ✅ **Easy CLI** for testing and demos

Perfect for:
- Building chatbots with memory
- Q&A systems with context
- Multi-turn conversations
- Tool-augmented RAG systems

For production deployment, consider migrating to persistent storage like the dosi-engine implementation with Weaviate.

