# Runbook Documentation

## Overview

This runbook provides comprehensive step-by-step instructions for setting up, running, and maintaining the PostgreSQL MCP Server and Streamlit application. It includes procedures for local development, production deployment, troubleshooting, and operational maintenance.

## Prerequisites

### System Requirements

#### Minimum Requirements
- **Operating System**: Linux (Ubuntu/Debian preferred), macOS, or Windows with WSL2
- **Python**: 3.12 or higher
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space (10GB for development with sample data)
- **Network**: Internet access for package installation and OpenAI API

#### Software Dependencies
- PostgreSQL 12+ (local installation or cloud instance)
- Git (for repository cloning)
- Python package manager (pip or uv)
- Text editor or IDE

### Account Requirements
- **OpenAI Account**: API access with GPT-4o model availability
- **PostgreSQL Database**: Local instance or cloud provider (Azure Database for PostgreSQL supported)

## Installation Guide

### Method 1: Automated Setup (Recommended for WSL2/Ubuntu)

#### Step 1: Download and Prepare
```bash
# Clone the repository
git clone <repository-url>
cd postgres-mcp

# Make setup script executable
chmod +x setup_postgresql_wsl.sh
```

#### Step 2: Run Automated Setup
```bash
# Execute the setup script (will prompt for passwords)
./setup_postgresql_wsl.sh
```

**What the script does**:
- Installs PostgreSQL and dependencies
- Creates database user and CMDB database
- Loads sample schema and data
- Configures authentication
- Creates `.env` file with database settings

#### Step 3: Configure OpenAI API
```bash
# Edit the .env file to add your OpenAI API key
nano .env

# Add this line with your actual API key:
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### Step 4: Install Python Dependencies
```bash
# Using pip
pip install -r requirements.txt

# OR using uv (recommended for faster installs)
uv sync
```

#### Step 5: Verify Installation
```bash
# Run the verification script
python verify_setup.py

# Test the database with sample queries
python test_cmdb_queries.py
```

### Method 2: Manual Setup

#### Step 1: Install PostgreSQL

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Windows**: Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

#### Step 2: Create Database and User
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database user
CREATE USER mcp_user WITH PASSWORD 'mcp_password';
ALTER USER mcp_user CREATEDB;

# Create database
CREATE DATABASE cmdb OWNER mcp_user;

# Exit PostgreSQL
\q
```

#### Step 3: Load Database Schema and Data
```bash
# Load schema
psql -U mcp_user -h localhost -d cmdb -f create_cmdb_database.sql

# Load sample data
psql -U mcp_user -h localhost -d cmdb -f insert_sample_data.sql
```

#### Step 4: Create Configuration File
```bash
# Create .env file
cat > .env << EOF
# PostgreSQL Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=cmdb
PGUSER=mcp_user
PGPASSWORD=mcp_password

# Alternative connection string
DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/cmdb

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
EOF
```

#### Step 5: Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Development Environment

#### Start PostgreSQL Service
```bash
# Linux (systemd)
sudo systemctl start postgresql

# Linux (SysV)
sudo service postgresql start

# macOS
brew services start postgresql

# WSL2
sudo service postgresql start
```

#### Launch the Streamlit Application
```bash
# Activate virtual environment if using one
source .venv/bin/activate

# Start the Streamlit web application
streamlit run streamlit_openai_mcp.py
```

#### Access the Application
- **Web Interface**: Open browser to `http://localhost:8501`
- **Default Port**: 8501 (configurable with `--port` flag)
- **Network Access**: Local only by default

#### Test MCP Server Directly
```bash
# Test the MCP server independently
python postgres_mcp_server.py

# Run database connectivity tests
python test_cmdb_queries.py
```

### Production Deployment

#### Environment Configuration

**Production .env file**:
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@prod-server:5432/production_db

# API Configuration
OPENAI_API_KEY=sk-prod-api-key

# Security Configuration
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/postgres-mcp/app.log
```

#### Docker Deployment (Future Enhancement)
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_openai_mcp.py", "--server.headless", "true"]
```

