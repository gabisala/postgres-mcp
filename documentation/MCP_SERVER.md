# MCP Server Documentation

## Overview

The PostgreSQL MCP Server (`postgres_mcp_server.py`) implements a Model Context Protocol server that exposes PostgreSQL database operations as standardized tools. Built with FastMCP framework, it provides a secure, read-only interface for AI assistants to query and analyze database content.

## Architecture

### Core Components

```mermaid
graph TB
    subgraph "MCP Server Process"
        MAIN[Main Entry Point] --> LIFESPAN[Lifespan Manager]
        LIFESPAN --> POOL[Connection Pool]
        
        subgraph "Tool Handlers"
            MAIN --> T1[@mcp.tool list_tables]
            MAIN --> T2[@mcp.tool describe_table]
            MAIN --> T3[@mcp.tool read_table]
            MAIN --> T4[@mcp.tool execute_query]
            MAIN --> T5[@mcp.tool get_table_stats]
            MAIN --> T6[@mcp.tool search_tables]
        end
        
        T1 --> POOL
        T2 --> POOL
        T3 --> POOL
        T4 --> POOL
        T5 --> POOL
        T6 --> POOL
    end
    
    POOL --> PG[(PostgreSQL Database)]
```

### Framework Details

- **Base Framework**: FastMCP (transitioning to official MCP SDK)
- **Transport**: Standard input/output (stdio)
- **Protocol**: JSON-RPC over stdio streams
- **Language**: Python 3.12+
- **Database Driver**: asyncpg for high-performance async operations

## Available Tools

### 1. list_tables

**Purpose**: Enumerate all tables in a specified database schema

**Parameters**:
- `schema` (string, optional): Database schema name (default: "public")

**Implementation**:
```python
@mcp.tool()
async def list_tables(schema: str = "public") -> str:
```

**Example Request**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_tables",
    "arguments": {"schema": "public"}
  }
}
```

**Example Response**:
```
Tables in schema 'public':
  • departments
  • servers
  • applications
  • incidents
  • relationships

Total: 5 tables
```

**Error Handling**:
- Database connection failures
- Invalid schema names
- Permission errors

---

### 2. describe_table

**Purpose**: Retrieve comprehensive schema information for a specific table

**Parameters**:
- `table_name` (string, required): Name of the table to describe
- `schema` (string, optional): Database schema name (default: "public")

**Implementation**:
```python
@mcp.tool()
async def describe_table(table_name: str, schema: str = "public") -> str:
```

**Output Includes**:
- Column names, data types, and constraints
- Primary keys, foreign keys, and unique constraints
- Default values and nullability
- Indexes and their definitions
- Foreign key relationships

**Example Response**:
```
=== Table: public.servers ===

COLUMNS:
  • id: integer NOT NULL [PRIMARY KEY]
      Default: nextval('servers_id_seq'::regclass)
  • hostname: character varying(100) NOT NULL [UNIQUE]
  • ip_address: inet NOT NULL
  • server_type: character varying(20)
  • environment: character varying(20)

FOREIGN KEYS:
  • department_id -> departments.id

INDEXES:
  • servers_pkey
      CREATE UNIQUE INDEX servers_pkey ON public.servers USING btree (id)
  • idx_servers_environment
      CREATE INDEX idx_servers_environment ON public.servers USING btree (environment)
