"""
FastAPI application with streaming chat endpoints
"""
import asyncio
import json
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.history import history_manager
from src.agent import run_agent_mode, run_rag_mode
from src.mcp_client import MCPClientManager
from src.tools import retrieve_dosiblog_context
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage


# Initialize FastAPI app
app = FastAPI(
    title="AI MCP Agent API",
    description="Intelligent agent with RAG, MCP tools, and conversation memory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    mode: str = "agent"  # "agent" or "rag"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    mode: str
    tools_used: list = []


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    messages: list


# Health check
@app.get("/")
async def root():
    """Root endpoint - redirect to chat UI"""
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "rag_available": True,
        "mcp_servers": len(Config.load_mcp_servers())
    }


# Chat endpoint (non-streaming)
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint
    
    Args:
        request: ChatRequest with message, session_id, and mode
        
    Returns:
        ChatResponse with answer
    """
    try:
        if request.mode == "rag":
            # RAG-only mode
            from src.rag import rag_system
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model=Config.OPENAI_MODEL, temperature=0)
            answer = rag_system.query_with_history(
                request.message, 
                request.session_id, 
                llm
            )
            
            return ChatResponse(
                response=answer,
                session_id=request.session_id,
                mode="rag",
                tools_used=["retrieve_dosiblog_context"]
            )
        else:
            # Agent mode
            mcp_servers = Config.load_mcp_servers()
            tools_used = []
            
            async with MCPClientManager(mcp_servers) as mcp_tools:
                all_tools = [retrieve_dosiblog_context] + mcp_tools
                
                # Create agent
                agent = create_agent(
                    model=Config.OPENAI_MODEL,
                    tools=all_tools,
                    system_prompt="You are a helpful AI assistant with access to various tools. Use them when needed."
                )
                
                # Get history
                history = history_manager.get_session_messages(request.session_id)
                messages = list(history) + [HumanMessage(content=request.message)]
                
                # Run agent
                final_answer = ""
                async for event in agent.astream({"messages": messages}, stream_mode="values"):
                    last_msg = event["messages"][-1]
                    
                    if isinstance(last_msg, AIMessage):
                        if getattr(last_msg, "tool_calls", None):
                            for call in last_msg.tool_calls:
                                tools_used.append(call['name'])
                        else:
                            final_answer = last_msg.content
                
                # Save to history
                session_history = history_manager.get_session_history(request.session_id)
                session_history.add_user_message(request.message)
                session_history.add_ai_message(final_answer)
                
                return ChatResponse(
                    response=final_answer,
                    session_id=request.session_id,
                    mode="agent",
                    tools_used=tools_used
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Streaming chat endpoint
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - returns chunks as they're generated
    
    Args:
        request: ChatRequest with message, session_id, and mode
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    async def generate() -> AsyncGenerator[str, None]:
        try:
            if request.mode == "rag":
                # For RAG mode, we'll stream the response
                from src.rag import rag_system
                from langchain_openai import ChatOpenAI
                
                llm = ChatOpenAI(model=Config.OPENAI_MODEL, temperature=0, streaming=True)
                
                # Get history
                history = history_manager.get_session_messages(request.session_id)
                
                # Build context
                from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful AI assistant. Use the following context to answer questions.\nContext: {context}"),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ])
                
                # Retrieve context
                context = rag_system.retrieve_context(request.message)
                
                # Stream response
                full_response = ""
                async for chunk in llm.astream(prompt.format(
                    context=context,
                    chat_history=history,
                    input=request.message
                )):
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'chunk': chunk.content, 'done': False})}\n\n"
                
                # Save to history
                session_history = history_manager.get_session_history(request.session_id)
                session_history.add_user_message(request.message)
                session_history.add_ai_message(full_response)
                
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            else:
                # Agent mode with streaming
                mcp_servers = Config.load_mcp_servers()
                
                async with MCPClientManager(mcp_servers) as mcp_tools:
                    all_tools = [retrieve_dosiblog_context] + mcp_tools
                    
                    # Create agent
                    agent = create_agent(
                        model=Config.OPENAI_MODEL,
                        tools=all_tools,
                        system_prompt="You are a helpful AI assistant with access to various tools. Use them when needed."
                    )
                    
                    # Get history
                    history = history_manager.get_session_messages(request.session_id)
                    messages = list(history) + [HumanMessage(content=request.message)]
                    
                    # Stream agent responses
                    full_response = ""
                    tool_calls_made = []
                    
                    async for event in agent.astream({"messages": messages}, stream_mode="values"):
                        last_msg = event["messages"][-1]
                        
                        if isinstance(last_msg, AIMessage):
                            if getattr(last_msg, "tool_calls", None):
                                for call in last_msg.tool_calls:
                                    tool_info = f"🔧 Using tool: {call['name']}"
                                    tool_calls_made.append(call['name'])
                                    yield f"data: {json.dumps({'chunk': tool_info + '\\n', 'done': False, 'tool': call['name']})}\n\n"
                            elif last_msg.content:
                                # Stream the actual response
                                # Split into words for smoother streaming
                                words = last_msg.content.split()
                                for i, word in enumerate(words):
                                    chunk = word + (" " if i < len(words) - 1 else "")
                                    full_response += chunk
                                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                                    await asyncio.sleep(0.01)  # Small delay for effect
                    
                    # Save to history
                    session_history = history_manager.get_session_history(request.session_id)
                    session_history.add_user_message(request.message)
                    session_history.add_ai_message(full_response)
                    
                    yield f"data: {json.dumps({'chunk': '', 'done': True, 'tools_used': tool_calls_made})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Session management endpoints
@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get session information"""
    messages = history_manager.get_session_messages(session_id)
    
    return SessionInfo(
        session_id=session_id,
        message_count=len(messages),
        messages=[
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            }
            for msg in messages
        ]
    )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session history"""
    history_manager.clear_session(session_id)
    return {"status": "success", "message": f"Session {session_id} cleared"}


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    sessions = history_manager.list_sessions()
    return {
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(history_manager.get_session_messages(sid))
            }
            for sid in sessions
        ]
    }


# MCP tools info
@app.get("/api/tools")
async def get_tools_info():
    """Get information about available tools"""
    mcp_servers = Config.load_mcp_servers()
    
    tools_info = {
        "local_tools": [
            {
                "name": "retrieve_dosiblog_context",
                "description": "Retrieves information about DosiBlog project",
                "type": "rag"
            }
        ],
        "mcp_servers": []
    }
    
    # We can't easily get MCP tools without connecting, so just return server info
    for server in mcp_servers:
        tools_info["mcp_servers"].append({
            "name": server.get("name"),
            "url": server.get("url"),
            "status": "configured"
        })
    
    return tools_info


# MCP Server Management Endpoints
class MCPServerRequest(BaseModel):
    name: str
    url: str


@app.get("/api/mcp-servers")
async def list_mcp_servers():
    """List all configured MCP servers"""
    try:
        servers = Config.load_mcp_servers()
        return {
            "status": "success",
            "count": len(servers),
            "servers": servers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mcp-servers")
async def add_mcp_server(server: MCPServerRequest):
    """Add a new MCP server to the configuration"""
    try:
        # Read existing servers
        config_file = Config.ROOT_DIR / Config.MCP_SERVERS_FILE
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                servers = json.load(f)
        else:
            servers = []
        
        # Check if server already exists
        for existing_server in servers:
            if existing_server.get("name") == server.name or existing_server.get("url") == server.url:
                raise HTTPException(
                    status_code=400, 
                    detail=f"MCP server with name '{server.name}' or URL '{server.url}' already exists"
                )
        
        # Add new server
        new_server = {
            "name": server.name,
            "url": server.url
        }
        servers.append(new_server)
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(servers, f, indent=2)
        
        return {
            "status": "success",
            "message": f"MCP server '{server.name}' added successfully",
            "server": new_server,
            "total_servers": len(servers)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/mcp-servers/{server_name}")
async def delete_mcp_server(server_name: str):
    """Delete an MCP server from the configuration"""
    try:
        config_file = Config.ROOT_DIR / Config.MCP_SERVERS_FILE
        
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No MCP servers configured")
        
        # Read existing servers
        with open(config_file, 'r') as f:
            servers = json.load(f)
        
        # Find and remove server
        initial_count = len(servers)
        servers = [s for s in servers if s.get("name") != server_name]
        
        if len(servers) == initial_count:
            raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
        
        # Save updated list
        with open(config_file, 'w') as f:
            json.dump(servers, f, indent=2)
        
        return {
            "status": "success",
            "message": f"MCP server '{server_name}' deleted successfully",
            "remaining_servers": len(servers)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/mcp-servers/{server_name}")
async def update_mcp_server(server_name: str, server: MCPServerRequest):
    """Update an existing MCP server"""
    try:
        config_file = Config.ROOT_DIR / Config.MCP_SERVERS_FILE
        
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="No MCP servers configured")
        
        # Read existing servers
        with open(config_file, 'r') as f:
            servers = json.load(f)
        
        # Find and update server
        updated = False
        for i, s in enumerate(servers):
            if s.get("name") == server_name:
                servers[i] = {
                    "name": server.name,
                    "url": server.url
                }
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
        
        # Save updated list
        with open(config_file, 'w') as f:
            json.dump(servers, f, indent=2)
        
        return {
            "status": "success",
            "message": f"MCP server '{server_name}' updated successfully",
            "server": servers[i]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

