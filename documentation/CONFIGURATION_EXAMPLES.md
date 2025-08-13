# Configuration Examples

This document provides real-world configuration examples for different deployment scenarios.

## Common Deployment Scenarios

### 1. Development Environment (Local)

**Use Case**: Local development with CMDB database

```bash
# .env file
DB_PROFILE=local
LOCAL_PGHOST=localhost
LOCAL_PGPORT=5432
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=mcp_user
LOCAL_PGPASSWORD=dev_password
OPENAI_API_KEY=sk-your-development-key
```

**Usage**:
```bash
# Start development server
uv run python postgres_mcp_server.py

# Start Streamlit interface
uv run streamlit run streamlit_openai_mcp.py
```

### 2. Production Environment (External Database)

**Use Case**: Production deployment connecting to external PostgreSQL

```bash
# .env file
DB_PROFILE=external
EXTERNAL_PGHOST=prod-db.company.com
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=production_analytics
EXTERNAL_PGUSER=readonly_mcp
EXTERNAL_PGPASSWORD=secure_prod_password
OPENAI_API_KEY=sk-your-production-key
```

**Usage**:
```bash
# Verify configuration
uv run python verify_setup.py

# Start production server
uv run python postgres_mcp_server.py --profile external
```

### 3. Cloud Database (AWS RDS)

**Use Case**: Connecting to AWS RDS PostgreSQL instance

```bash
# .env file
DB_PROFILE=external
EXTERNAL_PGHOST=mydb.abc123.us-east-1.rds.amazonaws.com
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=analytics
EXTERNAL_PGUSER=mcp_service
EXTERNAL_PGPASSWORD=aws_secure_password
# Connection string with SSL
EXTERNAL_DATABASE_URL=postgresql://mcp_service:aws_secure_password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/analytics?sslmode=require
OPENAI_API_KEY=sk-your-aws-key
```

### 4. Docker Compose Environment

**Use Case**: Multi-container development with PostgreSQL container

```bash
# .env file
DB_PROFILE=local
LOCAL_PGHOST=postgres_container
LOCAL_PGPORT=5432
LOCAL_PGDATABASE=cmdb
LOCAL_PGUSER=postgres
LOCAL_PGPASSWORD=docker_password
OPENAI_API_KEY=sk-your-docker-key
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    container_name: postgres_container
    environment:
      POSTGRES_DB: cmdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: docker_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  mcp-server:
    build: .
    depends_on:
      - postgres
    env_file:
      - .env
    volumes:
      - .:/app
    working_dir: /app

volumes:
  postgres_data:
```

### 5. Multiple Environment Setup

**Use Case**: Switch between dev/staging/prod databases

```bash
# .env file - Base configuration
OPENAI_API_KEY=sk-your-key

# Local development
LOCAL_PGHOST=localhost
LOCAL_PGDATABASE=cmdb_dev
LOCAL_PGUSER=dev_user
LOCAL_PGPASSWORD=dev_pass

# Staging environment
EXTERNAL_PGHOST=staging-db.company.com
EXTERNAL_PGDATABASE=cmdb_staging
EXTERNAL_PGUSER=staging_user
EXTERNAL_PGPASSWORD=staging_pass

# Default to development
DB_PROFILE=local
```

**Usage**:
```bash
# Development
DB_PROFILE=local uv run python postgres_mcp_server.py

# Staging
DB_PROFILE=external uv run python postgres_mcp_server.py

# Production (override host)
EXTERNAL_PGHOST=prod-db.company.com DB_PROFILE=external uv run python postgres_mcp_server.py
```

### 6. Secure Cloud Deployment (Google Cloud SQL)

**Use Case**: Google Cloud SQL with SSL and IAM authentication

```bash
# .env file
DB_PROFILE=external
EXTERNAL_PGHOST=10.1.2.3  # Private IP
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=analytics
EXTERNAL_PGUSER=mcp-service@project-id.iam
# Connection string with SSL and additional parameters
EXTERNAL_DATABASE_URL=postgresql://mcp-service%40project-id.iam@10.1.2.3:5432/analytics?sslmode=require&sslcert=client-cert.pem&sslkey=client-key.pem&sslrootcert=server-ca.pem
OPENAI_API_KEY=sk-your-gcp-key
```

### 7. Read Replica Setup

**Use Case**: Connecting to read replica for analytics

```bash
# .env file
DB_PROFILE=external
EXTERNAL_PGHOST=readonly-replica.company.com
EXTERNAL_PGPORT=5433  # Different port for replica
EXTERNAL_PGDATABASE=analytics
EXTERNAL_PGUSER=readonly_analytics
EXTERNAL_PGPASSWORD=replica_password
# Connection with specific application name for monitoring
EXTERNAL_DATABASE_URL=postgresql://readonly_analytics:replica_password@readonly-replica.company.com:5433/analytics?application_name=mcp-server&connect_timeout=10
OPENAI_API_KEY=sk-your-analytics-key
```

### 8. Development with SSH Tunnel

**Use Case**: Accessing remote database through SSH tunnel

```bash
# First, set up SSH tunnel (in separate terminal)
# ssh -L 5432:db-server:5432 user@bastion-host

# .env file
DB_PROFILE=external
EXTERNAL_PGHOST=localhost  # Through tunnel
EXTERNAL_PGPORT=5432
EXTERNAL_PGDATABASE=remote_db
EXTERNAL_PGUSER=remote_user
EXTERNAL_PGPASSWORD=remote_pass
OPENAI_API_KEY=sk-your-key
```

## Environment-Specific Configurations

### Development (.env.development)