```

---

### 3. read_table

**Purpose**: Retrieve table contents with pagination support

**Parameters**:
- `table_name` (string, required): Name of the table to read
- `schema` (string, optional): Database schema name (default: "public")
- `limit` (integer, optional): Maximum rows to return (default: 100)
- `offset` (integer, optional): Number of rows to skip (default: 0)

**Implementation**:
```python
@mcp.tool()
async def read_table(
    table_name: str,
    schema: str = "public",
    limit: int = 100,
    offset: int = 0
) -> str:
```

**Output Format**: JSON structure with metadata
```json
{
  "table": "public.servers",
  "total_rows": 20,
  "returned_rows": 5,
  "limit": 5,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "hostname": "web-prod-01",
      "ip_address": "10.10.10.11",
      "server_type": "physical",
      "environment": "production"
    }
  ]
}
```

**Features**:
- Automatic table existence validation
- Row count reporting
- Pagination metadata
- JSON serialization of all data types

---

### 4. execute_query

**Purpose**: Execute custom SELECT queries with safety restrictions

**Parameters**:
- `query` (string, required): SQL SELECT query to execute
- `limit` (integer, optional): Maximum rows to return (default: 100)

**Implementation**:
```python
@mcp.tool()
async def execute_query(query: str, limit: int = 100) -> str:
```

**Security Restrictions**:
- Only SELECT statements allowed
- Dangerous keywords blocked: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
- Automatic LIMIT injection if not present
- 30-second query timeout
- SQL injection protection via parameterized queries

**Example Query**:
```sql
SELECT s.hostname, s.environment, a.name as app_name
FROM servers s
JOIN applications a ON s.id = a.server_id
WHERE s.environment = 'production'
```

**Output Format**:
```json
{
  "query": "SELECT s.hostname, s.environment, a.name...",
  "columns": ["hostname", "environment", "app_name"],
  "row_count": 12,
  "data": [
    {
      "hostname": "web-prod-01",
      "environment": "production",
      "app_name": "Corporate Website"
    }
  ]
}
```

**Error Handling**:
- SQL syntax errors with detailed messages
- Permission denied errors
- Query timeout protection
- Invalid query structure detection

---

### 5. get_table_stats

**Purpose**: Provide comprehensive table statistics and analytics

**Parameters**:
- `table_name` (string, required): Name of the table to analyze
- `schema` (string, optional): Database schema name (default: "public")

**Implementation**:
```python
@mcp.tool()
async def get_table_stats(table_name: str, schema: str = "public") -> str:
```

**Statistics Provided**:
- Total row count
- Column count
- Physical storage size (table + indexes)
- Data type distribution
- Storage utilization

**Example Output**:
```
=== Statistics for public.servers ===

Row Count:     20
Column Count:  18
Total Size:    128 kB
Table Size:    64 kB
Indexes Size:  64 kB

Column Type Distribution:
  • character varying: 8 columns
  • integer: 4 columns
  • inet: 1 column
  • date: 3 columns
  • timestamp without time zone: 2 columns
```

**Use Cases**:
- Performance analysis
- Storage planning
- Data profiling
- Schema optimization

---

### 6. search_tables

**Purpose**: Search for tables and columns by name patterns

**Parameters**:
- `search_term` (string, required): Term to search for in names
- `schema` (string, optional): Database schema to search (default: "public")

**Implementation**:
```python
@mcp.tool()
async def search_tables(search_term: str, schema: str = "public") -> str:
```

**Search Behavior**:
- Case-insensitive pattern matching
- Searches both table names and column names
- Uses SQL LIKE with wildcards (`%term%`)
- Returns organized results by table

**Example Output**:
```
=== Search Results for 'server' in schema 'public' ===

MATCHING TABLES (1):
  • servers

MATCHING COLUMNS (3):

  applications:
    • server_id (integer)

  incidents:
    • server_id (integer)

  relationships:
    • parent_id (integer)
```

## Connection Management

### Connection Pool Configuration

```python
pool = await asyncpg.create_pool(
    db_url,
    min_size=1,
    max_size=10,
    command_timeout=60
)
```

**Pool Settings**:
- **Minimum Connections**: 1 (always maintains base connection)
- **Maximum Connections**: 10 (prevents resource exhaustion)
- **Command Timeout**: 60 seconds (prevents hanging queries)
- **Connection Validation**: Automatic health checks

### Lifespan Management

The server uses a lifespan manager to handle connection lifecycle:

```python
@asynccontextmanager
async def lifespan(server):
    # Startup: Create connection pool
    global pool
    pool = await asyncpg.create_pool(db_url, ...)
    print("Connected to database successfully")
    
    yield
    
    # Shutdown: Close connection pool
    if pool:
        await pool.close()
        print("Database connection closed")
```

### Connection String Support

The server supports multiple connection configuration methods:

1. **Environment Variables**:
   ```bash
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=cmdb
   PGUSER=mcp_user
   PGPASSWORD=mcp_password
   ```

2. **Database URL**:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:port/database
   ```

