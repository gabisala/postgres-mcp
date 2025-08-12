# #!/usr/bin/env python3
# """
# Streamlit PostgreSQL Chat with OpenAI GPT-4o - FIXED VERSION
# Uses GPT-4o to intelligently interact with your database through MCP.
# """

# import streamlit as st
# import asyncio
# import json
# import os
# import sys
# from typing import Dict, Any, List
# import pandas as pd
# from datetime import datetime
# from openai import OpenAI
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Helper functions
# def _to_int_or_none(x):
#     try:
#         if x is None:
#             return None
#         # allow "1,234" or "123.0"
#         return int(float(str(x).replace(",", "")))
#     except (ValueError, TypeError):
#         return None

# def _fmt_count(x):
#     x = _to_int_or_none(x)
#     return f"{x:,}" if x is not None else "—"


# # Configure page
# st.set_page_config(
#     page_title="AI Database Assistant",
#     page_icon="🤖",
#     layout="wide"
# )

# # Initialize OpenAI client
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # IMPROVED System prompt for GPT-4o
# SYSTEM_PROMPT = """You are a helpful database assistant that directly answers questions about a PostgreSQL database.

# You have access to these MCP tools:
# 1. list_tables(schema="public") - Lists all tables
# 2. describe_table(table_name, schema="public") - Shows table structure  
# 3. read_table(table_name, schema="public", limit=100, offset=0) - Reads data from a table
# 4. search_tables(search_term, schema="public") - Searches table/column names
# 5. get_table_stats(table_name, schema="public") - Gets table statistics
# 6. execute_query(query, limit=100) - Executes SELECT queries

# **IMPORTANT: Be direct and specific in your tool selection:**

# For questions about SPECIFIC DATA (like "Who is the manager of Sales?" or "What is the budget of Engineering?"):
# - Use execute_query() with a targeted SELECT query
# - Example: execute_query({"query": "SELECT manager FROM departments WHERE name = 'Sales'"})

# For questions about TABLE CONTENTS (like "Show me all departments" or "List all servers"):
# - Use read_table() to get the actual data
# - Example: read_table({"table_name": "departments"})

# For questions about TABLE STRUCTURE (like "What columns are in departments table?"):
# - Use describe_table() to show columns and types

# For questions about WHAT TABLES EXIST (like "What tables do I have?"):
# - Use list_tables() to show available tables

# Only use search_tables() when you need to FIND table names by keyword, not when you already know the table name.

# **For this database, remember these key tables:**
# - departments (contains: id, name, manager, budget, location, employee_count, etc.)
# - servers (contains server infrastructure data)
# - applications (contains software applications data)  
# - incidents (contains issue tracking data)
# - relationships (contains component dependencies)

# **Response Format:**
# Respond with JSON:
# {
#     "thoughts": "Direct reasoning about the query and which specific tool to use",
#     "tools_to_call": [{"tool": "specific_tool_name", "arguments": {...}}],
#     "response_type": "text|dataframe|mixed", 
#     "user_facing_message": "Natural language explanation of what you're showing the user"
# }

# **Important Guidelines:**
# - Be direct - if someone asks for specific data, query for it directly!
# - Only SELECT queries allowed in execute_query, never UPDATE/DELETE/DROP
# - Default to "public" schema unless specified
# - Use friendly, conversational language in user_facing_message
# - Table and column names are case-sensitive (e.g., use exact names like "Information Technology" not "IT")"""


# class OpenAIMCPAssistant:
#     """Assistant that uses OpenAI GPT-4o to interact with MCP server."""
    
#     def __init__(self):
#         self.server_path = "postgres_mcp_server.py"
#         self.conversation_history = []
        
#     async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
#         """Call an MCP tool and return the result."""
#         server_params = StdioServerParameters(
#             command=sys.executable,
#             args=[self.server_path],
#             env=os.environ.copy()
#         )
        
#         try:
#             async with stdio_client(server_params) as (read, write):
#                 async with ClientSession(read, write) as session:
#                     await session.initialize()
#                     result = await session.call_tool(tool_name, arguments)
                    
#                     if result.content and len(result.content) > 0:
#                         return result.content[0].text
#                     return "No result returned"
#         except Exception as e:
#             return f"Error calling tool: {str(e)}"
    
