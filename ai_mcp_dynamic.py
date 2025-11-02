"""
Dynamic MCP Agent - Pass MCP server URLs as arguments
Usage examples:
    python ai_mcp_dynamic.py
    python ai_mcp_dynamic.py --add-server '{"name":"MyServer","url":"https://example.com/mcp"}'
"""
from dotenv import load_dotenv
load_dotenv()
import asyncio
import json
import os
import argparse

# LangChain imports
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent

# MCP imports
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools

# --- 1. Define Local Tools ---

# Tool 1: RAG tool for DosiBlog context
texts = [
    "DosiBlog is a web development project created by Abdullah Al Sazib.",
    "DosiBlog uses Node.js, Express, and MongoDB.",
    "The DosiBlog project was started in September 2025."
]

try:
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    @tool("retrieve_dosiblog_context")
    def retrieve_dosiblog_context(query: str) -> str:
        """Retrieves relevant context about DosiBlog projects."""
        print(f"--- Calling RAG Tool for query: {query} ---")
        docs = retriever.invoke(query)
        if docs:
            return f"Retrieved context: {docs[0].page_content}"
        return "No relevant context found for DosiBlog."

except Exception as e:
    print(f"FAISS not available, RAG tool disabled: {e}")
    @tool("retrieve_dosiblog_context")
    def retrieve_dosiblog_context(query: str) -> str:
        return "RAG tool not available."

# --- 2. MCP Client Context Manager ---

class MCPClientManager:
    """Context manager to maintain MCP sessions"""
    def __init__(self, mcp_servers: list[dict]):
        """
        Initialize with a list of MCP server configurations
        
        Args:
            mcp_servers: List of server configs, each with 'name', 'url', and optional 'headers'
        """
        self.mcp_servers = mcp_servers
        self.sessions = []
        self.tools = []
        
    async def __aenter__(self):
        """Load tools from all configured MCP servers and keep sessions alive"""
        
        for server_config in self.mcp_servers:
            server_name = server_config.get("name", "Unknown")
            server_url = server_config["url"]
            server_headers = server_config.get("headers", {})
            
            print(f"Loading tools from {server_name} MCP server ({server_url})...")
            
            try:
                # Prepare server params
                server_params = {"url": server_url}
                if server_headers:
                    server_params["headers"] = server_headers
                
                # Connect to server
                client = streamablehttp_client(**server_params)
                read, write, _ = await client.__aenter__()
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()
                
                # Load tools
                tools = await load_mcp_tools(session)
                self.tools.extend(tools)
                self.sessions.append((client, session))
                
                print(f"✓ Loaded {len(tools)} tool(s) from {server_name} MCP server")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
            except Exception as e:
                print(f"✗ Failed to load {server_name} MCP tools: {e}")
            
            print()  # Empty line between servers
        
        return self.tools
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up all sessions"""
        print("\n🔄 Closing MCP sessions...")
        for client, session in reversed(self.sessions):
            try:
                await session.__aexit__(None, None, None)
                await client.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error closing session: {e}")
        print("✓ All MCP sessions closed")

# --- 3. Run Query Function ---

async def run_query(agent_executor, question: str):
    """Run a query through the agent"""
    print(f"\n{'='*60}")
    print(f"User Query: {question}")
    print(f"{'='*60}\n")
    
    inputs = {"messages": [HumanMessage(content=question)]}

    final_answer = ""
    async for event in agent_executor.astream(inputs, stream_mode="values"):
        last_msg = event["messages"][-1]

        if isinstance(last_msg, AIMessage):
            if getattr(last_msg, "tool_calls", None):
                for call in last_msg.tool_calls:
                    tool_input = call.get('args', call.get('input', {}))
                    print(f"🤖 Agent calling tool: {call['name']}")
                    print(f"   Input: {tool_input}")
            else:
                print(f"\n✅ Final Answer: {last_msg.content}\n")
                final_answer = last_msg.content
        
        elif hasattr(last_msg, "tool_name"):
            print(f"🔧 Tool '{last_msg.tool_name}' output: {last_msg.content}")

    return final_answer

# --- 4. Load MCP Servers Configuration ---

def load_mcp_servers_config(additional_servers: list = None) -> list[dict]:
    """
    Load MCP servers from multiple sources:
    1. Environment variable MCP_SERVERS (JSON array)
    2. Config file mcp_servers.json
    3. Additional servers passed as argument
    """
    servers = []
    
    # Method 1: From environment variable
    env_servers = os.getenv("MCP_SERVERS")
    if env_servers:
        try:
            servers.extend(json.loads(env_servers))
            print(f"📝 Loaded {len(json.loads(env_servers))} server(s) from MCP_SERVERS env variable")
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse MCP_SERVERS env variable: {e}")
    
    # Method 2: From config file
    config_file = "mcp_servers.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_servers = json.load(f)
                servers.extend(file_servers)
                print(f"📝 Loaded {len(file_servers)} server(s) from {config_file}")
        except Exception as e:
            print(f"⚠️  Failed to load {config_file}: {e}")
    
    # Method 3: Default servers if none loaded
    if not servers:
        servers = [ {} ]
        print("📝 Using default server configuration")
    
    # Add any additional servers passed as argument
    if additional_servers:
        servers.extend(additional_servers)
        print(f"📝 Added {len(additional_servers)} additional server(s)")
    
    return servers

# --- 5. Main Function ---

async def main(query: str = None, additional_servers: list = None):
    """Main function to set up and run the agent"""
    
    print("\n" + "="*60)
    print("🚀 Initializing AI Agent with Dynamic MCP Tools")
    print("="*60 + "\n")
    
    # Load MCP servers configuration
    mcp_servers = load_mcp_servers_config(additional_servers)
    
    print(f"\n📡 Connecting to {len(mcp_servers)} MCP server(s)...\n")
    
    # Use context manager to keep MCP sessions alive
    async with MCPClientManager(mcp_servers) as mcp_tools:
        
        # Combine with local DosiBlog RAG tool
        all_tools = [retrieve_dosiblog_context] + mcp_tools
        
        print(f"\n📦 Total tools available: {len(all_tools)}")
        print(f"   • Local tools: 1 (DosiBlog RAG)")
        print(f"   • Remote MCP tools: {len(mcp_tools)}")
        
        # Create the agent with all tools
        print("\n🔧 Creating agent with GPT-4o...")
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        agent_executor = create_agent(llm, all_tools)
        print("✓ Agent created successfully!")
        
        # Run queries
        if query:
            await run_query(agent_executor, query)
        else:
            # Default example queries
             await run_query(agent_executor, "add 5 and 3 and multiply by 2 the again add 8 and divide by 4 and say hello to jack? and what is dosiblog? and my name is abdullah")
             await run_query(agent_executor, "what is my name? ")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Agent with Dynamic MCP Tools')
    parser.add_argument('--query', '-q', type=str, help='Query to send to the agent')
    parser.add_argument('--add-server', '-s', type=str, action='append',
                        help='Add MCP server as JSON: \'{"name":"Name","url":"https://..."}\'')
    
    args = parser.parse_args()
    
    # Parse additional servers
    additional_servers = []
    if args.add_server:
        for server_json in args.add_server:
            try:
                additional_servers.append(json.loads(server_json))
            except json.JSONDecodeError as e:
                print(f"⚠️  Invalid server JSON: {e}")
    
    asyncio.run(main(query=args.query, additional_servers=additional_servers))

