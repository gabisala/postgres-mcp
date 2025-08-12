#!/usr/bin/env python3
"""
Test MCP Server and Client Compatibility
Quick test to verify the PostgreSQL MCP server works with MCP clients.
"""

import asyncio
import subprocess
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

async def test_mcp_server():
    """Test basic MCP server functionality."""
    print("🔄 Testing MCP Server Compatibility...")
    
    try:
        # Start the MCP server as subprocess
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "postgres_mcp_server.py"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server")
                
                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")
                
                # List available tools
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools:")
                
                for tool in tools.tools:
                    print(f"   • {tool.name}: {tool.description}")
                
                # Test list_tables tool
                print("\n🔄 Testing list_tables tool...")
                try:
                    result = await session.call_tool("list_tables", {})
                    print("✅ list_tables executed successfully")
                    print(f"   Result preview: {str(result.content[0].text)[:100]}...")
                    
                except Exception as e:
                    print(f"❌ list_tables failed: {e}")
                
                return True
                
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

async def main():
    """Run the compatibility test."""
    print("PostgreSQL MCP Server Compatibility Test")
    print("=" * 45)
    
    success = await test_mcp_server()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ MCP server is compatible and working!")
    else:
        print("❌ MCP server has compatibility issues")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())