#### Systemd Service Configuration
```ini
# /etc/systemd/system/postgres-mcp.service
[Unit]
Description=PostgreSQL MCP Streamlit Application
After=network.target postgresql.service

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/postgres-mcp
Environment=PATH=/opt/postgres-mcp/.venv/bin
ExecStart=/opt/postgres-mcp/.venv/bin/streamlit run streamlit_openai_mcp.py --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Start Production Service
```bash
# Install and start the service
sudo systemctl daemon-reload
sudo systemctl enable postgres-mcp
sudo systemctl start postgres-mcp

# Check service status
sudo systemctl status postgres-mcp
```

### Cloud Deployment (Azure)

#### Azure Database for PostgreSQL Setup
```bash
# Create Azure Database for PostgreSQL
az postgres server create \
  --resource-group myResourceGroup \
  --name mypostgresserver \
  --location eastus \
  --admin-user myadmin \
  --admin-password mypassword \
  --sku-name GP_Gen5_2

# Configure firewall
az postgres server firewall-rule create \
  --resource-group myResourceGroup \
  --server mypostgresserver \
  --name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

#### Azure App Service Deployment
```bash
# Create App Service plan
az appservice plan create \
  --resource-group myResourceGroup \
  --name myAppServicePlan \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name myPostgresMCPApp \
  --runtime "PYTHON|3.12"

# Configure app settings
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name myPostgresMCPApp \
  --settings \
    DATABASE_URL="postgresql://user:pass@server.postgres.database.azure.com:5432/db?sslmode=require" \
    OPENAI_API_KEY="sk-your-api-key"
```

## Configuration Management

### Environment Variables

#### Core Configuration
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PGHOST` | No | localhost | PostgreSQL server hostname |
| `PGPORT` | No | 5432 | PostgreSQL server port |
| `PGDATABASE` | No | postgres | Database name |
| `PGUSER` | No | postgres | Database username |
| `PGPASSWORD` | No | (empty) | Database password |
| `DATABASE_URL` | No | (constructed) | Full database connection string |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-4o |

#### Advanced Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `DB_POOL_MIN` | 1 | Minimum database connections |
| `DB_POOL_MAX` | 10 | Maximum database connections |
| `DB_TIMEOUT` | 60 | Database command timeout (seconds) |
| `QUERY_LIMIT` | 1000 | Default query result limit |
| `LOG_LEVEL` | INFO | Application logging level |

### Configuration Files

#### Streamlit Configuration
```toml
# .streamlit/config.toml
[server]
headless = true
port = 8501
address = "0.0.0.0"
maxUploadSize = 10

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f0f0"
```

#### Logging Configuration
```python
# logging_config.py
import logging
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FILE = os.getenv('LOG_FILE', 'postgres_mcp.log')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
```

## Operational Procedures

### Daily Operations

#### Health Checks
```bash
#!/bin/bash
# daily_health_check.sh

echo "=== PostgreSQL MCP Health Check ===="
echo "Date: $(date)"

# Check PostgreSQL service
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL service: Running"
else
    echo "❌ PostgreSQL service: Stopped"
fi

# Check database connectivity
if python -c "import asyncio, asyncpg; asyncio.run(asyncpg.connect('$DATABASE_URL').close())" 2>/dev/null; then
    echo "✅ Database connectivity: OK"
else
    echo "❌ Database connectivity: Failed"
fi

# Check Streamlit service
if pgrep -f streamlit >/dev/null; then
    echo "✅ Streamlit application: Running"
else
    echo "❌ Streamlit application: Not running"
fi

# Check API connectivity
if curl -s "https://api.openai.com/v1/models" -H "Authorization: Bearer $OPENAI_API_KEY" | grep -q "gpt-4"; then
    echo "✅ OpenAI API: Accessible"
else
    echo "❌ OpenAI API: Inaccessible"
fi

echo "=================================="
```

#### Log Monitoring
```bash
#!/bin/bash
# monitor_logs.sh

