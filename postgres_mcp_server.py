#!/usr/bin/env python3
"""
PostgreSQL MCP Server using Official MCP SDK
A Model Context Protocol server for interacting with PostgreSQL databases.
"""

import os
import json
import asyncio
import argparse
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

import asyncpg
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database_config() -> Dict[str, str]:
    """
    Get database configuration based on DB_PROFILE setting.
    Supports 'local' and 'external' profiles.
    
    Returns:
        Dictionary with database connection parameters
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
            print(f"Using external database profile: {host or 'from_url'}")
            return {
                'profile': 'external',
                'DATABASE_URL': db_url,
                'host': host or 'from_url',
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
        else:
            print("Warning: External profile selected but configuration incomplete, falling back to legacy variables")
    
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
        
        print(f"Using local database profile: {host}:{port}/{database}")
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
    
    print(f"Using legacy database configuration: {host}:{port}/{database}")
    return {
        'profile': 'legacy',
        'DATABASE_URL': db_url,
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }


# Pydantic models for structured return types
class TableListResult(BaseModel):
    """Result model for list_tables tool."""
    schema_name: str = Field(description="Database schema name")
    tables: List[str] = Field(description="List of table names")
    total_count: int = Field(description="Total number of tables")


class TableDataResult(BaseModel):
    """Result model for read_table tool."""
    table: str = Field(description="Full table name (schema.table)")
    total_rows: int = Field(description="Total number of rows in table")
    returned_rows: int = Field(description="Number of rows returned")
    limit: int = Field(description="Applied row limit")
    offset: int = Field(description="Applied row offset")
    data: List[Dict[str, Any]] = Field(description="Table data rows")


class ColumnInfo(BaseModel):
    """Column information model."""
    name: str = Field(description="Column name")
    data_type: str = Field(description="Column data type")
    nullable: bool = Field(description="Whether column allows NULL values")
    default: Optional[str] = Field(description="Default value if any")
    constraints: List[str] = Field(description="Column constraints")


class TableSchemaResult(BaseModel):
    """Result model for describe_table tool."""
    table: str = Field(description="Full table name (schema.table)")
    columns: List[ColumnInfo] = Field(description="Table column definitions")
    foreign_keys: List[Dict[str, str]] = Field(description="Foreign key relationships")
    indexes: List[Dict[str, str]] = Field(description="Table indexes")


class QueryResult(BaseModel):
    """Result model for execute_query tool."""
    query: str = Field(description="Executed SQL query (truncated if long)")
    columns: List[str] = Field(description="Result column names")
    row_count: int = Field(description="Number of rows returned")
    data: List[Dict[str, Any]] = Field(description="Query result data")


class TableStatsResult(BaseModel):
    """Result model for get_table_stats tool."""
    table: str = Field(description="Full table name (schema.table)")
    row_count: int = Field(description="Total number of rows")
    column_count: int = Field(description="Number of columns")
    total_size: str = Field(description="Total table size (human readable)")
    table_size: str = Field(description="Table data size (human readable)")
    indexes_size: str = Field(description="Indexes size (human readable)")
    column_types: Dict[str, int] = Field(description="Distribution of column types")


class SearchResult(BaseModel):
    """Result model for search_tables tool."""
    search_term: str = Field(description="Search term used")
    schema_name: str = Field(description="Schema searched")
    matching_tables: List[str] = Field(description="Tables matching the search")
    matching_columns: List[Dict[str, str]] = Field(description="Columns matching the search")


# Initialize FastMCP server
mcp = FastMCP("postgresql-server")

# Global connection pool
pool: Optional[asyncpg.Pool] = None


async def ensure_connection_pool() -> bool:
    """Ensure the global asyncpg pool is initialized.

    Returns True if the pool is ready; False otherwise.
    """
    global pool
    if pool:
        return True

    db_config = get_database_config()
    db_url = db_config.get('DATABASE_URL')

    if not db_url:
        print("Error: No database URL could be constructed from configuration")
        return False

    try:
        pool = await asyncpg.create_pool(
            db_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        print("Connected to database successfully")
        return True
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False


@asynccontextmanager
async def lifespan(server):
    """Manage database connection lifecycle."""
    global pool
    
    # Startup: Create connection pool
    db_config = get_database_config()
    db_url = db_config.get('DATABASE_URL')
    
    if not db_url:
        print("Error: No database URL could be constructed from configuration")
        raise ValueError("Database configuration incomplete")
    
    try:
        pool = await asyncpg.create_pool(
            db_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        print(f"Connected to database successfully")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown: Close connection pool
    if pool:
        await pool.close()
        print("Database connection closed")


# Set the lifespan for the FastMCP server
mcp.lifespan = lifespan


@mcp.tool()
async def list_tables(schema: str = "public") -> TableListResult:
    """
    List all tables in the specified database schema.
    
    Args:
        schema: The database schema to list tables from (default: "public")
    
    Returns:
        Structured information about tables in the schema
    """
    if not pool:
        if not await ensure_connection_pool():
            # Return error in structured format
            return TableListResult(
                schema_name=schema,
                tables=[],
                total_count=0
            )
    
    try:
        async with pool.acquire() as conn:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = $1 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """
            rows = await conn.fetch(query, schema)
            
            tables = [row['table_name'] for row in rows]
            
            return TableListResult(
                schema_name=schema,
                tables=tables,
                total_count=len(tables)
            )
            
    except Exception as e:
        # Return empty result on error
        return TableListResult(
            schema_name=schema,
            tables=[],
            total_count=0
        )