#     def get_ai_interpretation(self, user_message: str, context: List[Dict] = None) -> Dict:
#         """Use GPT-4o to interpret the user's request."""
#         try:
#             # Build conversation with context
#             messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
#             # Add conversation history for context (last 5 messages)
#             if context:
#                 for msg in context[-5:]:
#                     if msg["role"] == "user":
#                         messages.append({"role": "user", "content": msg["content"]})
#                     elif msg["role"] == "assistant" and isinstance(msg["content"], str):
#                         messages.append({"role": "assistant", "content": msg["content"][:500]})  # Truncate long responses
            
#             # Add current message
#             messages.append({"role": "user", "content": user_message})
            
#             # Get GPT-4o response
#             response = openai_client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=messages,
#                 temperature=0.1,  # Low temperature for consistency
#                 response_format={"type": "json_object"}
#             )
            
#             # Parse JSON response
#             ai_response = json.loads(response.choices[0].message.content)
#             return ai_response
            
#         except Exception as e:
#             st.error(f"OpenAI Error: {str(e)}")
#             return {
#                 "thoughts": f"Error interpreting request: {str(e)}",
#                 "tools_to_call": [],
#                 "response_type": "text",
#                 "user_facing_message": "I encountered an error understanding your request. Please try rephrasing."
#             }
    
#     async def process_user_message(self, user_message: str, context: List[Dict] = None) -> Dict[str, Any]:
#         """Process user message using GPT-4o and execute MCP tools."""
        
#         # Get AI interpretation
#         ai_interpretation = self.get_ai_interpretation(user_message, context)
        
#         # Show AI's thinking (optional - can be hidden in production)
#         with st.expander("🤖 AI Reasoning", expanded=False):
#             st.json(ai_interpretation)
        
#         # Execute tools based on AI's decision
#         results = []
#         for tool_call in ai_interpretation.get("tools_to_call", []):
#             tool_name = tool_call["tool"]
#             arguments = tool_call["arguments"]
            
#             # Call the MCP tool
#             result = await self.call_mcp_tool(tool_name, arguments)
#             results.append({
#                 "tool": tool_name,
#                 "arguments": arguments,
#                 "result": result
#             })
        
#         # Format response based on results
#         return self.format_response(
#             ai_interpretation.get("user_facing_message", "Here's what I found:"),
#             results,
#             ai_interpretation.get("response_type", "text")
#         )
    
#     def format_response(self, message: str, results: List[Dict], response_type: str) -> Dict[str, Any]:
#         """Format the results for display."""
#         if not results:
#             return {
#                 "type": "text",
#                 "content": message
#             }
        
#         # Handle single result
#         if len(results) == 1:
#             result = results[0]
#             tool_name = result["tool"]
            
#             # Try to parse as JSON and format based on tool type
#             try:
#                 data = json.loads(result["result"])
                
#                 # Handle list_tables response
#                 if tool_name == "list_tables" and isinstance(data, dict) and "tables" in data:
#                     if data["tables"]:
#                         table_list = ", ".join(data["tables"])
#                         formatted_message = f"Your database contains {data['total_count']} tables: {table_list}"
#                     else:
#                         formatted_message = f"No tables found in schema '{data.get('schema_name', 'public')}'"
                    
#                     return {
#                         "type": "text",
#                         "content": f"{message}\n\n{formatted_message}"
#                     }
                
#                 # Handle read_table response (data with rows)
#                 elif isinstance(data, dict) and "data" in data and data["data"]:
#                     df = pd.DataFrame(data["data"])
#                     return {
#                         "type": "dataframe",
#                         "message": message,
#                         "content": df,
#                         "metadata": {
#                             "table": data.get("table"),
#                             "total_rows": data.get("total_rows"),
#                             "returned_rows": data.get("returned_rows"),
#                             "query": data.get("query")
#                         }
#                     }
                
#                 # Handle execute_query response (structured query results)
#                 elif isinstance(data, dict) and "row_count" in data and "data" in data:
#                     if data["data"]:
#                         df = pd.DataFrame(data["data"])
#                         return {
#                             "type": "dataframe", 
#                             "message": message,
#                             "content": df,
#                             "metadata": {
#                                 "query": data.get("query"),
#                                 "row_count": data.get("row_count"),
#                                 "columns": data.get("columns")
#                             }
#                         }
#                     else:
#                         return {
#                             "type": "text",
#                             "content": f"{message}\n\nQuery executed successfully but returned no results."
#                         }
                
#             except (json.JSONDecodeError, KeyError):
#                 pass
            
