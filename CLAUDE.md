# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Information

**GitHub Repository**: https://github.com/gabisala/postgres-mcp
- **Owner**: gabisala
- **Repository Name**: postgres-mcp
- **Default Branch**: master
- **Access**: Public repository for collaborative development

## Project Overview

This is a PostgreSQL MCP (Model Context Protocol) server that enables AI assistants to interact with PostgreSQL databases through a standardized interface. The project includes:

- **FastMCP-based PostgreSQL server** (`postgres_mcp_server.py`) - Provides database tools via MCP protocol
- **Streamlit chat interface** (`streamlit_openai_mcp.py`) - OpenAI GPT-4o powered web UI for database interaction
- **CMDB example setup** - Complete Configuration Management Database with sample data

## Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
# OR using uv
uv sync

# Set up PostgreSQL and CMDB (WSL2)
chmod +x setup_postgresql_wsl.sh
./setup_postgresql_wsl.sh

# Verify setup
python verify_setup.py

# Load sample CMDB data
psql -U mcp_user -h localhost -d cmdb -f create_cmdb_database.sql
psql -U mcp_user -h localhost -d cmdb -f insert_sample_data.sql
```

### Running the Applications
```bash
# Run the Streamlit chat interface
streamlit run streamlit_openai_mcp.py

# Test MCP server directly
python postgres_mcp_server.py

# Test CMDB with sample queries
python test_cmdb_queries.py
```

### Database Operations
```bash
# Connect to CMDB database
psql -U mcp_user -h localhost -d cmdb

# Start/stop PostgreSQL (WSL2)
sudo service postgresql start
sudo service postgresql stop
```

## Architecture

### MCP Server (`postgres_mcp_server.py`)
- Uses FastMCP framework for MCP protocol implementation
- Provides 6 main database tools: `list_tables`, `describe_table`, `read_table`, `execute_query`, `get_table_stats`, `search_tables`
- Implements connection pooling with asyncpg
- READ-ONLY by design - only SELECT queries allowed in `execute_query` tool
- Environment-based configuration (supports both individual PG* vars and DATABASE_URL)

### Chat Interface (`streamlit_openai_mcp.py`)
- Streamlit web application with OpenAI GPT-4o integration
- Uses MCP client to communicate with PostgreSQL server via stdio
- Interprets natural language queries and translates to appropriate MCP tool calls
- Displays results as formatted text, DataFrames, or mixed content
- Includes conversation history and example queries

### CMDB Schema
Complete enterprise CMDB with tables:
- `departments` - Organizational units with budget/location info
- `servers` - Physical/virtual/cloud infrastructure
- `applications` - Software deployments with dependencies
- `incidents` - Issue tracking with severity levels
- `relationships` - Inter-component dependencies

## Configuration

### Environment Setup
1. Copy the environment template: `cp .env.template .env`
2. Edit `.env` with your actual configuration values

Required environment variables in `.env`:
```
# PostgreSQL Connection
PGHOST=localhost
PGPORT=5432
PGDATABASE=cmdb
PGUSER=mcp_user
PGPASSWORD=mcp_password

# Alternative connection string format
DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/cmdb

# OpenAI API (for chat interface)
OPENAI_API_KEY=sk-your-actual-openai-api-key
OPENAI_MODEL=gpt-4o
```

**Note**: The `.env` file is excluded from version control for security. Use `.env.template` as your starting point.

## Key Patterns

### Error Handling
- All MCP tools include comprehensive error handling with user-friendly messages
- Database connection failures are handled gracefully with retry logic
- SQL injection protection through parameterized queries and keyword filtering

### Security Features
- Execute queries restricted to SELECT statements only
- Dangerous SQL keywords blocked (`DROP`, `DELETE`, `UPDATE`, etc.)
- Connection timeouts and query limits enforced
- Environment variable based configuration (no hardcoded credentials)

### Data Display
- JSON formatting for structured data with proper serialization
- Rich table displays with metadata (row counts, table info)
- Pagination support with limit/offset parameters
- CSV export functionality in Streamlit interface

## Testing

The CMDB comes with realistic sample data:
- 8 departments (IT, HR, Finance, etc.)
- 20 servers (production, staging, development)
- 21 applications (web apps, databases, monitoring tools)
- 15 incidents (various severity levels)
- 20 relationships (dependencies between components)

Use `test_cmdb_queries.py` to verify database setup and see example queries.

## Project Documentation

### Planning and Task Management
- **`PLAN.md`** - Comprehensive implementation plan with Azure integration roadmap, architecture details, and phase-by-phase development workflow
- **`TASKS.md`** - Active task tracker showing current progress, sprint goals, and detailed task breakdowns with dependencies

### Technical Documentation (`documentation/` folder)
- **`ARCHITECTURE.md`** - Complete system architecture with component diagrams, data flows, and technology stack details
- **`DB_SCHEMA.md`** - Comprehensive database schema documentation with ERD, table definitions, sample queries, and performance considerations  
- **`MCP_CLIENT.md`** - Detailed client implementation documentation covering Streamlit integration, GPT-4o communication, and response formatting
- **`MCP_SERVER.md`** - Complete MCP server documentation including all 6 database tools, connection management, and security implementation
- **`RUNBOOK.md`** - Operational procedures for setup, deployment, monitoring, maintenance, and troubleshooting
- **`SECURITY.md`** - Multi-layered security model documentation covering read-only enforcement, SQL injection prevention, and compliance frameworks