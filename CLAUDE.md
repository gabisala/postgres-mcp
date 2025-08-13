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

## Development Environment

### Package Management with uv

This project uses **uv** as the primary package manager for fast, reliable dependency management, with pip as fallback support.

#### Why uv?
- **Speed**: 10-100x faster than pip for dependency resolution and installation
- **Reliability**: Better dependency resolution with conflict detection
- **Modern**: Written in Rust, actively maintained by Astral
- **Compatibility**: Drop-in replacement for pip with additional features

### Environment Setup Methods

#### Method 1: Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies in one step
uv sync

# This automatically:
# - Creates .venv/ directory if it doesn't exist
# - Installs Python 3.12 if needed (specified in .python-version)
# - Installs all dependencies from pyproject.toml and uv.lock
# - Activates the virtual environment
```

#### Method 2: Using traditional pip + venv
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Method 3: Using uv with explicit venv management
```bash
# Create virtual environment with uv
uv venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies with uv
uv pip install -r requirements.txt
```

### Package Management Commands

#### Using uv (Preferred)
```bash
# Install dependencies from pyproject.toml/uv.lock
uv sync

# Add new dependency
uv add package-name
uv add --dev package-name  # Development dependency

# Remove dependency
uv remove package-name

# Update dependencies
uv sync --upgrade

# Install specific package version
uv add "package-name==1.2.3"

# Run commands in the virtual environment
uv run python script.py
uv run streamlit run streamlit_openai_mcp.py

# Show installed packages
uv pip list

# Generate requirements.txt for compatibility
uv pip freeze > requirements.txt
```

#### Using pip (Fallback)
```bash
# Activate virtual environment first
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add new dependency
pip install package-name
echo "package-name" >> requirements.txt

# Upgrade dependencies
pip install --upgrade -r requirements.txt

# Show installed packages
pip list
```

### Development Workflow

#### Initial Project Setup
```bash
# 1. Clone repository
git clone https://github.com/gabisala/postgres-mcp.git
cd postgres-mcp

# 2. Setup environment with uv (creates .venv automatically)
uv sync

# 3. Copy environment template
cp .env.template .env

# 4. Edit .env with your configuration
nano .env  # Add your OpenAI API key

# 5. Set up PostgreSQL and CMDB (WSL2/Ubuntu)
chmod +x setup_postgresql_wsl.sh
./setup_postgresql_wsl.sh

# 6. Verify setup
uv run python verify_setup.py
```

#### Daily Development Commands
```bash
# Activate environment (if using manual venv)
source .venv/bin/activate

# Start development server
uv run streamlit run streamlit_openai_mcp.py
# OR with activated venv:
streamlit run streamlit_openai_mcp.py

# Test MCP server directly
uv run python postgres_mcp_server.py

# Run database tests
uv run python test_cmdb_queries.py

# Install new package during development
uv add new-package
git add pyproject.toml uv.lock  # Commit both files
```

### Virtual Environment Management

#### Understanding .venv Directory
```bash
# The .venv directory structure:
.venv/
├── bin/                    # Executables (Linux/macOS)
│   ├── activate           # Environment activation script  
│   ├── python            # Python interpreter
│   └── streamlit         # Installed packages
├── lib/python3.12/        # Python packages
└── pyvenv.cfg            # Virtual environment config

# On Windows:
.venv/Scripts/activate.bat  # Activation script location
```

#### Environment Activation Best Practices
```bash
# Check if environment is active
echo $VIRTUAL_ENV  # Should show path to .venv

# Using uv (handles activation automatically)
uv run <command>           # Runs command in venv without activation

# Manual activation when needed
source .venv/bin/activate  # Linux/macOS
deactivate                 # Exit virtual environment

# Verify correct Python/packages are being used
which python              # Should point to .venv/bin/python
which streamlit           # Should point to .venv/bin/streamlit
python -c "import sys; print(sys.path[0])"  # Check Python path
```

#### Dependency Files and Lock Management
```bash
# Project uses multiple dependency files:
pyproject.toml            # Main project configuration (uv format)
uv.lock                   # Exact dependency versions (like package-lock.json)
requirements.txt          # pip-compatible format (for fallback)
.python-version          # Specifies Python 3.12 requirement

# When adding dependencies with uv:
uv add package-name       # Updates both pyproject.toml and uv.lock
git add pyproject.toml uv.lock  # Always commit both files

# When someone else adds dependencies:
uv sync                   # Installs exact versions from uv.lock
```

### Running the Applications

#### Using uv (Recommended - handles venv automatically)
```bash
# Run the Streamlit chat interface
uv run streamlit run streamlit_openai_mcp.py

# Test MCP server directly  
uv run python postgres_mcp_server.py

# Test CMDB with sample queries
uv run python test_cmdb_queries.py

