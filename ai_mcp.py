from dotenv import load_dotenv
load_dotenv()
import asyncio
from typing import List

# LangChain imports
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

# MCP imports
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools

# --- 1. Define Tools ---

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
        """
        Retrieves relevant context about DosiBlog projects.
        """
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
                Example: [
                    {"name": "Math", "url": "https://example.com/math/mcp"},
                    {"name": "Jack", "url": "https://example.com/jack/mcp", "headers": {"X-Api-Key": "key"}}
                ]
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
        # Get the last message
        last_msg = event["messages"][-1]

        # If AI message
        if isinstance(last_msg, AIMessage):
            if getattr(last_msg, "tool_calls", None):
                # AI decided to call a tool
                for call in last_msg.tool_calls:
                    tool_input = call.get('args', call.get('input', {}))
                    print(f"🤖 Agent calling tool: {call['name']}")
                    print(f"   Input: {tool_input}")
            else:
                # AI final answer
                print(f"\n✅ Final Answer: {last_msg.content}\n")
                final_answer = last_msg.content
        
        # If Tool message
        elif hasattr(last_msg, "tool_name"):
            print(f"🔧 Tool '{last_msg.tool_name}' output: {last_msg.content}")

    return final_answer

# --- 4. Main Function ---

async def main():
    """Main function to set up and run the agent"""
    
    print("\n" + "="*60)
    print("🚀 Initializing AI Agent with MCP Tools")
    print("="*60 + "\n")
    
    # Define MCP servers as an array - easily add or remove servers!
    mcp_servers = [
        {
            "name": "Jack",
            "url": "https://mcp-test-kset.onrender.com/jack/mcp",
        },
        # Add more servers here as needed:
        # {
        #     "name": "Finance",
        #     "url": "https://mcp-finance-agent.xxx.us.langgraph.app/mcp",
        #     "headers": {"X-Api-Key": "lsv2_pt_your_api_key"}
        # },
    ]
    
    # Use context manager to keep MCP sessions alive
    async with MCPClientManager(mcp_servers) as mcp_tools:
        
        # Combine with local DosiBlog RAG tool
        all_tools = [retrieve_dosiblog_context] + mcp_tools
        
        print(f"\n📦 Total tools available: {len(all_tools)}")
        print("   Local tools: DosiBlog RAG")
        print(f"   Remote MCP tools: {len(mcp_tools)}")
        
        # Create the agent with all tools
        print("\n🔧 Creating agent with GPT-4o...")
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        agent_executor = create_agent(llm, all_tools)
        print("✓ Agent created successfully!")
        
        # Run example queries
        await run_query(agent_executor, "add 5 and 3 and multiply by 2 the again add 8 and divide by 4 and say hello to jack? and what is dosiblog? and my name is abdullah")
        await run_query(agent_executor, "what is my name? ")

if __name__ == "__main__":
    asyncio.run(main())