#             # Return raw result as text (for describe_table, get_table_stats, search_tables)
#             return {
#                 "type": "text",
#                 "content": f"{message}\n\n{result['result']}"
#             }
        
#         # Handle multiple results
#         formatted_content = message + "\n\n"
#         dataframes = []
        
#         for result in results:
#             formatted_content += f"**{result['tool']}**\n"
            
#             # Try to parse as JSON
#             try:
#                 data = json.loads(result["result"])
#                 if isinstance(data, dict) and "data" in data and data["data"]:
#                     df = pd.DataFrame(data["data"])
#                     dataframes.append({
#                         "df": df,
#                         "metadata": {
#                             "tool": result["tool"],
#                             "table": data.get("table"),
#                             "total_rows": data.get("total_rows")
#                         }
#                     })
#                 else:
#                     formatted_content += f"{result['result']}\n\n"
#             except:
#                 formatted_content += f"{result['result']}\n\n"
        
#         if dataframes:
#             return {
#                 "type": "mixed",
#                 "content": formatted_content,
#                 "dataframes": dataframes
#             }
        
#         return {
#             "type": "text",
#             "content": formatted_content
#         }


# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": """👋 Hello! I'm your AI-powered database assistant using GPT-4o."""
#     })

# if "assistant" not in st.session_state:
#     st.session_state.assistant = OpenAIMCPAssistant()


# # Main UI
# st.title("🤖 AI Database Assistant")
# st.caption("Powered by OpenAI GPT-4o and PostgreSQL MCP Server")

# # Sidebar
# with st.sidebar:
#     st.header("⚙️ Configuration")
    
#     # API Key check
#     api_key = os.getenv("OPENAI_API_KEY")
#     if api_key:
#         st.success("✅ OpenAI API Key configured")
#     else:
#         api_key = st.text_input("OpenAI API Key", type="password")
#         if api_key:
#             os.environ["OPENAI_API_KEY"] = api_key
#             openai_client.api_key = api_key
#             st.rerun()
    
#     # Database info
#     st.divider()
#     st.header("🗄️ Database Info")
#     st.info(f"""
#     **PostgreSQL Connection:**
#     - Host: {os.getenv('PGHOST', 'localhost')}
#     - Port: {os.getenv('PGPORT', '5432')}
#     - Database: {os.getenv('PGDATABASE', 'Not configured')}
#     - User: {os.getenv('PGUSER', 'Not configured')}
#     """)
    
#     # Model settings
#     st.divider()
#     st.header("🧠 AI Model")
#     st.info("Using: **GPT-4o** with improved system prompt")
    
#     # Example queries
#     st.divider()
#     st.header("💡 Example Queries")
#     examples = [
#         "Who is the manager of the Sales department?",
#         "Show me all departments",
#         "What tables do I have?",
#         "What is the budget of the IT department?",
#         "How many employees are in each department?",
#         "Show me the structure of the servers table"
#     ]
    
#     for example in examples:
#         if st.button(f"→ {example}", key=f"ex_{example}"):
#             st.session_state.example = example
    
#     # Clear chat
#     if st.button("🗑️ Clear Chat", use_container_width=True):
#         st.session_state.messages = [st.session_state.messages[0]]
#         st.rerun()


# # Chat interface
# chat_container = st.container()

# # Display messages
# with chat_container:
#     for i, message in enumerate(st.session_state.messages):
#         with st.chat_message(message["role"]):
#             if isinstance(message["content"], dict):
#                 # Handle structured responses
#                 msg_type = message["content"].get("type")
                
#                 if msg_type == "dataframe":
#                     st.write(message["content"].get("message", ""))
#                     df = message["content"]["content"]
#                     metadata = message["content"].get("metadata", {})
                    
#                     if metadata:
#                         cols = st.columns(4)
#                         if "table" in metadata:
#                             cols[0].metric("Table", metadata["table"])
#                         if "total_rows" in metadata:
#                             cols[1].metric("Total Rows", f"{metadata['total_rows']:,}")
#                         if "returned_rows" in metadata:
#                             cols[2].metric("Showing", metadata["returned_rows"])
                    
#                     st.dataframe(df, use_container_width=True)
                    
#                     # Add download button with unique key
#                     csv = df.to_csv(index=False)
#                     st.download_button(
#                         "📥 Download CSV",
#                         csv,
#                         "query_results.csv",
#                         "text/csv",
#                         key=f"download_msg_{i}"
#                     )
                    