# Run any Python script
uv run python script_name.py
```

#### Using activated virtual environment
```bash
# Activate environment first
source .venv/bin/activate

# Then run applications normally
streamlit run streamlit_openai_mcp.py
python postgres_mcp_server.py
python test_cmdb_queries.py

# Deactivate when done
deactivate
```

### Database Operations
```bash
# Connect to CMDB database
psql -U mcp_user -h localhost -d cmdb

# Start/stop PostgreSQL (WSL2)
sudo service postgresql start
sudo service postgresql stop

# Check PostgreSQL status
sudo service postgresql status
```

### Development Environment Troubleshooting

#### Common Issues and Solutions
```bash
# Issue: "Command not found" errors
# Solution: Make sure virtual environment is activated or use uv run
source .venv/bin/activate
# OR
uv run <command>

# Issue: Import errors for installed packages
# Solution: Verify you're using the correct Python interpreter
which python  # Should show .venv/bin/python
uv run which python

# Issue: Different package versions than expected
# Solution: Sync to locked versions
uv sync  # Installs exact versions from uv.lock

# Issue: Environment conflicts or corruption
# Solution: Recreate virtual environment
rm -rf .venv
uv sync  # Recreates .venv and installs dependencies

# Issue: uv command not found
# Solution: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # Or restart terminal
```

#### Environment Health Checks
```bash
# Verify environment setup
uv run python -c "
import sys
print(f'Python: {sys.executable}')
print(f'Version: {sys.version}')
print(f'Path: {sys.path[0]}')

# Check key packages
try:
    import streamlit, asyncpg, openai, fastmcp
    print('✅ All key packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Check uv environment status
uv pip list | head -10  # Show installed packages
ls -la .venv/           # Verify .venv directory structure
```

### Development Best Practices

#### Environment Management Rules
1. **Always use uv for dependency management** - Faster and more reliable than pip
2. **Use `uv run` for executing scripts** - Automatically handles virtual environment
3. **Commit both pyproject.toml and uv.lock** - Ensures reproducible builds
4. **Never commit .venv directory** - It's already in .gitignore
5. **Use .env.template for configuration examples** - Never commit actual .env files

#### IDE/Editor Setup
```bash
# VS Code workspace settings (.vscode/settings.json)
{
    "python.interpreter.path": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.defaultInterpreterPath": "./.venv/bin/python"
}

# PyCharm: Set Project Interpreter to .venv/bin/python
# Vim/Neovim: Add to .vimrc or init.lua
# let g:python3_host_prog = './.venv/bin/python'
```

#### Git Workflow with uv
```bash
# Adding new dependencies
uv add package-name                    # Add to pyproject.toml and uv.lock
git add pyproject.toml uv.lock        # Stage both files
git commit -m "Add package-name dependency"

# After pulling changes with new dependencies
git pull
uv sync                               # Install any new dependencies

# Updating all dependencies
uv sync --upgrade                     # Update to latest compatible versions
git add uv.lock                      # Commit the updated lock file
git commit -m "Update dependencies"
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

# AI Model Provider Selection
# Choose between "openai" (openai.com) or "azure" (Azure OpenAI)
AI_PROVIDER=openai

# OpenAI.com Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_MODEL=gpt-4o
```

### AI Model Provider Configuration

The application supports two AI providers that can be switched dynamically:

#### 1. OpenAI (openai.com)
Set `AI_PROVIDER=openai` to use OpenAI's direct API:
- **OPENAI_API_KEY**: Your OpenAI API key from openai.com
- **OPENAI_MODEL**: Model name (e.g., `gpt-4o`, `gpt-4-turbo`)
- **OPENAI_BASE_URL**: OpenAI API endpoint (defaults to `https://api.openai.com/v1`)

#### 2. Azure OpenAI
Set `AI_PROVIDER=azure` to use Azure-hosted OpenAI models:
- **AZURE_OPENAI_API_KEY**: Your Azure OpenAI resource API key
- **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI resource endpoint URL
- **AZURE_OPENAI_API_VERSION**: API version (recommended: `2024-10-21`)
- **AZURE_OPENAI_DEPLOYMENT_NAME**: Your model deployment name in Azure
- **AZURE_OPENAI_MODEL**: The underlying model (for reference)

#### Configuration-Based Switching
AI provider selection is controlled entirely through configuration:
1. **Edit your `.env` file** to set `AI_PROVIDER=openai` or `AI_PROVIDER=azure`
2. **Restart the Streamlit application** for changes to take effect
3. The sidebar displays the current provider and configuration status
4. Both providers use the same MCP integration and database tools

**No UI toggles** - Provider switching is intentionally configuration-only to prevent runtime changes and ensure consistent behavior across sessions.

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