```bash
DB_PROFILE=local
LOCAL_PGHOST=localhost
LOCAL_PGDATABASE=cmdb_dev
LOCAL_PGUSER=dev_user
LOCAL_PGPASSWORD=dev_password
OPENAI_API_KEY=sk-dev-key
OPENAI_MODEL=gpt-4o
```

### Staging (.env.staging)

```bash
DB_PROFILE=external
EXTERNAL_PGHOST=staging-db.company.com
EXTERNAL_PGDATABASE=cmdb_staging
EXTERNAL_PGUSER=staging_readonly
EXTERNAL_PGPASSWORD=staging_secure_password
EXTERNAL_DATABASE_URL=postgresql://staging_readonly:staging_secure_password@staging-db.company.com:5432/cmdb_staging?sslmode=require
OPENAI_API_KEY=sk-staging-key
OPENAI_MODEL=gpt-4o
```

### Production (.env.production)

```bash
DB_PROFILE=external
EXTERNAL_PGHOST=prod-db-cluster.company.com
EXTERNAL_PGDATABASE=cmdb_production
EXTERNAL_PGUSER=prod_readonly_mcp
EXTERNAL_PGPASSWORD=highly_secure_production_password
EXTERNAL_DATABASE_URL=postgresql://prod_readonly_mcp:highly_secure_production_password@prod-db-cluster.company.com:5432/cmdb_production?sslmode=require&connect_timeout=10&application_name=mcp-server-prod
OPENAI_API_KEY=sk-production-key
OPENAI_MODEL=gpt-4o
```

## Command-Line Usage Patterns

### Profile Switching

```bash
# Use local database
uv run python postgres_mcp_server.py --profile local

# Use external database
uv run python postgres_mcp_server.py --profile external

# Show configuration without starting
uv run python postgres_mcp_server.py --info

# Override profile for single session
DB_PROFILE=external uv run python postgres_mcp_server.py --info
```

### Verification Commands

```bash
# Test current configuration
uv run python verify_setup.py

# Test external profile specifically
DB_PROFILE=external uv run python verify_setup.py

# Test with environment override
EXTERNAL_PGHOST=test-db.com DB_PROFILE=external uv run python verify_setup.py
```

## Security Configuration Examples

### 1. Minimal Permissions Setup

**Database Setup**:
```sql
-- Create read-only user
CREATE USER mcp_readonly WITH PASSWORD 'secure_password';

-- Grant minimal permissions
GRANT CONNECT ON DATABASE analytics TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO mcp_readonly;

-- Ensure future tables are accessible
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
```

**Configuration**:
```bash
DB_PROFILE=external
EXTERNAL_PGUSER=mcp_readonly
EXTERNAL_PGPASSWORD=secure_password
# ... other settings
```

### 2. SSL/TLS Configuration

```bash
# Strong SSL enforcement
EXTERNAL_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require&sslcert=/path/to/client.crt&sslkey=/path/to/client.key&sslrootcert=/path/to/ca.crt

# SSL preferred (fallback to non-SSL)
EXTERNAL_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=prefer

# SSL with certificate verification
EXTERNAL_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=verify-full&sslrootcert=/path/to/ca.crt
```

### 3. Connection Pooling and Timeouts

```bash
# Connection string with performance tuning
EXTERNAL_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require&connect_timeout=10&command_timeout=30&server_lifetime=3600&max_inactive_time=300
```

## Troubleshooting Configurations

### Debug Connection Issues

```bash
# Test basic connectivity
psql "postgresql://user:pass@host:5432/db"

# Test with SSL
psql "postgresql://user:pass@host:5432/db?sslmode=require"

# Verbose connection testing
psql "postgresql://user:pass@host:5432/db?sslmode=require" -c "SELECT version();"
```

### Environment Variable Debugging

```bash
# Show all database-related environment variables
env | grep -E "(DB_|PG|DATABASE)" | sort

# Test configuration parsing
uv run python -c "
from postgres_mcp_server import get_database_config
import json
print(json.dumps(get_database_config(), indent=2))
"
```

### Connection String Testing

```bash
# Test raw asyncpg connection
uv run python -c "
import asyncpg
import asyncio
import sys

async def test():
    try:
        conn = await asyncpg.connect('$EXTERNAL_DATABASE_URL')
        version = await conn.fetchval('SELECT version()')
        print(f'Success: {version}')
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

asyncio.run(test())
"
```

## Integration Examples

### With CI/CD Pipelines

**GitHub Actions Example**:
```yaml
name: Test MCP Server
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_cmdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - name: Setup environment
        run: |
          echo "DB_PROFILE=local" >> .env
          echo "LOCAL_PGHOST=localhost" >> .env
          echo "LOCAL_PGDATABASE=test_cmdb" >> .env
          echo "LOCAL_PGUSER=postgres" >> .env
          echo "LOCAL_PGPASSWORD=postgres" >> .env
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
      
      - name: Test configuration
        run: uv run python verify_setup.py
```

### With Kubernetes

**ConfigMap Example**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
data:
  DB_PROFILE: "external"
  EXTERNAL_PGHOST: "postgres-service.database.svc.cluster.local"
  EXTERNAL_PGPORT: "5432"
  EXTERNAL_PGDATABASE: "analytics"
---
apiVersion: v1
kind: Secret
metadata:
  name: mcp-secrets
data:
  EXTERNAL_PGUSER: base64_encoded_username
  EXTERNAL_PGPASSWORD: base64_encoded_password
  OPENAI_API_KEY: base64_encoded_openai_key
```

These examples cover most common deployment scenarios and can be adapted to specific infrastructure requirements.