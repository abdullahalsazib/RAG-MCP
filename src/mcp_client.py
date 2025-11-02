"""
MCP (Model Context Protocol) client management
"""
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools


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
            api_key = server_config.get("api_key")
            
            # Handle API key in URL (e.g., Firecrawl: https://mcp.firecrawl.dev/<your_api_key>/sse)
            # Check for common placeholder patterns in URL
            final_url = server_url
            url_has_placeholder = False
            if api_key:
                # Common placeholder patterns: <your_api_key>, {api_key}, {YOUR_API_KEY}, <api_key>, etc.
                import re
                placeholder_patterns = [
                    r'<your_api_key>',
                    r'<api_key>',
                    r'<YOUR_API_KEY>',
                    r'<API_KEY>',
                    r'\{api_key\}',
                    r'\{YOUR_API_KEY\}',
                    r'\{API_KEY\}',
                    r'\{your_api_key\}',
                ]
                
                for pattern in placeholder_patterns:
                    if re.search(pattern, final_url, re.IGNORECASE):
                        final_url = re.sub(pattern, api_key, final_url, flags=re.IGNORECASE)
                        url_has_placeholder = True
                        print(f"  ℹ️  API key embedded in URL (placeholder replaced)")
                        break
            
            print(f"Loading tools from {server_name} MCP server ({final_url})...")
            
            try:
                # Prepare server params
                server_params = {"url": final_url}
                
                # Build headers: start with existing headers
                headers = dict(server_headers) if server_headers else {}
                
                # Add API key to headers ONLY if not embedded in URL
                # Some servers (like Firecrawl) use URL embedding, others use headers
                if api_key and not url_has_placeholder:
                    # Try common header patterns - prioritize Authorization Bearer
                    if "Authorization" not in headers:
                        headers["Authorization"] = f"Bearer {api_key}"
                    elif "X-API-Key" not in headers:
                        headers["X-API-Key"] = api_key
                
                if headers:
                    server_params["headers"] = headers
                
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
                # Close session first
                if session:
                    try:
                        await session.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        if "cancel scope" not in str(e).lower():
                            print(f"Error closing session: {e}")
                # Then close client
                if client:
                    try:
                        await client.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        if "cancel scope" not in str(e).lower():
                            print(f"Error closing client: {e}")
            except Exception as e:
                # Ignore cancel scope errors - these are common during cleanup
                if "cancel scope" not in str(e).lower():
                    print(f"Error during cleanup: {e}")
        print("✓ All MCP sessions closed")

