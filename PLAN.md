# PostgreSQL MCP Server Implementation Plan

## Project Overview

This project implements a PostgreSQL Model Context Protocol (MCP) server that enables AI assistants to interact with PostgreSQL databases through a standardized interface. The server supports both local and Azure Database for PostgreSQL deployments with comprehensive security and authentication features.

## Architecture

### Core Components

1. **MCP Server** (`postgres_mcp_server.py`)
   - Official MCP Python SDK implementation
   - 6 database tools: `list_tables`, `describe_table`, `read_table`, `execute_query`, `get_table_stats`, `search_tables`
   - READ-ONLY design for safety
   - Connection pooling with asyncpg
   - Multi-environment database profiles

2. **Streamlit Client** (`streamlit_openai_mcp.py`)
   - Web interface powered by OpenAI GPT-4o
   - Natural language to SQL conversion
   - Rich data visualization
   - Export capabilities

3. **Database Profiles**
   - Local PostgreSQL for development
   - Azure Database for PostgreSQL (Single Server & Flexible Server)
   - Environment-based configuration switching

## MCP Protocol Implementation

### Server Structure
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

server = Server("postgres-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    # Return 6 database tools with JSON schemas

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    # Handle all tool invocations
```

### Tool Definitions

#### 1. `list_tables`
- **Purpose**: List all tables in a schema
- **Parameters**: `schema` (default: "public")
- **Returns**: Formatted list of tables with counts

#### 2. `describe_table`
- **Purpose**: Get detailed table schema information
- **Parameters**: `table_name`, `schema` (default: "public")
- **Returns**: Column details, constraints, indexes, foreign keys

#### 3. `read_table`
- **Purpose**: Read table contents with pagination
- **Parameters**: `table_name`, `schema`, `limit`, `offset`
- **Returns**: JSON-formatted data with metadata

#### 4. `execute_query`
- **Purpose**: Execute SELECT queries safely
- **Parameters**: `query`, `limit`
- **Security**: Blocks dangerous keywords, enforces SELECT-only

#### 5. `get_table_stats`
- **Purpose**: Get table statistics and size information
- **Parameters**: `table_name`, `schema`
- **Returns**: Row count, size, column type distribution

#### 6. `search_tables`
- **Purpose**: Search tables and columns by name
- **Parameters**: `search_term`, `schema`
- **Returns**: Matching tables and columns

## Azure Database Integration

### Connection Support

#### Azure Single Server Format
```
postgresql://username%40servername:password@servername.postgres.database.azure.com:5432/database?sslmode=require
```

#### Azure Flexible Server Format
```
postgresql://username:password@servername.postgres.database.azure.com:5432/database?sslmode=require
```

### Authentication Methods

1. **Standard Authentication**
   - Username/password with SSL enforcement
   - Automatic URL encoding for Azure format

2. **Azure AD Authentication**
   - Service principal authentication
   - Managed Identity support
   - Token-based authentication with refresh

3. **Key Vault Integration**
   - Secure credential storage
   - Automatic secret retrieval
   - Environment-based configuration

### SSL/TLS Configuration

- **SSL Enforcement**: Required for all Azure connections
- **Certificate Validation**: Azure SSL certificate support
- **TLS Version**: Minimum version requirements
- **Connection Security**: Encrypted data in transit

## Database Profiles System

### Profile Configuration
```python
DB_PROFILES = {
    "local": {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "ssl_mode": "prefer",
        "pool_size": {"min": 1, "max": 10}
    },
    "azure_dev": {
        "host": "dev-server.postgres.database.azure.com",
        "port": 5432,
        "database": "dev_database",
        "ssl_mode": "require",
        "pool_size": {"min": 2, "max": 15},
        "azure_server_type": "flexible"
    },
    "azure_prod": {
        "host": "prod-server.postgres.database.azure.com",
        "port": 5432,
        "database": "production",
        "ssl_mode": "require",
        "pool_size": {"min": 5, "max": 25},
        "azure_server_type": "single",
        "use_azure_ad": True
    }
}
```

### Environment Variables

#### Basic Configuration
```env
# Profile selection
DB_PROFILE=local|azure_dev|azure_prod

# Database URL (overrides profile)
DATABASE_URL=postgresql://...

# Individual components
PGHOST=hostname
PGPORT=5432
PGDATABASE=database_name
PGUSER=username
PGPASSWORD=password
```

#### Azure-Specific Configuration
```env
# Azure AD Authentication
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
USE_AZURE_AD=true

# Azure Key Vault
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
DB_PASSWORD_SECRET_NAME=postgres-password

# SSL Configuration
SSL_MODE=require|prefer|disable
SSL_CERT_PATH=/path/to/certificate.pem
```

## Security Features

### Database Security
- **READ-ONLY Operations**: Only SELECT queries allowed
- **SQL Injection Protection**: Parameterized queries
- **Keyword Filtering**: Block dangerous SQL keywords
- **Query Timeouts**: Prevent long-running queries
- **Connection Limits**: Configurable pool sizes

### Azure Security
- **SSL Enforcement**: Required for Azure connections
- **Azure AD Integration**: Enterprise authentication
- **Managed Identity**: Passwordless authentication
- **Key Vault Integration**: Secure credential management
- **Network Security**: VNet and private endpoint support

## Connection Pool Optimization

### Local Database
```python
pool = await asyncpg.create_pool(
    db_url,
    min_size=1,
    max_size=10,
    command_timeout=60
)
```

### Azure Database
```python
pool = await asyncpg.create_pool(
    db_url,
    min_size=2,
    max_size=20,
    command_timeout=120,
    server_settings={
        'application_name': 'mcp_postgres_server',
        'tcp_keepalives_idle': '600',
        'tcp_keepalives_interval': '30',
        'tcp_keepalives_count': '3'
    }
)
```

## Error Handling

### Connection Errors
- Network timeout handling
- Azure service interruption recovery
- SSL/TLS handshake failures
- Authentication failures

### Query Errors
- SQL syntax error reporting
- Permission denied handling
- Table/column not found errors
- Query timeout management

## Performance Considerations

### Local vs Azure Optimization
- **Local**: Lower latency, higher connection limits
- **Azure**: Network optimization, connection pooling, retry logic

### Query Optimization
- **Pagination**: LIMIT/OFFSET support
- **Result Limiting**: Configurable row limits
- **Metadata Caching**: Schema information caching
- **Connection Reuse**: Efficient pool management

## Development Workflow

### Phase 1: MCP Protocol Compliance 
1.  Remove FastMCP dependency
2. = Implement official MCP Server class
3. ó Add proper tool schemas
4. ó Implement request/response handling

### Phase 2: Azure Integration
1. ó Azure connection string parsing
2. ó SSL/TLS configuration
3. ó Azure AD authentication
4. ó Key Vault integration

### Phase 3: Multi-Environment Support
1. ó Database profile system
2. ó Environment-based switching
3. ó Configuration validation
4. ó Connection testing

### Phase 4: Testing & Validation
1. ó Local database testing
2. ó Azure database testing
3. ó Client compatibility testing
4. ó Performance benchmarking

### Phase 5: Documentation & Deployment
1. ó Update documentation
2. ó Create deployment guides
3. ó Example configurations
4. ó Troubleshooting guides

## Testing Strategy

### Unit Tests
- Individual tool functionality
- Connection pool management
- Error handling scenarios
- Configuration parsing

### Integration Tests
- MCP protocol compliance
- Client-server communication
- Database connectivity
- Azure authentication

### End-to-End Tests
- Streamlit client interaction
- Multi-database scenarios
- Performance under load
- Error recovery

## Deployment Scenarios

### Local Development
- Docker PostgreSQL container
- Local configuration files
- Development database schema

### Azure Development
- Azure Database for PostgreSQL
- Development resource group
- Basic authentication

### Azure Production
- Managed Identity authentication
- Key Vault secret management
- Private endpoint connectivity
- High availability configuration

## Monitoring & Observability

### Connection Monitoring
- Pool utilization metrics
- Connection success/failure rates
- Query performance metrics
- Error rate tracking

### Azure-Specific Monitoring
- SSL handshake success
- Authentication token refresh
- Network latency metrics
- Service availability

## Future Enhancements

### Additional Features
- Query result caching
- Async streaming for large results
- Multi-database federation
- Read replica support

### Azure Enhancements
- Azure Monitor integration
- Application Insights logging
- Auto-scaling based on load
- Geo-replication support

### Security Enhancements
- Row-level security support
- Column-level encryption
- Audit logging
- Access control policies

## Configuration Examples

### Local Development
```env
DB_PROFILE=local
PGHOST=localhost
PGPORT=5432
PGDATABASE=development
PGUSER=dev_user
PGPASSWORD=dev_password
```

### Azure Development
```env
DB_PROFILE=azure_dev
DATABASE_URL=postgresql://devuser:devpass@mydev-server.postgres.database.azure.com:5432/devdb?sslmode=require
```

### Azure Production with Managed Identity
```env
DB_PROFILE=azure_prod
AZURE_SERVER_NAME=myprod-server.postgres.database.azure.com
AZURE_DATABASE_NAME=production
USE_AZURE_AD=true
USE_MANAGED_IDENTITY=true
SSL_MODE=require
```

This plan provides a comprehensive roadmap for implementing a production-ready PostgreSQL MCP server with full Azure integration support.