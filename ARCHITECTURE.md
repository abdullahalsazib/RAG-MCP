# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / CLI                               │
│                                                                   │
│  Commands: --query, --session-id, --mode, --show-history, etc.  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN CONTROLLER                             │
│                                                                   │
│  • Parse CLI arguments                                            │
│  • Route to appropriate mode (agent/rag)                         │
│  • Handle session management commands                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
         ┌──────────────────┐  ┌──────────────────┐
         │   AGENT MODE     │  │   RAG MODE       │
         │  (with tools)    │  │  (RAG only)      │
         └──────────────────┘  └──────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              CONVERSATION HISTORY MANAGER                        │
│                                                                   │
│  store: Dict[session_id → ChatMessageHistory]                   │
│                                                                   │
│  Methods:                                                         │
│    • get_session_history(session_id)                            │
│    • get_session_messages(session_id)                           │
│    • clear_session(session_id)                                  │
│    • list_sessions()                                             │
│    • get_session_summary(session_id)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   ENHANCED RAG SYSTEM                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Vector Store: FAISS                                    │    │
│  │  Embeddings: OpenAI (text-embedding-ada-002)            │    │
│  │  Documents: DosiBlog knowledge base                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Methods:                                                         │
│    • retrieve_context(query) → context                          │
│    • query_with_history(query, session_id, llm) → answer       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            HISTORY-AWARE RETRIEVAL CHAIN                         │
│                                                                   │
│  1. Contextualize Question                                       │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ chat_history + current_question                      │    │
│     │         ↓                                             │    │
│     │ reformulated_standalone_question                     │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                   │
│  2. Retrieve Context                                             │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ standalone_question                                  │    │
│     │         ↓                                             │    │
│     │ vector_search (FAISS)                                │    │
│     │         ↓                                             │    │
│     │ top_k_relevant_documents                             │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                   │
│  3. Generate Answer                                              │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ context + chat_history + current_question            │    │
│     │         ↓                                             │    │
│     │ LLM (GPT-4o)                                         │    │
│     │         ↓                                             │    │
│     │ natural_language_answer                              │    │
│     └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MCP CLIENT MANAGER                             │
│                  (Agent Mode Only)                               │
│                                                                   │
│  • Connect to MCP servers                                        │
│  • Load remote tools                                             │
│  • Maintain sessions                                             │
│  • Tool orchestration                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTOR                                │
│                  (Agent Mode Only)                               │
│                                                                   │
│  • Combine RAG tool + MCP tools                                  │
│  • LLM-based tool selection                                      │
│  • Execute tool calls                                            │
│  • Generate final response                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Multi-Turn Conversation

