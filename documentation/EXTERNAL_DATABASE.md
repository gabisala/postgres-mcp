# External Database Configuration Guide

This guide explains how to configure the PostgreSQL MCP server to connect to external databases while maintaining local database compatibility.

## Overview

The PostgreSQL MCP server now supports multiple database configurations through a profile-based system:

- **Local Profile** (`local`) - Default configuration for local CMDB setup
- **External Profile** (`external`) - Configuration for external PostgreSQL databases
- **Legacy Mode** - Fallback compatibility with existing configurations

## Database Profiles

### Profile Selection

Set the database profile using the `DB_PROFILE` environment variable:

```bash
# Local database (default)
DB_PROFILE=local

# External database
DB_PROFILE=external
```

You can also override the profile at runtime:

```bash
# Override profile via command line
uv run python postgres_mcp_server.py --profile external
```

## Configuration Options

### Local Database Configuration

For connecting to the local CMDB database:

```bash
# Database Profile
DB_PROFILE=local

# Local Database Settings
LOCAL_PGHOST=localhost
LOCAL_PGPORT=5432
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=mcp_user
LOCAL_PGPASSWORD=mcp_password

# Alternative: Connection String
LOCAL_DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/cmdb
```

### External Database Configuration

For connecting to external PostgreSQL databases:

```bash
# Database Profile
DB_PROFILE=external

# External Database Settings
EXTERNAL_PGHOST=your-external-host.com
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=your_database_name
EXTERNAL_PGUSER=your_username
EXTERNAL_PGPASSWORD=your_password

# Alternative: Connection String (with SSL)
EXTERNAL_DATABASE_URL=postgresql://username:password@external-host.com:5432/database_name?sslmode=require
```

### Legacy Configuration

For backward compatibility with existing setups:

```bash
# These variables are used when no profile-specific config is found
PGHOST=localhost
PGPORT=5432
PGDATABASE=cmdb
PGUSER=mcp_user
PGPASSWORD=mcp_password
DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/cmdb
```

## Setup Instructions

### 1. Environment Configuration

Copy the environment template and configure for your needs:

```bash
cp .env.template .env
```

Edit `.env` file with your database configuration:

```bash
# For local database
DB_PROFILE=local
LOCAL_PGHOST=localhost
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=mcp_user
LOCAL_PGPASSWORD=your_local_password
OPENAI_API_KEY=sk-your-openai-key

# For external database
DB_PROFILE=external
EXTERNAL_PGHOST=prod.example.com
EXTERNAL_PGDATABASE=production_db
EXTERNAL_PGUSER=readonly_user
EXTERNAL_PGPASSWORD=secure_password
OPENAI_API_KEY=sk-your-openai-key
```

### 2. Network and Security Considerations

#### For External Databases:

- **Network Access**: Ensure external database is accessible from your machine
- **Firewall Rules**: Configure firewall to allow connections on database port
- **VPN Connection**: Connect to VPN if required for database access
- **SSL/TLS**: Use encrypted connections for production databases

```bash
# Test connectivity
psql -h external-host.com -U username -d database_name

# With SSL requirement
EXTERNAL_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

#### Database Permissions

The MCP server requires minimal read-only permissions:

- `CONNECT` privilege on the database
- `USAGE` privilege on the schema (usually `public`)
- `SELECT` privilege on tables you want to query

```sql
-- Example permission setup
GRANT CONNECT ON DATABASE your_database TO mcp_user;
GRANT USAGE ON SCHEMA public TO mcp_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_user;
```

### 3. Verification

Use the verification script to test your configuration:

```bash
# Test current profile
uv run python verify_setup.py

# Test specific profile
DB_PROFILE=external uv run python verify_setup.py
```

Check server configuration:

```bash
# Show current configuration
uv run python postgres_mcp_server.py --info

# Show external profile configuration
uv run python postgres_mcp_server.py --profile external --info
```

## Usage Examples

### Running the MCP Server

```bash
# Use default profile (local)
uv run python postgres_mcp_server.py

# Use external database profile
uv run python postgres_mcp_server.py --profile external

# Show configuration without starting server
uv run python postgres_mcp_server.py --info
```

### Running the Streamlit Interface

The Streamlit application automatically uses the configured database profile:

```bash
# Start chat interface (uses current DB_PROFILE)
uv run streamlit run streamlit_openai_mcp.py

