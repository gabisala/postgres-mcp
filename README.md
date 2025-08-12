# PostgreSQL MCP Server

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.12.4-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A **Model Context Protocol (MCP)** server that enables AI assistants to interact with PostgreSQL databases through a standardized interface. Built with the official MCP Python SDK and designed for both local development and Azure Database for PostgreSQL deployments.

## 🚀 Features

- **🔒 Read-Only by Design**: Only SELECT operations allowed for security
- **📊 Rich Database Tools**: 6 comprehensive database interaction tools
- **🏗️ Structured Data**: Pydantic models for type-safe, validated responses  
- **🤖 AI-Optimized**: Built specifically for LLM integration via MCP
- **☁️ Azure Ready**: Designed for Azure Database for PostgreSQL
- **⚡ High Performance**: Connection pooling with asyncpg
- **🛡️ Security First**: SQL injection protection and query validation

## 🛠️ Available Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `list_tables` | List all tables in a schema | Structured table list |
| `describe_table` | Get table schema and constraints | Table definition details |
| `read_table` | Read table contents with pagination | Structured table data |
| `execute_query` | Execute SELECT queries safely | Query results |
| `get_table_stats` | Get table statistics and size info | Table analytics |
| `search_tables` | Search tables and columns by term | Matching results |

## 📋 Requirements

- **Python 3.12+**
- **PostgreSQL 12+** (local or Azure Database)
- **OpenAI API Key** (for the chat interface)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/gabisala/postgres-mcp.git
cd postgres-mcp

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.template .env

# Edit configuration
nano .env
```

Add your configuration:
```env
# PostgreSQL Connection
PGHOST=localhost
PGPORT=5432
PGDATABASE=your_database
PGUSER=your_username
PGPASSWORD=your_password

# Alternative: Use connection URL
# DATABASE_URL=postgresql://user:password@host:port/database

# OpenAI API (for chat interface)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
```

### 3. Setup Database (Optional)

For testing, set up the included CMDB (Configuration Management Database):

```bash
# Setup PostgreSQL and sample data (WSL2/Ubuntu)
chmod +x setup_postgresql_wsl.sh
./setup_postgresql_wsl.sh

# Verify everything is working
uv run python verify_setup.py
```

### 4. Run the Applications

**Start the MCP Server:**
```bash
uv run python postgres_mcp_server.py
```

**Launch the Chat Interface:**
```bash
uv run streamlit run streamlit_openai_mcp.py
```

Visit `http://localhost:8501` to interact with your database through AI!

## 📁 Project Structure

```
postgres-mcp/
├── 📄 postgres_mcp_server.py      # MCP server implementation
├── 🌐 streamlit_openai_mcp.py     # Web chat interface
├── ⚙️ .env.template               # Configuration template
├── 🧪 test_mcp_compatibility.py   # MCP functionality tests
├── 📊 create_cmdb_database.sql    # Sample database schema
├── 📝 insert_sample_data.sql      # Sample data
├── ✅ verify_setup.py             # Setup verification
├── 📚 documentation/              # Detailed documentation
│   ├── ARCHITECTURE.md
│   ├── DB_SCHEMA.md  
│   ├── MCP_SERVER.md
│   ├── MCP_CLIENT.md
│   ├── SECURITY.md
│   └── RUNBOOK.md
├── 📋 CLAUDE.md                   # Development guidelines
├── 📈 PLAN.md                     # Implementation roadmap
└── ✔️ TASKS.md                    # Progress tracking
```

## 🔧 Usage Examples

### Using the MCP Server Directly

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to the MCP server
server_params = StdioServerParameters(
    command="python", 
    args=["postgres_mcp_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # List all tables
        result = await session.call_tool("list_tables", {})
        print(result.content[0].text)
        
        # Read table data
        result = await session.call_tool("read_table", {
            "table_name": "employees",
            "limit": 10
        })
        print(result.content[0].text)
```

### Chat Interface Examples

Try these queries in the Streamlit interface:

- *"What tables are available in the database?"*
- *"Show me the structure of the employees table"*
- *"Find all servers in the production environment"*
- *"What are the latest incidents in the system?"*
- *"Show me department budget information"*

## 🏗️ Architecture

### MCP Server (`postgres_mcp_server.py`)
- **Framework**: Official MCP Python SDK with FastMCP
- **Database Driver**: asyncpg for high-performance PostgreSQL access
- **Security**: READ-ONLY operations, SQL injection protection
- **Data Models**: Pydantic models for structured responses
- **Connection Management**: Async connection pooling

### Chat Interface (`streamlit_openai_mcp.py`)  
- **Frontend**: Streamlit web application
- **AI Model**: OpenAI GPT-4o for natural language processing
- **MCP Integration**: Seamless tool calling via stdio transport
- **Features**: Conversation history, example queries, data visualization

### Sample Database (CMDB)
- **Purpose**: Enterprise Configuration Management Database
- **Entities**: Departments, Servers, Applications, Incidents, Relationships
- **Size**: ~90 sample records across 6 tables
- **Use Cases**: IT infrastructure management, incident tracking

## 🔒 Security Features

- **Read-Only Enforcement**: Only SELECT queries allowed
- **SQL Injection Protection**: Parameterized queries and keyword filtering
- **Connection Security**: Support for SSL/TLS connections
- **Query Timeouts**: 30-second execution limits
- **Error Handling**: Safe error messages without information leakage

## ☁️ Azure Database Support

**Ready for Azure Database for PostgreSQL:**

```env
# Azure connection example
DATABASE_URL=postgresql://username@servername:password@servername.postgres.database.azure.com:5432/database?sslmode=require

# Or individual components
PGHOST=servername.postgres.database.azure.com
PGPORT=5432
PGDATABASE=your_database
PGUSER=username@servername
PGPASSWORD=your_password
PGSSLMODE=require
```

**Upcoming Azure features:**
- Azure AD authentication
- Managed Identity support
- Connection string parsing
- Environment profiles (dev/staging/prod)

## 🧪 Testing

**Verify Installation:**
```bash
uv run python verify_setup.py
```

**Test MCP Functionality:**
```bash
uv run python test_mcp_compatibility.py
```

**Test Structured Schemas:**
```bash
uv run python test_structured_schemas.py
```

## 📚 Documentation

Comprehensive documentation available in the `documentation/` folder:

- **[Architecture Guide](documentation/ARCHITECTURE.md)** - System design and components
- **[Database Schema](documentation/DB_SCHEMA.md)** - CMDB structure and relationships  
- **[MCP Server Guide](documentation/MCP_SERVER.md)** - Server implementation details
- **[Client Integration](documentation/MCP_CLIENT.md)** - Using the Streamlit client
- **[Security Model](documentation/SECURITY.md)** - Security features and best practices
- **[Operations Runbook](documentation/RUNBOOK.md)** - Deployment and maintenance

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)  
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Model Context Protocol](https://modelcontextprotocol.io)** - For the standardized AI-tool integration protocol
- **[OpenAI](https://openai.com)** - For GPT-4o and the AI capabilities
- **[Streamlit](https://streamlit.io)** - For the excellent web framework
- **[asyncpg](https://magicstack.github.io/asyncpg/)** - For high-performance PostgreSQL connectivity

---

**Built with ❤️ for the AI and database community**

[![Star on GitHub](https://img.shields.io/github/stars/gabisala/postgres-mcp?style=social)](https://github.com/gabisala/postgres-mcp)