#                 elif msg_type == "mixed":
#                     st.write(message["content"]["content"])
#                     for df_info in message["content"].get("dataframes", []):
#                         st.dataframe(df_info["df"], use_container_width=True)
                        
#                 else:
#                     st.write(message["content"].get("content", ""))
#             else:
#                 st.write(message["content"])


# # Handle example query
# if "example" in st.session_state:
#     example_query = st.session_state.example
#     del st.session_state.example
    
#     # Process as user input
#     st.session_state.messages.append({"role": "user", "content": example_query})
    
#     with st.chat_message("user"):
#         st.write(example_query)
    
#     with st.chat_message("assistant"):
#         with st.spinner("🤔 Thinking..."):
#             response = asyncio.run(
#                 st.session_state.assistant.process_user_message(
#                     example_query,
#                     st.session_state.messages
#                 )
#             )
            
#             if response["type"] == "dataframe":
#                 st.write(response.get("message", ""))
#                 df = response["content"]
#                 metadata = response.get("metadata", {})
                
#                 if metadata:
#                     cols = st.columns(4)
#                     if "table" in metadata:
#                         cols[0].metric("Table", metadata["table"])
#                     if "total_rows" in metadata:
#                         cols[1].metric("Total Rows", f"{metadata['total_rows']:,}")
                
#                 st.dataframe(df, use_container_width=True)
                
#                 csv = df.to_csv(index=False)
#                 st.download_button("📥 Download CSV", csv, "results.csv", "text/csv", key="download_example")
                
#             elif response["type"] == "mixed":
#                 st.write(response["content"])
#                 for df_info in response.get("dataframes", []):
#                     st.dataframe(df_info["df"], use_container_width=True)
#             else:
#                 st.write(response["content"])
            
#             st.session_state.messages.append({"role": "assistant", "content": response})
    
#     st.rerun()


# # Chat input
# if prompt := st.chat_input("Ask anything about your database..."):
#     # Check for API key
#     if not os.getenv("OPENAI_API_KEY"):
#         st.error("Please configure your OpenAI API key in the sidebar first!")
#     else:
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         with st.chat_message("user"):
#             st.write(prompt)
        
#         # Get AI response
#         with st.chat_message("assistant"):
#             with st.spinner("🤔 Thinking..."):
#                 response = asyncio.run(
#                     st.session_state.assistant.process_user_message(
#                         prompt,
#                         st.session_state.messages
#                     )
#                 )
                
#                 if response["type"] == "dataframe":
#                     st.write(response.get("message", ""))
#                     df = response["content"]
#                     metadata = response.get("metadata", {})
                    
#                     if metadata:
#                         cols = st.columns(4)
#                         if "table" in metadata:
#                             cols[0].metric("Table", metadata["table"])
#                         if "total_rows" in metadata:
#                             cols[1].metric("Total Rows", f"{metadata['total_rows']:,}")
#                         if "returned_rows" in metadata:
#                             cols[3].metric("Showing", metadata["returned_rows"])
                    
#                     st.dataframe(df, use_container_width=True)
                    
#                     csv = df.to_csv(index=False)
#                     st.download_button("📥 Download CSV", csv, "results.csv", "text/csv", key="download_prompt")
                    
#                 elif response["type"] == "mixed":
#                     st.write(response["content"])
#                     for df_info in response.get("dataframes", []):
#                         st.dataframe(df_info["df"], use_container_width=True)
#                 else:
#                     st.write(response["content"])
                
#                 st.session_state.messages.append({"role": "assistant", "content": response})
        
#         st.rerun()



#!/usr/bin/env python3
"""
Streamlit PostgreSQL Chat with OpenAI GPT-4o - FIXED VERSION
Uses GPT-4o to intelligently interact with your database through MCP.
"""

import streamlit as st
import asyncio
import json
import os
import sys
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# ----------------------------------
# Helpers for safe numeric formatting
# ----------------------------------
def _to_int_or_none(x):
    try:
        if x is None:
            return None
        # allow "1,234" or "123.0"
        return int(float(str(x).replace(",", "")))
    except (ValueError, TypeError):
        return None

