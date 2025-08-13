# PostgreSQL MCP Server

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.12.4-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A **Model Context Protocol (MCP)** server that enables AI assistants to interact with PostgreSQL databases through a standardized interface. Built with the official MCP Python SDK and designed for both local development and external database deployments (including Azure Database for PostgreSQL, AWS RDS, Google Cloud SQL, and more).

## 🚀 Features

- **🔒 Read-Only by Design**: Only SELECT operations allowed for security
- **📊 Rich Database Tools**: 6 comprehensive database interaction tools
- **🏗️ Structured Data**: Pydantic models for type-safe, validated responses  
- **🤖 AI-Optimized**: Built specifically for LLM integration via MCP
- **☁️ Multi-Cloud Ready**: Works with Azure, AWS RDS, Google Cloud SQL, and any PostgreSQL
- **🔄 Flexible Configuration**: Profile-based configuration for local and external databases
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
- **PostgreSQL 12+** (local, cloud, or remote)
- **OpenAI API Key** (for the chat interface)
- **Network access** to your PostgreSQL database

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

Choose your database configuration profile:

#### **Local Database (Default)**
```env
# Database Profile Selection
DB_PROFILE=local

# Local Database Configuration
LOCAL_PGHOST=localhost
LOCAL_PGPORT=5432
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=mcp_user
LOCAL_PGPASSWORD=your_password

# OpenAI API (for chat interface)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
```

#### **External Database (Cloud/Remote)**
```env
# Database Profile Selection
DB_PROFILE=external

# External Database Configuration
EXTERNAL_PGHOST=your-database-host.com
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=your_database
EXTERNAL_PGUSER=your_username
EXTERNAL_PGPASSWORD=your_password

# Alternative: Use connection URL with SSL
EXTERNAL_DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# OpenAI API (for chat interface)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
```

#### **Legacy Configuration (Backward Compatible)**
```env
# Traditional PostgreSQL environment variables (still supported)
PGHOST=localhost
PGPORT=5432
PGDATABASE=your_database
PGUSER=your_username
PGPASSWORD=your_password
DATABASE_URL=postgresql://user:password@host:port/database

# OpenAI API
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

**Verify Your Configuration:**
```bash
# Check current configuration
uv run python verify_setup.py

# Check specific profile configuration
uv run python postgres_mcp_server.py --info
```

**Start the MCP Server:**
```bash
# Use default profile (from .env)
uv run python postgres_mcp_server.py

# Override profile at runtime
uv run python postgres_mcp_server.py --profile external

# Show configuration details
uv run python postgres_mcp_server.py --info
```

**Launch the Chat Interface:**
```bash
# Uses current DB_PROFILE setting
uv run streamlit run streamlit_openai_mcp.py

# Override profile for session
DB_PROFILE=external uv run streamlit run streamlit_openai_mcp.py
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
│   ├── RUNBOOK.md
│   ├── EXTERNAL_DATABASE.md       # External database configuration
│   └── CONFIGURATION_EXAMPLES.md  # Real-world config examples
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

## 🌐 Database Deployment Scenarios

### 💻 Local Development
Perfect for development and testing with local PostgreSQL:
```bash
DB_PROFILE=local
LOCAL_PGHOST=localhost
LOCAL_PGDATABASE=cmdb
```

### ☁️ Cloud Databases

#### **Azure Database for PostgreSQL**
```bash
DB_PROFILE=external
EXTERNAL_PGHOST=myserver.postgres.database.azure.com
EXTERNAL_PGUSER=username@myserver
EXTERNAL_DATABASE_URL=postgresql://user@server:pass@myserver.postgres.database.azure.com:5432/db?sslmode=require
```

#### **AWS RDS PostgreSQL**
```bash
DB_PROFILE=external
EXTERNAL_PGHOST=mydb.abc123.us-east-1.rds.amazonaws.com
EXTERNAL_DATABASE_URL=postgresql://user:pass@mydb.abc123.us-east-1.rds.amazonaws.com:5432/analytics?sslmode=require
```

#### **Google Cloud SQL**
```bash
DB_PROFILE=external
EXTERNAL_PGHOST=10.1.2.3  # Private IP or public IP
EXTERNAL_DATABASE_URL=postgresql://user:pass@10.1.2.3:5432/production?sslmode=require
```

#### **Docker/Docker Compose**
```bash
DB_PROFILE=local
LOCAL_PGHOST=postgres_container  # Container name
LOCAL_PGDATABASE=cmdb
```

### 🔒 Enterprise Scenarios

- **Read Replicas**: Connect to read-only replicas for analytics
- **SSH Tunnels**: Access databases through bastion hosts  
- **VPN Connections**: Secure access to private databases
- **Multi-Environment**: Switch between dev/staging/production

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

## ☁️ Cloud Database Support

**Multi-Cloud Ready - Works with any PostgreSQL database:**

### Azure Database for PostgreSQL
```env
DB_PROFILE=external
EXTERNAL_PGHOST=myserver.postgres.database.azure.com
EXTERNAL_PGUSER=username@myserver
EXTERNAL_PGPASSWORD=password
EXTERNAL_DATABASE_URL=postgresql://user@server:pass@myserver.postgres.database.azure.com:5432/db?sslmode=require
```

### AWS RDS PostgreSQL
```env
DB_PROFILE=external
EXTERNAL_PGHOST=mydb.abc123.us-east-1.rds.amazonaws.com
EXTERNAL_DATABASE_URL=postgresql://user:pass@mydb.abc123.us-east-1.rds.amazonaws.com:5432/db?sslmode=require
```

### Google Cloud SQL
```env
DB_PROFILE=external
EXTERNAL_PGHOST=10.1.2.3
EXTERNAL_DATABASE_URL=postgresql://user:pass@10.1.2.3:5432/db?sslmode=require
```

**Supported Features:**
- ✅ Profile-based configuration (local/external)
- ✅ SSL/TLS connections
- ✅ Connection string and individual parameter formats
- ✅ Environment-specific profiles
- ✅ Command-line profile override
- ✅ Connection validation and testing

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
- **[External Database Guide](documentation/EXTERNAL_DATABASE.md)** - Configure external/cloud databases
- **[Configuration Examples](documentation/CONFIGURATION_EXAMPLES.md)** - Real-world deployment scenarios

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