@mcp.tool()
async def read_table(
    table_name: str,
    schema: str = "public",
    limit: int = 100,
    offset: int = 0
) -> TableDataResult:
    """
    Read contents from a PostgreSQL table.
    
    Args:
        table_name: Name of the table to read
        schema: Database schema (default: "public")
        limit: Maximum number of rows to return (default: 100)
        offset: Number of rows to skip (default: 0)
    
    Returns:
        Structured table data with metadata
    """
    if not pool:
        if not await ensure_connection_pool():
            return TableDataResult(
                table=f"{schema}.{table_name}",
                total_rows=0,
                returned_rows=0,
                limit=limit,
                offset=offset,
                data=[]
            )
    
    try:
        async with pool.acquire() as conn:
            # Validate table exists
            check_query = """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = $1 AND table_name = $2
            """
            exists = await conn.fetchval(check_query, schema, table_name)
            
            if not exists:
                return TableDataResult(
                    table=f"{schema}.{table_name}",
                    total_rows=0,
                    returned_rows=0,
                    limit=limit,
                    offset=offset,
                    data=[]
                )
            
            # Get total row count
            count_query = f"SELECT COUNT(*) FROM {schema}.{table_name}"
            total_rows = await conn.fetchval(count_query)
            
            # Read table data with limit and offset
            # Note: In production, you should use proper identifier escaping
            data_query = f"""
                SELECT * FROM {schema}.{table_name}
                ORDER BY 1
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(data_query, limit, offset)
            
            return TableDataResult(
                table=f"{schema}.{table_name}",
                total_rows=total_rows,
                returned_rows=len(rows),
                limit=limit,
                offset=offset,
                data=[dict(row) for row in rows]
            )
            
    except Exception as e:
        return TableDataResult(
            table=f"{schema}.{table_name}",
            total_rows=0,
            returned_rows=0,
            limit=limit,
            offset=offset,
            data=[]
        )


@mcp.tool()
async def describe_table(table_name: str, schema: str = "public") -> str:
    """
    Get detailed schema information about a PostgreSQL table.
    
    Args:
        table_name: Name of the table to describe
        schema: Database schema (default: "public")
    
    Returns:
        Detailed table schema including columns, types, constraints, and indexes
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    async with pool.acquire() as conn:
        # Get column information
        column_query = """
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.is_nullable,
                c.column_default,
                ARRAY_AGG(tc.constraint_type) as constraints
            FROM information_schema.columns c
            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name
            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.table_schema = tc.table_schema
            WHERE c.table_schema = $1 AND c.table_name = $2
            GROUP BY 
                c.column_name, c.ordinal_position, c.data_type,
                c.character_maximum_length, c.numeric_precision,
                c.numeric_scale, c.is_nullable, c.column_default
            ORDER BY c.ordinal_position;
        """
        
        columns = await conn.fetch(column_query, schema, table_name)
        
        if not columns:
            return f"Table '{schema}.{table_name}' not found"
        
        # Get indexes
        index_query = """
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = $1 AND tablename = $2;
        """
        indexes = await conn.fetch(index_query, schema, table_name)
        
        # Get foreign key relationships
        fk_query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_schema = $1
                AND tc.table_name = $2;
        """
        foreign_keys = await conn.fetch(fk_query, schema, table_name)
        
        # Format the output
        result = f"=== Table: {schema}.{table_name} ===\n\n"
        result += "COLUMNS:\n"
        
        for col in columns:
            # Format data type
            data_type = col['data_type']
            if col['character_maximum_length']:
                data_type += f"({col['character_maximum_length']})"
            elif col['numeric_precision']:
                data_type += f"({col['numeric_precision']}"
                if col['numeric_scale']:
                    data_type += f",{col['numeric_scale']}"
                data_type += ")"
            
            # Format column line
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            result += f"  • {col['column_name']}: {data_type} {nullable}"
            
            # Add constraints
            constraints = [c for c in col['constraints'] if c]
            if constraints:
                result += f" [{', '.join(set(constraints))}]"
            
            # Add default value
            if col['column_default']:
                result += f"\n      Default: {col['column_default']}"
            
            result += "\n"
        
        # Add foreign keys section
        if foreign_keys:
            result += "\nFOREIGN KEYS:\n"
            for fk in foreign_keys:
                result += f"  • {fk['column_name']} -> {fk['foreign_table']}.{fk['foreign_column']}\n"
        
        # Add indexes section
        if indexes:
            result += "\nINDEXES:\n"
            for idx in indexes:
                result += f"  • {idx['indexname']}\n"
                result += f"      {idx['indexdef']}\n"
        
        return result


@mcp.tool()
async def execute_query(query: str, limit: int = 100) -> str:
    """
    Execute a custom SELECT query on the PostgreSQL database.
    For safety, only SELECT statements are allowed.
    
    Args:
        query: SQL SELECT query to execute
        limit: Maximum number of rows to return (default: 100)
    
    Returns:
        Query results in JSON format or error message
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    # Safety check - only allow SELECT queries
    query_lower = query.lower().strip()
    if not query_lower.startswith('select'):
        return "Error: Only SELECT queries are allowed for safety. Use other tools for modifications."
    
    # Check for dangerous keywords even in SELECT
    dangerous_keywords = ['drop', 'delete', 'truncate', 'update', 'insert', 'alter', 'create']
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            return f"Error: Query contains potentially dangerous keyword '{keyword}'. Only pure SELECT queries are allowed."
    
    # Add LIMIT if not present
    if 'limit' not in query_lower:
        query = query.rstrip(';') + f" LIMIT {limit}"
    
    async with pool.acquire() as conn:
        try:
            # Execute query with timeout
            rows = await asyncio.wait_for(
                conn.fetch(query),
                timeout=30.0  # 30 second timeout
            )
            
            if not rows:
                return "Query executed successfully but returned no results."
            
            # Get column names from the first row
            columns = list(rows[0].keys())
            
            # Format results
            result = {
                "query": query[:200] + "..." if len(query) > 200 else query,
                "columns": columns,
                "row_count": len(rows),
                "data": [dict(row) for row in rows]
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except asyncio.TimeoutError:
            return "Error: Query execution timed out (30 seconds limit)"
        except asyncpg.PostgresSyntaxError as e:
            return f"SQL Syntax Error: {str(e)}"
        except asyncpg.InsufficientPrivilegeError:
            return "Error: Insufficient privileges to execute this query"
        except Exception as e:
            return f"Query execution error: {str(e)}"


@mcp.tool()
async def get_table_stats(table_name: str, schema: str = "public") -> str:
    """
    Get statistics about a PostgreSQL table including row count, size, and basic analytics.
    
    Args:
        table_name: Name of the table
        schema: Database schema (default: "public")
    
    Returns:
        Table statistics including size, row count, and column statistics
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    async with pool.acquire() as conn:
        try:
            # Check if table exists
            exists_query = """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = $1 AND table_name = $2
            """
            exists = await conn.fetchval(exists_query, schema, table_name)
            
            if not exists:
                return f"Error: Table '{schema}.{table_name}' not found"
            
            # Get table size and stats
            stats_query = """
                SELECT 
                    pg_size_pretty(pg_total_relation_size($1::regclass)) as total_size,
                    pg_size_pretty(pg_relation_size($1::regclass)) as table_size,
                    pg_size_pretty(pg_indexes_size($1::regclass)) as indexes_size,
                    (SELECT COUNT(*) FROM """ + f"{schema}.{table_name}" + """) as row_count,
                    (SELECT COUNT(*) FROM information_schema.columns 
                     WHERE table_schema = $2 AND table_name = $3) as column_count
            """
            
            full_table_name = f"{schema}.{table_name}"
            stats = await conn.fetchrow(stats_query, full_table_name, schema, table_name)
            
            # Get column data types distribution
            type_query = """
                SELECT data_type, COUNT(*) as count
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                GROUP BY data_type
                ORDER BY count DESC
            """
            type_dist = await conn.fetch(type_query, schema, table_name)
            
            # Format results
            result = f"=== Statistics for {schema}.{table_name} ===\n\n"
            result += f"Row Count:     {stats['row_count']:,}\n"
            result += f"Column Count:  {stats['column_count']}\n"
            result += f"Total Size:    {stats['total_size']}\n"
            result += f"Table Size:    {stats['table_size']}\n"
            result += f"Indexes Size:  {stats['indexes_size']}\n\n"
            
            result += "Column Type Distribution:\n"
            for type_info in type_dist:
                result += f"  • {type_info['data_type']}: {type_info['count']} columns\n"
            
            return result
            
        except Exception as e:
            return f"Error getting table statistics: {str(e)}"


@mcp.tool()
async def search_tables(search_term: str, schema: str = "public") -> str:
    """
    Search for tables and columns containing a specific term.
    
    Args:
        search_term: Term to search for in table and column names
        schema: Database schema to search in (default: "public")
    
    Returns:
        List of matching tables and columns
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    search_pattern = f"%{search_term.lower()}%"
    
    async with pool.acquire() as conn:
        # Search for matching tables
        table_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = $1
            AND LOWER(table_name) LIKE $2
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        matching_tables = await conn.fetch(table_query, schema, search_pattern)
        
        # Search for matching columns
        column_query = """
            SELECT 
                table_name,
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = $1
            AND (LOWER(column_name) LIKE $2 OR LOWER(table_name) LIKE $2)
            ORDER BY table_name, column_name
        """
        matching_columns = await conn.fetch(column_query, schema, search_pattern)
        
        # Format results
        result = f"=== Search Results for '{search_term}' in schema '{schema}' ===\n\n"
        
        if matching_tables:
            result += f"MATCHING TABLES ({len(matching_tables)}):\n"
            for table in matching_tables:
                result += f"  • {table['table_name']}\n"
            result += "\n"
        else:
            result += "No matching tables found.\n\n"
        
        if matching_columns:
            result += f"MATCHING COLUMNS ({len(matching_columns)}):\n"
            current_table = None
            for col in matching_columns:
                if col['table_name'] != current_table:
                    current_table = col['table_name']
                    result += f"\n  {current_table}:\n"
                result += f"    • {col['column_name']} ({col['data_type']})\n"
        else:
            result += "No matching columns found."
        
        return result


# Main entry point
def main():
    """Run the PostgreSQL MCP server."""
    import sys
    
    parser = argparse.ArgumentParser(description='PostgreSQL MCP Server')
    parser.add_argument(
        '--profile', 
        choices=['local', 'external'], 
        help='Database profile to use (overrides DB_PROFILE env var)'
    )
    parser.add_argument(
        '--info', 
        action='store_true',
        help='Show configuration information and exit'
    )
    
    args = parser.parse_args()
    
    # Override DB_PROFILE if specified via command line
    if args.profile:
        os.environ['DB_PROFILE'] = args.profile
    
    # Validate database configuration
    try:
        db_config = get_database_config()
        if not db_config.get('DATABASE_URL'):
            print("Error: Database configuration incomplete!", file=sys.stderr)
            print("Please configure your database settings in .env file", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: Database configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print configuration info
    profile = os.getenv('DB_PROFILE', 'local')
    print(f"Starting PostgreSQL MCP Server")
    print(f"Database profile: {profile} ({db_config.get('profile', 'unknown')})")
    print(f"Host: {db_config['host']}:{db_config['port']}")
    print(f"Database: {db_config['database']}")
    print(f"Transport: stdio (MCP protocol)")
    
    if args.info:
        print("\nConfiguration Details:")
        print(f"  DATABASE_URL: {db_config['DATABASE_URL'][:50]}...")
        print(f"  Profile: {db_config.get('profile', 'unknown')}")
        return
    
    print("\nServer ready for MCP connections...")
    
    # Run the FastMCP server (always uses stdio for MCP protocol)
    mcp.run()


if __name__ == "__main__":
    main()