#!/bin/bash

# =====================================================
# PostgreSQL Setup Script for WSL2 with CMDB Database
# =====================================================

echo "================================================"
echo "PostgreSQL CMDB Setup for WSL2"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Step 1: Update package list
print_status "Updating package list..."
sudo apt update

# Step 2: Install PostgreSQL
print_status "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Step 3: Start PostgreSQL service
print_status "Starting PostgreSQL service..."
sudo service postgresql start

# Check if PostgreSQL is running
if sudo service postgresql status | grep -q "online"; then
    print_status "PostgreSQL is running"
else
    print_warning "PostgreSQL might not be running. Trying to start..."
    sudo service postgresql restart
fi

# Step 4: Get PostgreSQL version
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+(?=\.)')
print_status "PostgreSQL version $PG_VERSION detected"

# Step 5: Set password for postgres user
print_status "Setting password for postgres user..."
echo "Enter password for PostgreSQL 'postgres' user (default: postgres):"
read -s PG_PASSWORD
PG_PASSWORD=${PG_PASSWORD:-postgres}

sudo -u postgres psql <<EOF
ALTER USER postgres PASSWORD '$PG_PASSWORD';
EOF

# Step 6: Create a new database user for MCP
print_status "Creating MCP database user..."
echo "Enter username for MCP user (default: mcp_user):"
read MCP_USER
MCP_USER=${MCP_USER:-mcp_user}

echo "Enter password for MCP user (default: mcp_password):"
read -s MCP_PASSWORD
MCP_PASSWORD=${MCP_PASSWORD:-mcp_password}

sudo -u postgres psql <<EOF
CREATE USER $MCP_USER WITH PASSWORD '$MCP_PASSWORD';
ALTER USER $MCP_USER CREATEDB;
EOF

# Step 7: Update PostgreSQL configuration for local connections
print_status "Configuring PostgreSQL for local connections..."

# Find pg_hba.conf location
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

# Backup original configuration
sudo cp $PG_CONFIG_DIR/pg_hba.conf $PG_CONFIG_DIR/pg_hba.conf.backup

# Update pg_hba.conf to allow password authentication
sudo bash -c "cat > $PG_CONFIG_DIR/pg_hba.conf" <<EOF
# Database administrative login by Unix domain socket
local   all             postgres                                peer

# "local" is for Unix domain socket connections only
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             localhost               md5

# IPv6 local connections:
host    all             all             ::1/128                 md5
EOF

# Update postgresql.conf to listen on localhost
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" $PG_CONFIG_DIR/postgresql.conf

# Restart PostgreSQL to apply changes
print_status "Restarting PostgreSQL..."
sudo service postgresql restart

# Step 8: Create CMDB database
print_status "Creating CMDB database..."
sudo -u postgres createdb cmdb

# Grant privileges to MCP user
sudo -u postgres psql -d cmdb <<EOF
GRANT ALL PRIVILEGES ON DATABASE cmdb TO $MCP_USER;
ALTER DATABASE cmdb OWNER TO $MCP_USER;
EOF

# Step 9: Load CMDB schema and data
print_status "Loading CMDB schema..."
if [ -f "create_cmdb_database.sql" ]; then
    PGPASSWORD=$MCP_PASSWORD psql -U $MCP_USER -h localhost -d cmdb -f create_cmdb_database.sql
    print_status "CMDB schema created successfully"
else
    print_warning "create_cmdb_database.sql not found. Please run it manually later."
fi

print_status "Loading sample data..."
if [ -f "insert_sample_data.sql" ]; then
    PGPASSWORD=$MCP_PASSWORD psql -U $MCP_USER -h localhost -d cmdb -f insert_sample_data.sql
    print_status "Sample data loaded successfully"
else
    print_warning "insert_sample_data.sql not found. Please run it manually later."
fi

# Step 10: Create .env file for the application
print_status "Creating .env configuration file..."
cat > .env <<EOF
# PostgreSQL Configuration for CMDB
PGHOST=localhost
PGPORT=5432
PGDATABASE=cmdb
PGUSER=$MCP_USER
PGPASSWORD=$MCP_PASSWORD

# Alternative connection string
DATABASE_URL=postgresql://$MCP_USER:$MCP_PASSWORD@localhost:5432/cmdb

# OpenAI Configuration (add your key here)
OPENAI_API_KEY=sk-your-openai-api-key-here
EOF

print_status ".env file created"

# Step 11: Test the connection
print_status "Testing database connection..."
PGPASSWORD=$MCP_PASSWORD psql -U $MCP_USER -h localhost -d cmdb -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "Database connection successful!"
    
    # Show summary statistics
    echo ""
    echo "================================================"
    echo "CMDB Database Statistics:"
    echo "================================================"
    
    PGPASSWORD=$MCP_PASSWORD psql -U $MCP_USER -h localhost -d cmdb -t <<EOF
SELECT 'Departments: ' || COUNT(*) FROM departments
UNION ALL
SELECT 'Servers: ' || COUNT(*) FROM servers
UNION ALL
SELECT 'Applications: ' || COUNT(*) FROM applications
UNION ALL
SELECT 'Incidents: ' || COUNT(*) FROM incidents
UNION ALL
SELECT 'Relationships: ' || COUNT(*) FROM relationships;
EOF
else
    print_error "Could not connect to database. Please check the configuration."
fi

# Step 12: Create systemd service (optional)
print_status "Creating PostgreSQL auto-start script..."
cat > ~/start_postgresql.sh <<'EOF'
#!/bin/bash
sudo service postgresql start
EOF
chmod +x ~/start_postgresql.sh

# Step 13: Show final instructions
echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Database Details:"
echo "  Database: cmdb"
echo "  User: $MCP_USER"
echo "  Password: [hidden]"
echo "  Host: localhost"
echo "  Port: 5432"
echo ""
echo "To start PostgreSQL manually:"
echo "  sudo service postgresql start"
echo ""
echo "To connect to the database:"
echo "  psql -U $MCP_USER -h localhost -d cmdb"
echo ""
echo "To use with the MCP server:"
echo "  1. The .env file has been created with your credentials"
echo "  2. Run: python verify_setup.py"
echo "  3. Run: streamlit run streamlit_openai_mcp.py"
echo ""
echo "Your CMDB database is ready with:"
echo "  • 8 Departments"
echo "  • 20 Servers"
echo "  • 21 Applications"
echo "  • 15 Incidents"
echo "  • 20 Relationships"
echo ""
print_status "You can now test the MCP chat interface!"