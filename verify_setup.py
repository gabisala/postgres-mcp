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

# PostgreSQL configuration
pg_vars = {
    "PGHOST": os.getenv("PGHOST"),
    "PGPORT": os.getenv("PGPORT"),
    "PGDATABASE": os.getenv("PGDATABASE"),
    "PGUSER": os.getenv("PGUSER"),
    "PGPASSWORD": os.getenv("PGPASSWORD")
}

print("   PostgreSQL Configuration:")
for var, value in pg_vars.items():
    if value:
        if var == "PGPASSWORD":
            print(f"      ✅ {var} = ****** (configured)")
        else:
            print(f"      ✅ {var} = {value}")
    else:
        print(f"      ❌ {var} = Not set")
        if var != "PGPASSWORD":  # Password might be empty
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
async def test_db():
    try:
        import asyncpg
        
        # Build connection string
        db_url = f"postgresql://{pg_vars['PGUSER']}:{pg_vars['PGPASSWORD']}@{pg_vars['PGHOST']}:{pg_vars['PGPORT']}/{pg_vars['PGDATABASE']}"
        
        # Try to connect
        conn = await asyncpg.connect(db_url, timeout=5)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        
        print(f"   ✅ Connected to PostgreSQL")
        print(f"      Version: {version.split(',')[0]}")
        return True
    except Exception as e:
        print(f"   ❌ Could not connect to database")
        print(f"      Error: {str(e)}")
        return False

if all([pg_vars["PGHOST"], pg_vars["PGDATABASE"], pg_vars["PGUSER"]]):
    db_ok = asyncio.run(test_db())
    if not db_ok:
        all_good = False
else:
    print("   ⏭️  Skipping (database not configured)")

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
    print("\nRun your demo with:")
    print("   streamlit run streamlit_openai_mcp.py")
else:
    print("❌ Some issues need to be fixed:")
    print("\n1. Install missing packages:")
    print("   uv sync  # or pip install streamlit pandas openai mcp asyncpg python-dotenv")
    print("\n2. Create/update your .env file with:")
    print("   PGHOST=localhost")
    print("   PGPORT=5432")
    print("   PGDATABASE=your_database")
    print("   PGUSER=your_username")
    print("   PGPASSWORD=your_password")
    print("   OPENAI_API_KEY=sk-your-openai-key")
    print("\n3. Make sure PostgreSQL is running")

print("\n" + "=" * 50)