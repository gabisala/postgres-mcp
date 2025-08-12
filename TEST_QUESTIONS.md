# MCP Server Test Questions

This document contains comprehensive test questions to validate all capabilities of the PostgreSQL MCP server, including edge cases and error scenarios.

## Database Schema Overview
Your CMDB contains these tables:
- **applications** (40 records) - Software deployments and apps
- **audit_log** - System audit trail  
- **departments** (8 records) - Organizational units
- **incidents** (15 records) - Issue tracking
- **relationships** (20 records) - Component dependencies  
- **servers** (20 records) - Infrastructure inventory

## 1. list_tables() Tool Tests

### Basic Functionality
- "What tables are in my database?"
- "List all tables"
- "Show me the table names"
- "What tables do I have?"

### Schema-Specific Tests
- "List tables in the public schema"
- "Show tables from public schema"

### Edge Cases
- "List tables in the information_schema"
- "Show tables in the pg_catalog schema"
- "List tables in a non-existent schema called 'fake_schema'"

## 2. describe_table() Tool Tests

### Basic Table Structure
- "Describe the applications table"
- "Show me the structure of the servers table"
- "What columns does the departments table have?"
- "Tell me about the incidents table schema"

### Column Details
- "What data types are used in the applications table?"
- "Show me all constraints on the servers table"
- "What foreign keys exist in the relationships table?"
- "Which columns in departments are nullable?"

### Index Information
- "What indexes exist on the applications table?"
- "Show me the primary keys for all tables"

### Edge Cases
- "Describe a table called 'nonexistent_table'"
- "Show the structure of table 'APPLICATIONS' (uppercase)"
- "Describe the audit_log table from the public schema"

## 3. read_table() Tool Tests

### Basic Data Retrieval
- "Show me all records from departments"
- "Display data from the servers table"
- "Get me 5 rows from applications"
- "Show the first 3 incidents"

### Pagination Tests
- "Show me 10 records from applications starting from row 5"
- "Get records 11-20 from the servers table"
- "Show me the last 5 applications (using offset)"

### Limit Variations
- "Show me just 1 record from departments"
- "Give me exactly 50 rows from applications"
- "Show me all data from incidents" (should apply default limit)

### Edge Cases
- "Read data from nonexistent_table"
- "Show me 0 records from servers"
- "Get -5 records from applications" (negative limit)
- "Show me 1000 records from applications" (exceeds total)
- "Read from applications with offset 100" (beyond total rows)

## 4. execute_query() Tool Tests

### Simple SELECT Queries
- "SELECT * FROM departments"
- "SELECT name, budget FROM departments WHERE budget > 500000"
- "SELECT COUNT(*) FROM applications"
- "SELECT DISTINCT app_type FROM applications"

### JOIN Queries
- "SELECT s.hostname, a.name FROM servers s JOIN applications a ON s.id = a.server_id"
- "Show me all applications with their department names"
- "List servers and their applications"

### Aggregate Functions
- "What's the average budget of all departments?"
- "How many applications are there per department?"
- "What's the total monthly cost of all applications?"
- "Show me the department with the highest budget"

### Complex Queries
- "SELECT d.name as dept, COUNT(a.id) as app_count FROM departments d LEFT JOIN applications a ON d.id = a.department_id GROUP BY d.name ORDER BY app_count DESC"
- "Find all critical applications and their servers"
- "Show applications that cost more than $1000 per month"

### Security & Safety Tests (Should be BLOCKED)
- "DELETE FROM applications WHERE id = 1"
- "UPDATE servers SET hostname = 'hacked' WHERE id = 1"  
- "DROP TABLE applications"
- "INSERT INTO departments VALUES (999, 'Evil Dept', 'EVIL', 'Hacker', 0)"
- "TRUNCATE TABLE incidents"
- "ALTER TABLE servers ADD COLUMN hacked boolean"
- "CREATE TABLE malicious (id int)"

### SQL Injection Attempts (Should be BLOCKED)
- "SELECT * FROM applications; DROP TABLE servers; --"
- "SELECT * FROM departments WHERE name = 'IT'; DELETE FROM applications; --"
- "SELECT * FROM servers UNION SELECT * FROM applications"

### Query with Dangerous Keywords in Comments (Should work)
- "SELECT name FROM applications -- This is a DROP comment"
- "SELECT * FROM servers /* INSERT comment */"

### Syntax Error Tests
- "SELECTT * FROM applications" (typo)
- "SELECT * FORM departments" (typo) 
- "SELECT name FROM" (incomplete)
- "SELECT * FROM nonexistent_table"

## 5. get_table_stats() Tool Tests

### Basic Statistics
- "Get statistics for the applications table"
- "Show me stats about the servers table"
- "What are the size metrics for departments?"
- "How big is the incidents table?"

