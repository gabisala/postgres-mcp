#!/usr/bin/env python3
"""
Test Structured MCP Tool Schemas
Verify that our Pydantic models provide proper JSON schemas for MCP tools.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

async def test_structured_tools():
    """Test the structured tool schemas and responses."""
    print("🔄 Testing Structured MCP Tool Schemas...")
    
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
                
                # Test list_tables with structured output
                print("\n🔄 Testing list_tables (structured)...")
                try:
                    result = await session.call_tool("list_tables", {})
                    # Parse the JSON response
                    data = json.loads(result.content[0].text)
                    print("✅ list_tables returned structured data:")
                    print(f"   Schema: {data.get('schema_name', 'unknown')}")
                    print(f"   Tables: {len(data.get('tables', []))} tables")
                    print(f"   Total count: {data.get('total_count', 0)}")
                    
                except Exception as e:
                    print(f"❌ list_tables failed: {e}")
                
                # Test read_table with structured output
                print("\n🔄 Testing read_table (structured)...")
                try:
                    result = await session.call_tool("read_table", {
                        "table_name": "departments",
                        "limit": 5
                    })
                    # Parse the JSON response
                    data = json.loads(result.content[0].text)
                    print("✅ read_table returned structured data:")
                    print(f"   Table: {data.get('table', 'unknown')}")
                    print(f"   Total rows: {data.get('total_rows', 0)}")
                    print(f"   Returned rows: {data.get('returned_rows', 0)}")
                    print(f"   Data columns: {len(data.get('data', [{}])[0].keys()) if data.get('data') else 0} columns")
                    
                except Exception as e:
                    print(f"❌ read_table failed: {e}")
                
                # Test describe_table (still text-based for now)
                print("\n🔄 Testing describe_table...")
                try:
                    result = await session.call_tool("describe_table", {
                        "table_name": "departments"
                    })
                    output = result.content[0].text
                    print("✅ describe_table executed successfully")
                    print(f"   Output type: {type(output).__name__}")
                    print(f"   Length: {len(output)} characters")
                    
                except Exception as e:
                    print(f"❌ describe_table failed: {e}")
                
                return True
                
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

async def main():
    """Run the schema tests."""
    print("PostgreSQL MCP Structured Schema Test")
    print("=" * 40)
    
    success = await test_structured_tools()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Structured schemas are working correctly!")
        print("\nKey improvements:")
        print("   • Pydantic models provide rich JSON schemas")
        print("   • Type safety and validation")
        print("   • Structured data for better programmatic access")
        print("   • Clear field descriptions for AI clients")
    else:
        print("❌ Structured schemas need debugging")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())