def _fmt_count(x):
    x = _to_int_or_none(x)
    return f"{x:,}" if x is not None else "—"

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# IMPROVED System prompt for GPT-4o
SYSTEM_PROMPT = """You are a helpful database assistant that directly answers questions about a PostgreSQL database.

You have access to these MCP tools:
1. list_tables(schema="public") - Lists all tables
2. describe_table(table_name, schema="public") - Shows table structure  
3. read_table(table_name, schema="public", limit=100, offset=0) - Reads data from a table
4. search_tables(search_term, schema="public") - Searches table/column names
5. get_table_stats(table_name, schema="public") - Gets table statistics
6. execute_query(query, limit=100) - Executes SELECT queries

**IMPORTANT: Be direct and specific in your tool selection:**

For questions about SPECIFIC DATA (like "Who is the manager of Sales?" or "What is the budget of Engineering?"):
- Use execute_query() with a targeted SELECT query
- Example: execute_query({"query": "SELECT manager FROM departments WHERE name = 'Sales'"})

For questions about TABLE CONTENTS (like "Show me all departments" or "List all servers"):
- Use read_table() to get the actual data
- Example: read_table({"table_name": "departments"})

For questions about TABLE STRUCTURE (like "What columns are in departments table?"):
- Use describe_table() to show columns and types

For questions about WHAT TABLES EXIST (like "What tables do I have?"):
- Use list_tables() to show available tables

Only use search_tables() when you need to FIND table names by keyword, not when you already know the table name.

**For this database, remember these key tables:**
- departments (contains: id, name, manager, budget, location, employee_count, etc.)
- servers (contains server infrastructure data)
- applications (contains software applications data)  
- incidents (contains issue tracking data)
- relationships (contains component dependencies)

**Response Format:**
Respond with JSON:
{
    "thoughts": "Direct reasoning about the query and which specific tool to use",
    "tools_to_call": [{"tool": "specific_tool_name", "arguments": {...}}],
    "response_type": "text|dataframe|mixed", 
    "user_facing_message": "Natural language explanation of what you're showing the user"
}

**Important Guidelines:**
- Be direct - if someone asks for specific data, query for it directly!
- Only SELECT queries allowed in execute_query, never UPDATE/DELETE/DROP
- Default to "public" schema unless specified
- Use friendly, conversational language in user_facing_message
- Table and column names are case-sensitive (e.g., use exact names like "Information Technology" not "IT")"""