```
┌─────────────────────────────────────────────────────────────────┐
│ Turn 1: "What is DosiBlog?"                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Empty history for session "user1"              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RAG System:                                                       │
│   Query: "What is DosiBlog?"                                     │
│   No reformulation needed (first question)                       │
│   Retrieved context: [doc1, doc2, doc3]                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LLM Response: "DosiBlog is a web development project..."        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Save Q&A to session "user1"                    │
│   [HumanMessage("What is DosiBlog?"),                           │
│    AIMessage("DosiBlog is a web development project...")]       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Turn 2: "Who created it?"                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Load history for session "user1"               │
│   Previous messages: 2 (1 Q&A pair)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History-Aware Retriever:                                         │
│   Input: "Who created it?" + chat_history                       │
│   Context: Previous Q about "DosiBlog"                          │
│   Reformulated: "Who created DosiBlog?"                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RAG System:                                                       │
│   Query: "Who created DosiBlog?"                                 │
│   Retrieved context: [creator info, ...]                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LLM Response: "DosiBlog was created by Abdullah Al Sazib."      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Append to session "user1"                      │
│   [HumanMessage("What is DosiBlog?"),                           │
│    AIMessage("DosiBlog is a web development project..."),       │
│    HumanMessage("Who created it?"),                             │
│    AIMessage("DosiBlog was created by Abdullah Al Sazib.")]     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Turn 3: "What technologies does it use?"                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Load history for session "user1"               │
│   Previous messages: 4 (2 Q&A pairs)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History-Aware Retriever:                                         │
│   Input: "What technologies does it use?" + chat_history        │
│   Context: "it" refers to "DosiBlog" from history              │
│   Reformulated: "What technologies does DosiBlog use?"          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RAG System:                                                       │
│   Query: "What technologies does DosiBlog use?"                  │
│   Retrieved context: [Node.js, Express, MongoDB, ...]          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LLM Response: "DosiBlog uses Node.js, Express, and MongoDB."    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Complete history for session "user1"           │
│   Total messages: 6 (3 Q&A pairs)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction: Agent Mode with Tools

```
┌─────────────────────────────────────────────────────────────────┐
│ User Query: "Calculate 25 * 4 and tell me about DosiBlog"       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent Executor:                                                  │
│   Available Tools:                                               │
│     1. retrieve_dosiblog_context (RAG)                          │
│     2. calculator (MCP)                                          │
│     3. [other MCP tools...]                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LLM (GPT-4o) Plans:                                             │
│   Step 1: Use calculator for "25 * 4"                           │
│   Step 2: Use retrieve_dosiblog_context for "DosiBlog"         │
│   Step 3: Synthesize both results                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────┬──────────────────────────────────┐
│     Tool Call 1              │      Tool Call 2                 │
│  calculator.multiply(25, 4)  │  retrieve_dosiblog_context(...)  │
│         ↓                    │           ↓                      │
│    Result: 100               │    Result: "DosiBlog is..."      │
└──────────────────────────────┴──────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent Synthesizes:                                               │
│   "25 * 4 = 100. DosiBlog is a web development project          │
│    created by Abdullah Al Sazib using Node.js, Express,         │
│    and MongoDB."                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ History Manager: Save complete interaction                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Session Management Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│           CONVERSATION HISTORY MANAGER                           │
│                                                                   │
│  self.store: Dict[str, ChatMessageHistory]                      │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │ session1   │  │ session2   │  │ session3   │  ...           │
│  │            │  │            │  │            │                 │
│  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │                │
│  │ │ Msg 1  │ │  │ │ Msg 1  │ │  │ │ Msg 1  │ │                │
│  │ │ Msg 2  │ │  │ │ Msg 2  │ │  │ │ Msg 2  │ │                │
│  │ │ Msg 3  │ │  │ │ Msg 3  │ │  │ │ Msg 3  │ │                │
│  │ │  ...   │ │  │ │  ...   │ │  │ │  ...   │ │                │
│  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │                │
│  └────────────┘  └────────────┘  └────────────┘                │
│                                                                   │
│  Operations:                                                      │
│    • Create new session (automatic on first access)             │
│    • Retrieve session history                                    │
│    • Append messages to session                                  │
│    • Clear session                                               │
│    • List all sessions                                           │
└─────────────────────────────────────────────────────────────────┘

Example Usage:
┌─────────────────────────────────────────────────────────────────┐
│ User A (session "alice"):                                        │
│   Q: "Hi, I'm Alice"                                             │
│   A: "Hello Alice! How can I help you?"                          │
│   Q: "What's my name?"                                           │
│   A: "Your name is Alice."                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ User B (session "bob"):                                          │
│   Q: "Hi, I'm Bob"                                               │
│   A: "Hello Bob! How can I help you?"                            │
│   Q: "What's my name?"                                           │
│   A: "Your name is Bob."                                         │
└─────────────────────────────────────────────────────────────────┘

Sessions are independent - no cross-contamination!
```

---

## RAG System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENHANCED RAG SYSTEM                           │
│                                                                   │
│  Knowledge Base (texts):                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • "DosiBlog is a web development project..."            │   │
│  │ • "DosiBlog uses Node.js, Express, and MongoDB..."      │   │
│  │ • "The DosiBlog project was started in September 2025"  │   │
│  │ • "DosiBlog features include user authentication..."    │   │
│  │ • "Abdullah Al Sazib is a full-stack developer..."      │   │
│  │ • "The project uses RESTful API architecture..."        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         OpenAI Embeddings                                │   │
│  │  (text-embedding-ada-002)                                │   │
│  │                                                           │   │
│  │  Converts text → 1536-dimensional vectors                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         FAISS Vector Store                               │   │
│  │                                                           │   │
│  │  • Fast similarity search                                │   │
│  │  • In-memory storage                                     │   │
│  │  • Efficient indexing                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Retriever (k=3)                                  │   │
│  │                                                           │   │
│  │  Query → Top 3 most relevant documents                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Retrieval Flow:
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Query: "What technologies does DosiBlog use?"           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Embed Query: [0.123, -0.456, 0.789, ..., 0.321]             │
│    (1536 dimensions)                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. FAISS Similarity Search:                                      │
│    Compare query embedding with all document embeddings         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Top 3 Results (by similarity score):                         │
│    1. "DosiBlog uses Node.js, Express, and MongoDB..." (0.92)  │
│    2. "The project uses RESTful API architecture..." (0.85)    │
│    3. "DosiBlog features include user authentication..." (0.78)│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Context for LLM: Concatenated top 3 documents               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Comparison: dosi-engine vs ai_mcp_dynamic Architecture

### dosi-engine (Weaviate-based)
```
User Query
    ↓