# Monitor application logs for errors
tail -f postgres_mcp.log | grep -E "(ERROR|CRITICAL|Exception)" --line-buffered | while read line; do
    echo "[ALERT] $line"
    # Send notification (implement as needed)
done

# Monitor PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log | grep -E "(ERROR|FATAL)" --line-buffered | while read line; do
    echo "[DB ALERT] $line"
done
```

### Backup Procedures

#### Database Backup
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/opt/backups/postgres-mcp"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cmdb_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
echo "Creating database backup..."
pg_dump -U mcp_user -h localhost -d cmdb > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

#### Configuration Backup
```bash
#!/bin/bash
# backup_config.sh

CONFIG_BACKUP_DIR="/opt/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $CONFIG_BACKUP_DIR

# Backup configuration files (excluding sensitive data)
tar -czf "$CONFIG_BACKUP_DIR/config_backup_$DATE.tar.gz" \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='.git' \
    /opt/postgres-mcp/

echo "Configuration backup completed: config_backup_$DATE.tar.gz"
```

### Maintenance Tasks

#### Weekly Maintenance
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Weekly Maintenance - $(date) ==="

# Update system packages (if applicable)
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip list --outdated --format=json | jq -r '.[].name' | xargs -I {} pip install --upgrade {}

# Restart services to apply updates
sudo systemctl restart postgres-mcp
sudo systemctl restart postgresql

# Clean up old log files
find /var/log -name "*.log" -mtime +7 -delete
find . -name "*.log" -mtime +7 -delete

# Database maintenance
psql -U mcp_user -h localhost -d cmdb -c "VACUUM ANALYZE;"

echo "=== Maintenance Complete ==="
```

#### Monthly Maintenance
```bash
#!/bin/bash
# monthly_maintenance.sh

echo "=== Monthly Maintenance - $(date) ==="

# Database statistics update
psql -U mcp_user -h localhost -d cmdb << 'EOF'
-- Update table statistics
ANALYZE;

-- Check for bloated tables
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
EOF

# Security audit
python -c "
import pkg_resources
import requests

# Check for security vulnerabilities
for package in pkg_resources.working_set:
    try:
        response = requests.get(f'https://pypi.org/pypi/{package.project_name}/json', timeout=5)
        # Process security information
    except:
        pass
"

echo "=== Monthly Maintenance Complete ==="
```

## Troubleshooting Guide

### Common Issues

#### Database Connection Issues

**Problem**: "Failed to connect to database"
```bash
# Diagnosis steps
1. Check PostgreSQL service status
   sudo systemctl status postgresql

2. Verify database credentials
   psql -U mcp_user -h localhost -d cmdb -c "SELECT 1;"

3. Check network connectivity
   telnet localhost 5432

4. Review PostgreSQL logs
   sudo tail -f /var/log/postgresql/postgresql-*.log
```

**Solution**:
```bash
# Restart PostgreSQL service
sudo systemctl restart postgresql

# Reset user password if needed
sudo -u postgres psql -c "ALTER USER mcp_user PASSWORD 'new_password';"

# Update .env file with new credentials
```

#### OpenAI API Issues

**Problem**: "OpenAI Error: Invalid API key"
```bash
# Diagnosis
1. Check API key in .env file
   grep OPENAI_API_KEY .env

2. Test API key manually
   curl -s "https://api.openai.com/v1/models" \
     -H "Authorization: Bearer $OPENAI_API_KEY" | jq .

3. Check API usage limits
   # Log into OpenAI dashboard to check quota
```

**Solution**:
```bash
# Update API key in .env file
sed -i 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=sk-new-api-key/' .env

# Restart application
pkill -f streamlit
streamlit run streamlit_openai_mcp.py
```

#### Streamlit Application Issues

**Problem**: "Streamlit won't start" or "Port already in use"
```bash
# Diagnosis
1. Check if port 8501 is in use
   lsof -i :8501

2. Check for existing Streamlit processes
   pgrep -f streamlit

3. Review application logs
   tail -f *.log
```