class OpenAIMCPAssistant:
    """Assistant that uses OpenAI GPT-4o to interact with MCP server."""
    
    def __init__(self):
        self.server_path = "postgres_mcp_server.py"
        self.conversation_history = []
        
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP tool and return the result."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_path],
            env=os.environ.copy()
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    
                    if result.content and len(result.content) > 0:
                        return result.content[0].text
                    return "No result returned"
        except Exception as e:
            return f"Error calling tool: {str(e)}"
    
    def get_ai_interpretation(self, user_message: str, context: List[Dict] = None) -> Dict:
        """Use GPT-4o to interpret the user's request."""
        try:
            # Build conversation with context
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add conversation history for context (last 5 messages)
            if context:
                for msg in context[-5:]:
                    if msg["role"] == "user":
                        messages.append({"role": "user", "content": msg["content"]})
                    elif msg["role"] == "assistant" and isinstance(msg["content"], str):
                        messages.append({"role": "assistant", "content": msg["content"][:500]})  # Truncate long responses
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            # Get GPT-4o response
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            ai_response = json.loads(response.choices[0].message.content)
            return ai_response
            
        except Exception as e:
            st.error(f"OpenAI Error: {str(e)}")
            return {
                "thoughts": f"Error interpreting request: {str(e)}",
                "tools_to_call": [],
                "response_type": "text",
                "user_facing_message": "I encountered an error understanding your request. Please try rephrasing."
            }
    
    async def process_user_message(self, user_message: str, context: List[Dict] = None) -> Dict[str, Any]:
        """Process user message using GPT-4o and execute MCP tools."""
        
        # Get AI interpretation
        ai_interpretation = self.get_ai_interpretation(user_message, context)
        
        # Show AI's thinking (optional - can be hidden in production)
        with st.expander("🤖 AI Reasoning", expanded=False):
            st.json(ai_interpretation)
        
        # Execute tools based on AI's decision
        results = []
        for tool_call in ai_interpretation.get("tools_to_call", []):
            tool_name = tool_call["tool"]
            arguments = tool_call["arguments"]
            
            # Call the MCP tool
            result = await self.call_mcp_tool(tool_name, arguments)
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result
            })
        
        # Format response based on results
        return self.format_response(
            ai_interpretation.get("user_facing_message", "Here's what I found:"),
            results,
            ai_interpretation.get("response_type", "text")
        )
    
    def format_response(self, message: str, results: List[Dict], response_type: str) -> Dict[str, Any]:
        """Format the results for display."""
        if not results:
            return {
                "type": "text",
                "content": message
            }
        
        # Handle single result
        if len(results) == 1:
            result = results[0]
            tool_name = result["tool"]
            
            # Try to parse as JSON and format based on tool type
            try:
                data = json.loads(result["result"])
                
                # Handle list_tables response
                if tool_name == "list_tables" and isinstance(data, dict) and "tables" in data:
                    if data["tables"]:
                        total_count = _to_int_or_none(data.get("total_count"))
                        table_list = ", ".join(data["tables"])
                        if total_count is not None:
                            formatted_message = f"Your database contains {total_count:,} tables: {table_list}"
                        else:
                            formatted_message = f"Your database tables: {table_list}"
                    else:
                        formatted_message = f"No tables found in schema '{data.get('schema_name', 'public')}'"
                    
                    return {
                        "type": "text",
                        "content": f"{message}\n\n{formatted_message}"
                    }
                
                # Handle read_table response (data with rows)
                elif isinstance(data, dict) and "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    returned_rows = data.get("returned_rows")
                    if returned_rows is None:
                        returned_rows = len(df)  # fallback

                    return {
                        "type": "dataframe",
                        "message": message,
                        "content": df,
                        "metadata": {
                            "table": data.get("table"),
                            "total_rows": _to_int_or_none(data.get("total_rows")),
                            "returned_rows": _to_int_or_none(returned_rows),
                            "query": data.get("query")
                        }
                    }
                
                # Handle execute_query response (structured query results)
                elif isinstance(data, dict) and "row_count" in data and "data" in data:
                    df = pd.DataFrame(data["data"]) if data["data"] else pd.DataFrame()
                    return {
                        "type": "dataframe", 
                        "message": message if not df.empty else f"{message}\n\nQuery executed successfully but returned no results.",
                        "content": df,
                        "metadata": {
                            "query": data.get("query"),
                            "row_count": _to_int_or_none(data.get("row_count")),
                            "returned_rows": _to_int_or_none(len(df)),
                            "columns": data.get("columns")
                        }
                    }
                
            except (json.JSONDecodeError, KeyError):
                pass
            
            # Return raw result as text (for describe_table, get_table_stats, search_tables)
            return {
                "type": "text",
                "content": f"{message}\n\n{result['result']}"
            }
        
        # Handle multiple results
        formatted_content = message + "\n\n"
        dataframes = []
        
        for result in results:
            formatted_content += f"**{result['tool']}**\n"
            
            # Try to parse as JSON
            try:
                data = json.loads(result["result"])
                if isinstance(data, dict) and "data" in data and data["data"]:
                    df = pd.DataFrame(data["data"])
                    dataframes.append({
                        "df": df,
                        "metadata": {
                            "tool": result["tool"],
                            "table": data.get("table"),
                            "total_rows": _to_int_or_none(data.get("total_rows"))
                        }
                    })
                else:
                    formatted_content += f"{result['result']}\n\n"
            except:
                formatted_content += f"{result['result']}\n\n"
        
        if dataframes:
            return {
                "type": "mixed",
                "content": formatted_content,
                "dataframes": dataframes
            }
        
        return {
            "type": "text",
            "content": formatted_content
        }


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 Hello! I'm your AI-powered database assistant using GPT-4o."""
    })

if "assistant" not in st.session_state:
    st.session_state.assistant = OpenAIMCPAssistant()


# Main UI
st.title("🤖 AI Database Assistant")
st.caption("Powered by OpenAI GPT-4o and PostgreSQL MCP Server")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key check
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API Key configured")
    else:
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            openai_client.api_key = api_key
            st.rerun()
    
    # Database info
    st.divider()
    st.header("🗄️ Database Info")
    st.info(f"""
    **PostgreSQL Connection:**
    - Host: {os.getenv('PGHOST', 'localhost')}
    - Port: {os.getenv('PGPORT', '5432')}
    - Database: {os.getenv('PGDATABASE', 'Not configured')}
    - User: {os.getenv('PGUSER', 'Not configured')}
    """)
    
    # Model settings
    st.divider()
    st.header("🧠 AI Model")
    st.info("Using: **GPT-4o** with improved system prompt")
    
    # Example queries
    st.divider()
    st.header("💡 Example Queries")
    examples = [
        "Who is the manager of the Sales department?",
        "Show me all departments",
        "What tables do I have?",
        "What is the budget of the IT department?",
        "How many employees are in each department?",
        "Show me the structure of the servers table"
    ]
    
    for example in examples:
        if st.button(f"→ {example}", key=f"ex_{example}"):
            st.session_state.example = example
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()