┌────────────────────────────────────┐
│   WeaviateService                  │
│   ├── Weaviate Client              │
│   ├── HuggingFace Embeddings       │
│   ├── Multi-tenant Collections     │
│   └── Session Store (dict)         │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   History-Aware RAG Chain          │
│   ├── Contextualization            │
│   ├── Retrieval (Hybrid Search)    │
│   └── Answer Generation            │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   LLM (Gemini/DeepSeek/Ollama)    │
└────────────────────────────────────┘
    ↓
Response (with optional streaming)
```

### ai_mcp_dynamic (FAISS-based + MCP)
```
User Query (via CLI)
    ↓
┌────────────────────────────────────┐
│   Main Controller                  │
│   ├── CLI Parser                   │
│   ├── Mode Selector (agent/rag)    │
│   └── Session Manager              │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   ConversationHistoryManager       │
│   └── Session Store (dict)         │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   EnhancedRAGSystem                │
│   ├── FAISS Vector Store           │
│   ├── OpenAI Embeddings            │
│   └── History-Aware Retrieval      │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   Agent Executor (if agent mode)   │
│   ├── RAG Tool                     │
│   ├── MCP Tools                    │
│   └── Tool Orchestration           │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│   LLM (OpenAI GPT-4o)             │
└────────────────────────────────────┘
    ↓
Response
```

---

## Technology Stack

### Core Technologies
```
┌─────────────────────────────────────────────────────────────────┐
│                      Python 3.8+                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬─────────────────────────┐
│   LangChain      │   OpenAI         │   FAISS                  │
│   Framework      │   LLM & Embed    │   Vector Store           │
└──────────────────┴──────────────────┴─────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬─────────────────────────┐
│   MCP Protocol   │   Async/Await    │   Argparse               │
│   Tool Integration│  Async Execution │   CLI Interface          │
└──────────────────┴──────────────────┴─────────────────────────┘
```

### Dependencies
- **LangChain**: RAG chains, history management, agent execution
- **OpenAI**: LLM (GPT-4o) and embeddings
- **FAISS**: Fast similarity search for vector store
- **MCP**: Tool server protocol and integration
- **Python Standard Library**: argparse, asyncio, json, typing

---

## Design Patterns Used

### 1. **Context Manager Pattern**
```python
async with MCPClientManager(mcp_servers) as mcp_tools:
    # Tools automatically loaded and cleaned up
    pass
```

### 2. **Dependency Injection**
```python
def query_with_history(self, query: str, session_id: str, llm: ChatOpenAI):
    # LLM injected, allowing flexibility
```

### 3. **Factory Pattern**
```python
def get_session_history(session_id: str):
    if session_id not in self.store:
        self.store[session_id] = ChatMessageHistory()
    return self.store[session_id]
```

### 4. **Strategy Pattern**
```python
# Different modes (agent/rag) use different strategies
if mode == "rag":
    await run_rag_query(query, session_id)
else:
    await run_agent_query(agent_executor, query, session_id)
```

---

## Scalability Considerations

### Current (Development)
```
Memory: In-memory storage
  ↓
Limitation: Lost on restart
  ↓
Suitable for: Development, testing, demos
```

### Production (Recommended)
```
Persistent Storage: PostgreSQL, Redis, Weaviate
  ↓
Session Management: TTL, cleanup jobs
  ↓
Scalability: Horizontal scaling, load balancing
  ↓
Suitable for: Production applications
```

---

## Security Architecture

### Current Implementation
- ✅ Session isolation (no cross-session access)
- ✅ No hardcoded credentials
- ✅ Environment variable for API keys
- ⚠️ No authentication layer
- ⚠️ No rate limiting
- ⚠️ No input sanitization

### Production Recommendations
- Add user authentication
- Implement rate limiting per session
- Sanitize inputs
- Add logging and monitoring
- Implement session expiry
- Add API key rotation

---

## Performance Characteristics

### FAISS Vector Search
- **Speed**: O(log n) for k-NN search
- **Memory**: All vectors in memory
- **Scalability**: Up to ~1M documents
- **Trade-off**: Fast but not persistent

### History Management
- **Speed**: O(1) session lookup
- **Memory**: Linear with message count
- **Scalability**: Limited by RAM
- **Trade-off**: Fast but memory-bound

### LLM Calls
- **Speed**: ~2-5 seconds per call
- **Cost**: Per token pricing
- **Trade-off**: Quality vs. speed/cost

---

This architecture provides a solid foundation for RAG-based conversational AI with history maintenance, suitable for development and small-scale production deployments.