3. **Automatic Fallback**: Individual variables → DATABASE_URL → defaults

## Error Handling

### Connection Errors
```python
try:
    pool = await asyncpg.create_pool(db_url, ...)
except Exception as e:
    print(f"Failed to connect to database: {e}")
    raise
```

### Query Execution Errors
- `asyncpg.PostgresSyntaxError`: SQL syntax issues
- `asyncpg.InsufficientPrivilegeError`: Permission problems
- `asyncio.TimeoutError`: Query timeout exceeded
- `Exception`: Generic database errors

### Tool-Level Error Handling
Each tool implements comprehensive error handling:

```python
async def read_table(...):
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    async with pool.acquire() as conn:
        # Validate table exists
        exists = await conn.fetchval(check_query, schema, table_name)
        if not exists:
            return f"Error: Table '{schema}.{table_name}' not found"
        
        try:
            # Execute query
            rows = await conn.fetch(data_query, limit, offset)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return f"Error reading table: {str(e)}"
```

## Performance Considerations

### Query Optimization
- **Automatic Limits**: Prevents accidental large result sets
- **Connection Reuse**: Pool-based connection management
- **Timeout Protection**: Prevents resource exhaustion
- **Efficient Serialization**: JSON with proper type handling

### Memory Management
- **Streaming Results**: Large datasets handled efficiently
- **Connection Pooling**: Prevents connection exhaustion
- **Garbage Collection**: Automatic cleanup of query results

### Indexing Recommendations
The CMDB schema includes strategic indexes:
- Primary key indexes (automatic)
- Foreign key indexes for joins
- Environment and status filters
- Search-optimized indexes

## Configuration Options

### Environment Variables

| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| `PGHOST` | Database host | localhost | No |
| `PGPORT` | Database port | 5432 | No |
| `PGDATABASE` | Database name | postgres | No |
| `PGUSER` | Database user | postgres | No |
| `PGPASSWORD` | Database password | (empty) | No |
| `DATABASE_URL` | Full connection string | (built from above) | No |

### Pool Configuration (Future Enhancement)
```python
# Configurable via environment
pool = await asyncpg.create_pool(
    db_url,
    min_size=int(os.getenv('DB_POOL_MIN', 1)),
    max_size=int(os.getenv('DB_POOL_MAX', 10)),
    command_timeout=int(os.getenv('DB_TIMEOUT', 60))
)
```

## Security Model

### Read-Only Enforcement
- **Tool Level**: Only SELECT operations in `execute_query`
- **Keyword Filtering**: Dangerous SQL keywords blocked
- **Query Validation**: Syntax and structure checks

### SQL Injection Prevention
- **Parameterized Queries**: All user input properly escaped
- **Input Validation**: Schema and table name validation
- **Type Safety**: Proper data type handling

### Access Control
- **Database Permissions**: MCP user has minimal required permissions
- **Schema Isolation**: Optional schema-based access control
- **Connection Security**: SSL support for remote connections

## Monitoring & Observability

### Logging
- Connection establishment/failure events
- Tool execution timing
- Error conditions and resolution
- Pool utilization metrics

### Health Checks
```python
async def ensure_connection_pool() -> bool:
    """Health check for database connectivity"""
    if pool:
        return True
    # Attempt connection recovery
    return await initialize_pool()
```

### Performance Metrics
- Query execution times
- Connection pool utilization
- Error rates by tool
- Memory usage patterns

## Future Enhancements

### Planned Improvements
1. **Official MCP SDK Migration**: Replace FastMCP with official SDK
2. **Azure Integration**: Azure Database for PostgreSQL support
3. **Advanced Security**: Row-level security, column encryption
4. **Performance**: Query result caching, connection multiplexing
5. **Monitoring**: Prometheus metrics, distributed tracing

### Configuration Expansion
1. **Multi-Database Support**: Connect to multiple databases
2. **Schema Profiles**: Pre-configured schema access patterns
3. **Query Templates**: Reusable query patterns
4. **Access Policies**: Fine-grained permission control

This MCP server provides a robust, secure, and performant interface for AI-powered database interactions while maintaining strict read-only access and comprehensive error handling.