# Chat interface
chat_container = st.container()

# Display messages
with chat_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict):
                # Handle structured responses
                msg_type = message["content"].get("type")
                
                if msg_type == "dataframe":
                    st.write(message["content"].get("message", ""))
                    df = message["content"]["content"]
                    metadata = message["content"].get("metadata", {})
                    
                    if metadata:
                        cols = st.columns(4)
                        if "table" in metadata:
                            cols[0].metric("Table", metadata["table"])
                        if "total_rows" in metadata:
                            cols[1].metric("Total Rows", _fmt_count(metadata.get("total_rows")))
                        rows_shown = metadata.get("returned_rows") or metadata.get("row_count")
                        if rows_shown is not None:
                            cols[2].metric("Rows", _fmt_count(rows_shown))

                    with st.expander("Debug: metadata", expanded=False):
                        st.json(metadata)
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Add download button with unique key
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "query_results.csv",
                        "text/csv",
                        key=f"download_msg_{i}"
                    )
                    
                elif msg_type == "mixed":
                    st.write(message["content"]["content"])
                    for df_info in message["content"].get("dataframes", []):
                        st.dataframe(df_info["df"], use_container_width=True)
                        
                else:
                    st.write(message["content"].get("content", ""))
            else:
                st.write(message["content"])


# Handle example query
if "example" in st.session_state:
    example_query = st.session_state.example
    del st.session_state.example
    
    # Process as user input
    st.session_state.messages.append({"role": "user", "content": example_query})
    
    with st.chat_message("user"):
        st.write(example_query)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = asyncio.run(
                st.session_state.assistant.process_user_message(
                    example_query,
                    st.session_state.messages
                )
            )
            
            if response["type"] == "dataframe":
                st.write(response.get("message", ""))
                df = response["content"]
                metadata = response.get("metadata", {})
                
                if metadata:
                    cols = st.columns(4)
                    if "table" in metadata:
                        cols[0].metric("Table", metadata["table"])
                    if "total_rows" in metadata:
                        cols[1].metric("Total Rows", _fmt_count(metadata.get("total_rows")))
                    rows_shown = metadata.get("returned_rows") or metadata.get("row_count")
                    if rows_shown is not None:
                        cols[2].metric("Rows", _fmt_count(rows_shown))

                with st.expander("Debug: metadata", expanded=False):
                    st.json(metadata)
                
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "results.csv", "text/csv", key="download_example")
                
            elif response["type"] == "mixed":
                st.write(response["content"])
                for df_info in response.get("dataframes", []):
                    st.dataframe(df_info["df"], use_container_width=True)
            else:
                st.write(response["content"])
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()


# Chat input
if prompt := st.chat_input("Ask anything about your database..."):
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Please configure your OpenAI API key in the sidebar first!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = asyncio.run(
                    st.session_state.assistant.process_user_message(
                        prompt,
                        st.session_state.messages
                    )
                )
                
                if response["type"] == "dataframe":
                    st.write(response.get("message", ""))
                    df = response["content"]
                    metadata = response.get("metadata", {})
                    
                    if metadata:
                        cols = st.columns(4)
                        if "table" in metadata:
                            cols[0].metric("Table", metadata["table"])
                        if "total_rows" in metadata:
                            cols[1].metric("Total Rows", _fmt_count(metadata.get("total_rows")))
                        rows_shown = metadata.get("returned_rows") or metadata.get("row_count")
                        if rows_shown is not None:
                            cols[2].metric("Rows", _fmt_count(rows_shown))

                    with st.expander("Debug: metadata", expanded=False):
                        st.json(metadata)
                    
                    st.dataframe(df, use_container_width=True)
                    
                    csv = df.to_csv(index=False)
                    st.download_button("📥 Download CSV", csv, "results.csv", "text/csv", key="download_prompt")
                    
                elif response["type"] == "mixed":
                    st.write(response["content"])
                    for df_info in response.get("dataframes", []):
                        st.dataframe(df_info["df"], use_container_width=True)
                else:
                    st.write(response["content"])
                
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
