#!/usr/bin/env python3
"""
PostgreSQL MCP Server using FastMCP
A Model Context Protocol server for interacting with PostgreSQL databases.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import asyncpg
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

    db_url = os.getenv('DATABASE_URL')

    if not db_url:
        # Build from individual components
        host = os.getenv('PGHOST', 'localhost')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE', 'postgres')
        user = os.getenv('PGUSER', 'postgres')
        password = os.getenv('PGPASSWORD', '')

        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

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
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        # Build from individual components
        host = os.getenv('PGHOST', 'localhost')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE', 'postgres')
        user = os.getenv('PGUSER', 'postgres')
        password = os.getenv('PGPASSWORD', '')
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
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
async def list_tables(schema: str = "public") -> str:
    """
    List all tables in the specified database schema.
    
    Args:
        schema: The database schema to list tables from (default: "public")
    
    Returns:
        A formatted list of all tables in the schema
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    async with pool.acquire() as conn:
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = $1 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        rows = await conn.fetch(query, schema)
        
        if not rows:
            return f"No tables found in schema '{schema}'"
        
        tables = [row['table_name'] for row in rows]
        result = f"Tables in schema '{schema}':\n"
        result += "\n".join(f"  • {table}" for table in tables)
        result += f"\n\nTotal: {len(tables)} tables"
        
        return result


@mcp.tool()
async def read_table(
    table_name: str,
    schema: str = "public",
    limit: int = 100,
    offset: int = 0
) -> str:
    """
    Read contents from a PostgreSQL table.
    
    Args:
        table_name: Name of the table to read
        schema: Database schema (default: "public")
        limit: Maximum number of rows to return (default: 100)
        offset: Number of rows to skip (default: 0)
    
    Returns:
        JSON-formatted table contents with metadata
    """
    if not pool:
        if not await ensure_connection_pool():
            return "Error: Database connection not initialized"
    
    async with pool.acquire() as conn:
        # Validate table exists
        check_query = """
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = $1 AND table_name = $2
        """
        exists = await conn.fetchval(check_query, schema, table_name)
        
        if not exists:
            return f"Error: Table '{schema}.{table_name}' not found"
        
        try:
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
            
            # Format results
            result = {
                "table": f"{schema}.{table_name}",
                "total_rows": total_rows,
                "returned_rows": len(rows),
                "limit": limit,
                "offset": offset,
                "data": [dict(row) for row in rows]
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return f"Error reading table: {str(e)}"


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
    
    # Check if we have a database configuration
    if not any([
        os.getenv('DATABASE_URL'),
        all([os.getenv('PGHOST'), os.getenv('PGDATABASE')])
    ]):
        print("Error: Database configuration not found!", file=sys.stderr)
        print("Please set either DATABASE_URL or PGHOST/PGDATABASE/etc. environment variables", file=sys.stderr)
        sys.exit(1)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()