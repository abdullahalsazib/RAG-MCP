"""
Configuration and environment management
"""
import os
import json
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available, using environment variables directly")


class Config:
    """Application configuration"""
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # MCP settings
    MCP_SERVERS_FILE = "mcp_servers.json"
    MCP_SERVERS_ENV = os.getenv("MCP_SERVERS")
    
    # Project root
    ROOT_DIR = Path(__file__).parent.parent
    
    @classmethod
    def load_mcp_servers(cls, additional_servers: list = None) -> list[dict]:
        """
        Load MCP servers from multiple sources:
        1. Environment variable MCP_SERVERS (JSON array)
        2. Config file mcp_servers.json
        3. Additional servers passed as argument
        """
        servers = []
        
        # Method 1: From environment variable
        if cls.MCP_SERVERS_ENV:
            try:
                env_servers = json.loads(cls.MCP_SERVERS_ENV)
                servers.extend(env_servers)
                print(f"📝 Loaded {len(env_servers)} server(s) from MCP_SERVERS env variable")
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse MCP_SERVERS env variable: {e}")
        
        # Method 2: From config file
        config_file = cls.ROOT_DIR / cls.MCP_SERVERS_FILE
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_servers = json.load(f)
                    servers.extend(file_servers)
                    print(f"📝 Loaded {len(file_servers)} server(s) from {cls.MCP_SERVERS_FILE}")
            except Exception as e:
                print(f"⚠️  Failed to load {cls.MCP_SERVERS_FILE}: {e}")
        
        # Method 3: No servers configured
        if not servers:
            print("📝 No MCP servers configured - agent will use local tools only")
        
        # Add any additional servers passed as argument
        if additional_servers:
            servers.extend(additional_servers)
            print(f"📝 Added {len(additional_servers)} additional server(s)")
        
        return servers