### Performance Metrics
- "What's the row count for applications?"
- "How much disk space does the servers table use?"
- "Show me column type distribution for applications"

### Edge Cases
- "Get stats for nonexistent_table"
- "Show statistics for 'APPLICATIONS' (uppercase)"
- "Get stats for audit_log table"

## 6. search_tables() Tool Tests

### Table Name Searches
- "Find tables containing 'app'"
- "Search for tables with 'server' in the name"
- "Look for tables named like 'dep'"

### Column Name Searches
- "Find all tables with an 'email' column"
- "Search for tables containing 'name' columns"
- "Look for 'id' columns across all tables"
- "Find tables with 'created_at' columns"

### Mixed Searches
- "Search for anything related to 'incident'"
- "Find tables or columns with 'budget'"
- "Look for 'status' in table or column names"

### Case Sensitivity Tests
- "Search for 'APPLICATION'" (uppercase)
- "Find 'Name' columns" (mixed case)
- "Look for 'ID' columns" (uppercase)

### Edge Cases
- "Search for 'xyz123' (non-existent term)"
- "Find tables with '@#$%' (special characters)"
- "Search for empty string ''"
- "Look for very long search term 'supercalifragilisticexpialidocious'"

## 7. Natural Language Query Tests

### Conversational Queries
- "How many departments do we have?"
- "What types of applications are deployed?"
- "Which servers are running Linux?"
- "Show me all critical applications"
- "What incidents happened recently?"

### Business Questions
- "What's our total IT budget across all departments?"
- "Which department has the most applications?"
- "How many production servers do we have?"
- "What's the most expensive application to run?"
- "Show me all applications that need disaster recovery"

### Complex Analysis
- "Compare application counts by programming language"
- "Show me the relationship between server types and applications"
- "Which departments have budget overruns?"
- "Find applications without proper documentation"

## 8. Error Handling & Edge Cases

### Connection Issues
- Test with database temporarily down
- Test with invalid credentials
- Test with network timeout

### Data Type Handling  
- Tables with JSON columns
- Tables with array columns
- Tables with timestamp data
- Tables with decimal/numeric precision

### Unicode & Special Characters
- "Search for tables with 'café' (accented characters)"
- Insert queries with emoji (should be blocked)
- Queries with unicode characters

### Memory & Performance
- "SELECT * FROM applications" (without LIMIT - should auto-add)
- Very large result sets
- Complex joins across multiple tables
- Queries that might timeout

## 9. Schema & Permission Tests

### Different Schemas
- "List tables in information_schema"
- "Describe information_schema.columns"
- "What tables are in pg_catalog?"

### Permission Boundaries
- Attempt to access system tables
- Try to read from restricted schemas
- Test read-only enforcement

## 10. Integration & Workflow Tests

### Multi-Step Workflows
1. "What tables do I have?" → "Describe the applications table" → "Show me 5 applications"
2. "Find tables with 'server'" → "Get stats for servers" → "Show me production servers"
3. "Search for 'incident'" → "Describe incidents table" → "Show recent incidents"

### Data Exploration Patterns
- "I'm new to this database, help me explore it"
- "Show me the most important tables and their relationships"
- "Give me an overview of the data structure"

## Expected Behaviors

### ✅ Should Work
- All SELECT queries (with auto-added LIMIT)
- All read operations on existing tables
- Pagination with limit/offset
- Basic aggregation functions
- JOINs between tables
- Case-insensitive table/column matching for search

### ❌ Should Be Blocked
- Any DML operations (INSERT, UPDATE, DELETE)
- Any DDL operations (CREATE, ALTER, DROP)
- Any administrative commands (GRANT, REVOKE)
- SQL injection attempts
- Queries with dangerous keywords

### 🔄 Should Handle Gracefully
- Non-existent tables/columns
- Invalid syntax errors
- Network timeouts
- Permission errors
- Large result sets (auto-pagination)

## Testing Tips

1. **Start Simple**: Begin with basic queries, then increase complexity
2. **Test Edge Cases**: Try invalid inputs, non-existent tables, etc.
3. **Security Testing**: Attempt dangerous operations to verify blocking
4. **Performance**: Test with large datasets and complex queries
5. **Error Recovery**: Test how system handles and recovers from errors
6. **User Experience**: Ensure responses are helpful and well-formatted

## Success Criteria

- ✅ All legitimate queries return properly formatted results
- ✅ All dangerous operations are blocked with clear error messages  
- ✅ Edge cases are handled gracefully without crashes
- ✅ Performance is acceptable for typical use cases
- ✅ Responses are user-friendly and informative
- ✅ Search functionality works across tables and columns
- ✅ Statistics provide useful insights about data