#!/usr/bin/env python3
"""
Quick Setup Verification for PostgreSQL + OpenAI + MCP Demo
Run this to check if everything is configured correctly.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_config():
    """
    Get database configuration based on DB_PROFILE setting.
    Same logic as postgres_mcp_server.py
    """
    profile = os.getenv('DB_PROFILE', 'local').lower()
    
    if profile == 'external':
        # Try external-specific environment variables first
        host = os.getenv('EXTERNAL_PGHOST')
        port = os.getenv('EXTERNAL_PGPORT', '5432')
        database = os.getenv('EXTERNAL_PGDATABASE')
        user = os.getenv('EXTERNAL_PGUSER')
        password = os.getenv('EXTERNAL_PGPASSWORD')
        db_url = os.getenv('EXTERNAL_DATABASE_URL')
        
        if not db_url and all([host, database, user]):
            db_url = f"postgresql://{user}:{password or ''}@{host}:{port}/{database}"
        
        if db_url:
            return {
                'profile': 'external',
                'DATABASE_URL': db_url,
                'host': host or 'from_url',
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
    
    # Use local profile or fallback to legacy environment variables
    if profile == 'local':
        # Try local-specific environment variables first
        host = os.getenv('LOCAL_PGHOST', 'localhost')
        port = os.getenv('LOCAL_PGPORT', '5432')
        database = os.getenv('LOCAL_PGDATABASE', 'cmdb')
        user = os.getenv('LOCAL_PGUSER', 'mcp_user')
        password = os.getenv('LOCAL_PGPASSWORD', '')
        db_url = os.getenv('LOCAL_DATABASE_URL')
        
        if not db_url:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        return {
            'profile': 'local',
            'DATABASE_URL': db_url,
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    # Fallback to legacy environment variables
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    database = os.getenv('PGDATABASE', 'postgres')
    user = os.getenv('PGUSER', 'postgres')
    password = os.getenv('PGPASSWORD', '')
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return {
        'profile': 'legacy',
        'DATABASE_URL': db_url,
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }

print("🔍 PostgreSQL + OpenAI + MCP Demo Setup Checker\n")
print("=" * 50)

# Track if everything is OK
all_good = True

# 1. Check Python version
print("\n1️⃣ Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"   ✅ Python {sys.version.split()[0]} (OK)")
else:
    print(f"   ❌ Python {sys.version.split()[0]} (Need 3.8+)")
    all_good = False

# 2. Check required files
print("\n2️⃣ Checking required files...")
required_files = {
    "postgres_mcp_server.py": "PostgreSQL MCP Server",
    "streamlit_openai_mcp.py": "Streamlit OpenAI Chat App",
    ".env": "Configuration file"
}

for file, description in required_files.items():
    if Path(file).exists():
        print(f"   ✅ {file} - {description}")
    else:
        print(f"   ❌ {file} - {description} (MISSING)")
        all_good = False

# 3. Check Python packages
print("\n3️⃣ Checking Python packages...")
packages = {
    "streamlit": "Web interface",
    "pandas": "Data handling",
    "openai": "GPT-4o integration",
    "mcp": "Official MCP SDK",
    "asyncpg": "PostgreSQL async driver",
    "dotenv": "Environment variables"
}

for package, description in packages.items():
    try:
        if package == "dotenv":
            import dotenv
        else:
            __import__(package)
        print(f"   ✅ {package} - {description}")
    except ImportError:
        print(f"   ❌ {package} - {description} (NOT INSTALLED)")
        all_good = False

# 4. Check environment variables
print("\n4️⃣ Checking environment variables...")

# Get database configuration using the new profile system
db_config = get_database_config()
db_profile = os.getenv('DB_PROFILE', 'local')

print(f"   Database Profile: {db_profile} ({db_config.get('profile', 'unknown')})")
print("   PostgreSQL Configuration:")

if db_config:
    print(f"      ✅ Host: {db_config['host']}")
    print(f"      ✅ Port: {db_config['port']}")
    print(f"      ✅ Database: {db_config['database']}")
    print(f"      ✅ User: {db_config['user']}")
    if db_config['password']:
        print(f"      ✅ Password: ****** (configured)")
    else:
        print(f"      ⚠️  Password: (empty)")
    
    # Show transport configuration if available
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    print(f"   MCP Transport Configuration:")
    print(f"      ✅ Transport: {transport}")
    if transport in ['http', 'sse']:
        host = os.getenv('MCP_HOST', '0.0.0.0')
        port = os.getenv('MCP_PORT', '8080')
        print(f"      ✅ Server Host: {host}")
        print(f"      ✅ Server Port: {port}")
else:
    print("      ❌ Database configuration incomplete")
    all_good = False

# OpenAI configuration
openai_key = os.getenv("OPENAI_API_KEY")
print("\n   OpenAI Configuration:")
if openai_key:
    print(f"      ✅ OPENAI_API_KEY = sk-...{openai_key[-4:]} (configured)")
else:
    print(f"      ❌ OPENAI_API_KEY = Not set")
    all_good = False

# 5. Test database connection
print("\n5️⃣ Testing database connection...")
async def test_db(config):
    try:
        import asyncpg
        
        # Use the DATABASE_URL from configuration
        db_url = config['DATABASE_URL']
        
        # Try to connect
        conn = await asyncpg.connect(db_url, timeout=10)
        version = await conn.fetchval("SELECT version()")
        
        # Test a simple query
        result = await conn.fetchval("SELECT 1 as test")
        await conn.close()
        
        print(f"   ✅ Connected to PostgreSQL ({config['profile']} profile)")
        print(f"      Host: {config['host']}:{config['port']}")
        print(f"      Database: {config['database']}")
        print(f"      Version: {version.split(',')[0]}")
        print(f"      Test query result: {result}")
        return True
    except Exception as e:
        print(f"   ❌ Could not connect to database ({config['profile']} profile)")
        print(f"      Host: {config['host']}:{config['port']}")
        print(f"      Database: {config['database']}")
        print(f"      Error: {str(e)}")
        return False

if db_config and db_config.get('DATABASE_URL'):
    db_ok = asyncio.run(test_db(db_config))
    if not db_ok:
        all_good = False
else:
    print("   ⏭️  Skipping (database not configured)")
    all_good = False

# 6. Test OpenAI connection
print("\n6️⃣ Testing OpenAI API...")
if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        # Make a minimal test request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'OK' if you're working"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print(f"   ✅ OpenAI API is working (GPT-4o available)")
        else:
            print(f"   ❌ OpenAI API responded but no content")
            all_good = False
            
    except Exception as e:
        print(f"   ❌ OpenAI API error")
        print(f"      Error: {str(e)}")
        all_good = False
else:
    print("   ⏭️  Skipping (API key not configured)")

# Final summary
print("\n" + "=" * 50)
if all_good:
    print("✅ READY! Everything is configured correctly!")
    print(f"\nDatabase Profile: {db_config.get('profile', 'unknown')}")
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    print(f"MCP Transport: {transport}")
    
    print("\nRun your applications:")
    print("   # Streamlit chat interface")
    print("   uv run streamlit run streamlit_openai_mcp.py")
    print("   # or: streamlit run streamlit_openai_mcp.py")
    print("")
    print("   # MCP server directly")
    print("   uv run python postgres_mcp_server.py")
    
    if transport == 'http':
        host = os.getenv('MCP_HOST', '0.0.0.0')
        port = os.getenv('MCP_PORT', '8080')
        print(f"   # HTTP server will be available at: http://{host}:{port}/mcp")
        print("   uv run python postgres_mcp_server.py --transport http")
    elif transport == 'sse':
        host = os.getenv('MCP_HOST', '0.0.0.0')
        port = os.getenv('MCP_PORT', '8080')
        print(f"   # SSE server will be available at: http://{host}:{port}/sse")
        print("   uv run python postgres_mcp_server.py --transport sse")
else:
    print("❌ Some issues need to be fixed:")
    print("\n1. Install missing packages:")
    print("   uv sync  # or pip install streamlit pandas openai mcp asyncpg python-dotenv")
    print("\n2. Create/update your .env file. Choose one of:")
    print("\n   LOCAL DATABASE (default):")
    print("   DB_PROFILE=local")
    print("   LOCAL_PGHOST=localhost")
    print("   LOCAL_PGPORT=5432")
    print("   LOCAL_PGDATABASE=cmdb")
    print("   LOCAL_PGUSER=mcp_user")
    print("   LOCAL_PGPASSWORD=your_password")
    print("   OPENAI_API_KEY=sk-your-openai-key")
    print("\n   EXTERNAL DATABASE:")
    print("   DB_PROFILE=external")
    print("   EXTERNAL_PGHOST=your-external-host.com")
    print("   EXTERNAL_PGDATABASE=your_database")
    print("   EXTERNAL_PGUSER=your_username")
    print("   EXTERNAL_PGPASSWORD=your_password")
    print("   OPENAI_API_KEY=sk-your-openai-key")
    print("\n   TRANSPORT OPTIONS:")
    print("   MCP_TRANSPORT=stdio    # For local/Claude Desktop")
    print("   MCP_TRANSPORT=http     # For web applications")
    print("   MCP_HOST=0.0.0.0       # HTTP/SSE host")
    print("   MCP_PORT=8080          # HTTP/SSE port")
    print("\n3. Make sure PostgreSQL is accessible")

print("\n" + "=" * 50)