# Override profile for session
DB_PROFILE=external uv run streamlit run streamlit_openai_mcp.py
```

## Configuration Priority

The system uses the following configuration priority (highest to lowest):

1. **Command-line profile override** (`--profile external`)
2. **Profile-specific environment variables** (`EXTERNAL_*` or `LOCAL_*`)
3. **Profile-specific connection string** (`EXTERNAL_DATABASE_URL` or `LOCAL_DATABASE_URL`)
4. **Legacy environment variables** (`PG*` variables)
5. **Default values** (localhost, port 5432, etc.)

## Connection String Formats

### Basic Connection

```bash
postgresql://username:password@hostname:port/database
```

### With SSL Requirements

```bash
postgresql://username:password@hostname:port/database?sslmode=require
```

### With Additional Parameters

```bash
postgresql://username:password@hostname:port/database?sslmode=require&connect_timeout=10&application_name=mcp-server
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused

```
Error: connection to server at "external-host.com" (1.2.3.4), port 5432 failed: Connection refused
```

**Solutions:**
- Verify hostname and port are correct
- Check firewall rules
- Ensure database server is running
- Verify network connectivity (`telnet hostname port`)

#### 2. Authentication Failed

```
Error: FATAL: password authentication failed for user "username"
```

**Solutions:**
- Verify username and password are correct
- Check if user exists in the database
- Verify user has connection permissions
- Check pg_hba.conf configuration on database server

#### 3. Database Does Not Exist

```
Error: FATAL: database "database_name" does not exist
```

**Solutions:**
- Verify database name is correct
- Check if user has access to the database
- Ensure database exists on the server

#### 4. SSL Connection Issues

```
Error: server does not support SSL, but SSL was required
```

**Solutions:**
- Remove `sslmode=require` from connection string
- Enable SSL on database server
- Use `sslmode=prefer` instead of `require`

### Debug Configuration

Use these commands to debug configuration issues:

```bash
# Show detailed configuration
uv run python postgres_mcp_server.py --info

# Test database connection only
uv run python verify_setup.py

# Check environment variables
env | grep -E "(DB_PROFILE|.*PG.*|.*DATABASE.*)"

# Test raw connection
python -c "
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
# Add your connection string here
asyncio.run(asyncpg.connect('postgresql://...'))
"
```

## Best Practices

### Security

1. **Use Read-Only Users**: Create dedicated read-only database users for MCP access
2. **Limit Network Access**: Use IP whitelisting and VPN connections
3. **Enable SSL**: Always use encrypted connections for external databases
4. **Rotate Credentials**: Regularly update database passwords
5. **Monitor Access**: Log and monitor database connections

### Performance

1. **Connection Pooling**: The server uses connection pooling by default (1-10 connections)
2. **Query Limits**: Built-in query limits prevent resource exhaustion
3. **Timeouts**: Connection and query timeouts prevent hanging connections
4. **Indexes**: Ensure proper indexing on frequently queried tables

### Operational

1. **Environment Separation**: Use different profiles for dev/staging/production
2. **Configuration Management**: Store configurations securely (not in code)
3. **Health Checks**: Use `--info` flag and verify_setup.py for monitoring
4. **Backup Plans**: Have fallback configurations ready

## Migration Guide

### From Legacy Configuration

If you're currently using the legacy `PG*` environment variables:

1. **Keep existing configuration** - it will continue to work
2. **Add profile selection** - set `DB_PROFILE=local` for clarity
3. **Optionally migrate** to `LOCAL_*` variables for consistency

```bash
# Old configuration (still works)
PGHOST=localhost
PGDATABASE=cmdb
PGUSER=mcp_user

# New configuration (recommended)
DB_PROFILE=local
LOCAL_PGHOST=localhost
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=mcp_user
```

### Adding External Database

To add external database capability to existing setup:

1. **Keep local configuration** unchanged
2. **Add external configuration** using `EXTERNAL_*` variables
3. **Switch profiles** as needed using `DB_PROFILE` or `--profile`

## Support and Resources

- **Verification Script**: Use `verify_setup.py` to test configurations
- **Configuration Display**: Use `--info` flag to see active configuration
- **PostgreSQL Documentation**: [Official PostgreSQL connection documentation](https://www.postgresql.org/docs/current/libpq-connect.html)
- **Connection String Reference**: [PostgreSQL connection URI format](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)

This external database capability enables flexible deployment scenarios while maintaining the simplicity and security of the original local CMDB setup.