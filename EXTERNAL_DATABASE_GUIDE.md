# External Database Connection Guide

This guide explains how to connect your PostgreSQL MCP server to external databases and explores transport alternatives to STDIO.

## External Database Configuration

To connect to an external PostgreSQL database instead of the local CMDB:

### 1. Update Connection Settings

Edit your `.env` file with external database credentials:

```bash
# External database connection
PGHOST=your-external-host.com
PGPORT=5432
PGDATABASE=your_database_name
PGUSER=your_username
PGPASSWORD=your_password

# Or use DATABASE_URL format
DATABASE_URL=postgresql://username:password@external-host.com:5432/database_name
```

### 2. Verify Network Connectivity

- Ensure the external database is accessible from your machine
- Check firewall rules and network policies
- Verify VPN connection if required
- Test with: `psql -h external-host.com -U username -d database_name`

### 3. Database Permissions

- Your user account needs SELECT permissions on tables you want to query
- The MCP server only requires read access (no INSERT/UPDATE/DELETE needed)
- Recommended minimum permissions: `CONNECT` on database, `USAGE` on schema, `SELECT` on tables

### 4. Connection Security

- Use SSL/TLS encryption for production databases
- Consider connection pooling for high-traffic scenarios
- Set appropriate connection timeouts
- Example with SSL: `DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require`

### 5. Test External Connection

```bash
# Verify setup with external database
uv run python verify_setup.py

# Test specific connection
uv run python -c "
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    conn = await asyncpg.connect(
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD')
    )
    tables = await conn.fetch('SELECT tablename FROM pg_tables WHERE schemaname = \$1', 'public')
    print(f'Found {len(tables)} tables')
    await conn.close()

asyncio.run(test())
"
```

## Transport Alternatives to STDIO

FastMCP supports multiple transport protocols beyond STDIO. For external database deployments, consider:

### 1. Streamable HTTP Transport (Recommended for Web Deployments)

**Start Server:**
```bash
# Start server with HTTP transport
uv run python postgres_mcp_server.py --transport http --host 0.0.0.0 --port 8080

# Or modify server code:
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)
```

**Client Connection:**
```python
from fastmcp import Client

async with Client("http://your-server-host:8080/mcp") as client:
    tables = await client.call_tool("list_tables")
```

**Benefits:**
- Web-accessible via standard HTTP
- Works through firewalls and proxies  
- Supports authentication headers
- Better for cloud deployments
- Can handle multiple concurrent clients

### 2. Server-Sent Events (SSE) Transport (Legacy)

**Start Server:**
```bash
# Start with SSE transport  
uv run python postgres_mcp_server.py --transport sse --host 127.0.0.1 --port 8000

# Server code modification:
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
```

**Client Connection:**
```python
from fastmcp import Client
from fastmcp.client.transports import SSETransport

transport = SSETransport("http://server-host:8000/sse/")
async with Client(transport) as client:
    result = await client.call_tool("execute_query", {"query": "SELECT * FROM users LIMIT 5"})
```

### 3. Transport Comparison

| Transport | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **STDIO** | Local development, Claude Desktop | Simple, no network setup | Single client, local only |
| **HTTP** | Web applications, cloud deployment | Multi-client, web-standard, firewall-friendly | More complex setup |
| **SSE** | Real-time applications | Streaming support | Legacy, limited adoption |

## Production Deployment Recommendations

For external database access in production:

1. **Use HTTP Transport** - Most compatible and scalable
2. **Add Authentication** - Secure your MCP endpoints
3. **Enable SSL/TLS** - Encrypt transport layer
4. **Use Reverse Proxy** - nginx/Apache for load balancing
5. **Monitor Connections** - Track database and client connections

### Example Production Configuration

```python
# postgres_mcp_server.py
from fastmcp import FastMCP
from fastmcp.server.auth import BearerTokenAuth

mcp = FastMCP("PostgreSQL-MCP")

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",  # Bind to all interfaces
        port=8080,
        auth=BearerTokenAuth("your-secret-token")  # Add authentication
    )
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "postgres_mcp_server.py"]
```

## Client Configuration for External Databases

### Streamlit App with HTTP Transport

Update `streamlit_openai_mcp.py` to use HTTP instead of STDIO:

```python
from fastmcp import Client

# Replace STDIO client
# client = Client("python postgres_mcp_server.py")

# With HTTP client
async with Client("http://your-mcp-server:8080/mcp") as client:
    # Your existing tool calls
    pass
```

### Authentication Headers

If using authentication:

```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport(
    url="http://your-mcp-server:8080/mcp",
    headers={"Authorization": "Bearer your-secret-token"}
)

async with Client(transport) as client:
    result = await client.call_tool("list_tables")
```

## Security Considerations

### Database Security
- Use read-only database users
- Implement row-level security if needed
- Monitor query execution and performance
- Set connection limits and timeouts

### Transport Security
- Always use HTTPS in production
- Implement proper authentication
- Use API keys or JWT tokens
- Rate limit requests
- Log and monitor access

### Network Security
- Use VPNs for database connections
- Implement IP whitelisting
- Use secure tunnels (SSH, etc.)
- Monitor network traffic

This configuration allows your MCP server to connect to any external PostgreSQL database while providing flexible, secure transport options for client connections.