**Solution**:
```bash
# Kill existing processes
pkill -f streamlit

# Start on different port
streamlit run streamlit_openai_mcp.py --server.port 8502

# Or configure in .streamlit/config.toml
```

#### Performance Issues

**Problem**: "Slow query responses"
```bash
# Diagnosis
1. Check database performance
   psql -U mcp_user -h localhost -d cmdb -c "
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC LIMIT 10;"

2. Monitor system resources
   top -p $(pgrep -f postgres)
   top -p $(pgrep -f streamlit)

3. Check connection pool status
   # Review application logs for pool utilization
```

**Solution**:
```bash
# Optimize database
psql -U mcp_user -h localhost -d cmdb -c "VACUUM ANALYZE;"

# Increase connection pool size
export DB_POOL_MAX=20

# Add query result caching (application enhancement)
```

### Error Codes and Solutions

| Error Code | Description | Solution |
|------------|-------------|----------|
| DB001 | Connection timeout | Check network, increase timeout settings |
| DB002 | Authentication failed | Verify credentials in .env file |
| DB003 | Database not found | Create database or update connection string |
| API001 | OpenAI rate limit | Implement exponential backoff, check quota |
| API002 | Invalid API key | Update API key in configuration |
| API003 | Model not available | Verify GPT-4o access, check OpenAI status |
| APP001 | Port in use | Change port or kill existing process |
| APP002 | Memory exhaustion | Restart application, check for memory leaks |
| APP003 | File permission error | Check file permissions and ownership |

### Log Analysis

#### Important Log Patterns
```bash
# Error patterns to monitor
grep -E "(ERROR|CRITICAL|Exception|Failed)" *.log

# Performance issues
grep -E "(timeout|slow|performance)" *.log

# Security events
grep -E "(auth|security|injection|blocked)" *.log

# Database connection issues
grep -E "(connection|pool|database)" *.log
```

#### Log Rotation Setup
```bash
# /etc/logrotate.d/postgres-mcp
/opt/postgres-mcp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

## Monitoring and Alerts

### Monitoring Setup

#### Prometheus Metrics (Future Enhancement)
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
query_counter = Counter('database_queries_total', 'Total database queries')
query_duration = Histogram('database_query_duration_seconds', 'Query duration')
active_connections = Gauge('database_connections_active', 'Active connections')

# Start metrics server
start_http_server(8000)
```

#### Basic Health Monitoring
```bash
#!/bin/bash
# health_monitor.sh

while true; do
    # Check application health
    if ! curl -s http://localhost:8501 > /dev/null; then
        echo "ALERT: Streamlit application down"
        # Send notification
    fi
    
    # Check database health
    if ! psql -U mcp_user -h localhost -d cmdb -c "SELECT 1;" > /dev/null 2>&1; then
        echo "ALERT: Database connection failed"
        # Send notification
    fi
    
    sleep 60
done
```

### Performance Monitoring

#### Database Performance
```sql
-- Query performance monitoring
CREATE VIEW query_performance AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC;

-- Connection monitoring
CREATE VIEW connection_stats AS
SELECT 
    datname,
    usename,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'cmdb';
```

#### Application Metrics
```python
# app_metrics.py
import time
import psutil
from dataclasses import dataclass

@dataclass
class ApplicationMetrics:
    cpu_percent: float
    memory_usage: int
    active_sessions: int
    query_count: int
    avg_response_time: float

def collect_metrics() -> ApplicationMetrics:
    process = psutil.Process()
    return ApplicationMetrics(
        cpu_percent=process.cpu_percent(),
        memory_usage=process.memory_info().rss,
        active_sessions=get_active_session_count(),
        query_count=get_query_count(),
        avg_response_time=get_avg_response_time()
    )
```

This runbook provides comprehensive operational guidance for maintaining a reliable, secure, and high-performing PostgreSQL MCP system. Regular use of these procedures will ensure optimal system health and user experience.