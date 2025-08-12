-- =====================================================
-- CMDB (Configuration Management Database) Schema
-- =====================================================
-- This script creates a complete CMDB with:
-- 1. Servers (physical and virtual infrastructure)
-- 2. Applications (software and services)
-- 3. Departments (organizational units)
-- 4. Incidents (issues and problems)
-- 5. Relationships (dependencies between components)
-- =====================================================

-- Drop existing database if it exists (be careful!)
-- DROP DATABASE IF EXISTS cmdb;

-- Create the database
CREATE DATABASE cmdb;

-- Connect to the database
\c cmdb;

-- Enable UUID extension for better IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. DEPARTMENTS TABLE
-- =====================================================
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    manager VARCHAR(100),
    budget DECIMAL(12, 2),
    cost_center VARCHAR(20),
    location VARCHAR(100),
    employee_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. SERVERS TABLE
-- =====================================================
CREATE TABLE servers (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    ip_address INET NOT NULL,
    server_type VARCHAR(20) CHECK (server_type IN ('physical', 'virtual', 'cloud', 'container')),
    operating_system VARCHAR(100),
    os_version VARCHAR(50),
    cpu_cores INTEGER,
    memory_gb INTEGER,
    storage_gb INTEGER,
    environment VARCHAR(20) CHECK (environment IN ('production', 'staging', 'development', 'test', 'dr')),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'maintenance', 'decommissioned')),
    location VARCHAR(100),
    datacenter VARCHAR(50),
    rack_position VARCHAR(20),
    department_id INTEGER REFERENCES departments(id),
    purchase_date DATE,
    warranty_expires DATE,
    cost DECIMAL(10, 2),
    last_patched DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monitored BOOLEAN DEFAULT true,
    backup_enabled BOOLEAN DEFAULT true,
    notes TEXT
);

-- Create indexes for common queries
CREATE INDEX idx_servers_status ON servers(status);
CREATE INDEX idx_servers_environment ON servers(environment);
CREATE INDEX idx_servers_department ON servers(department_id);

-- =====================================================
-- 3. APPLICATIONS TABLE
-- =====================================================
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50),
    app_type VARCHAR(50) CHECK (app_type IN ('web', 'database', 'api', 'batch', 'middleware', 'monitoring')),
    programming_language VARCHAR(50),
    framework VARCHAR(50),
    description TEXT,
    business_criticality VARCHAR(20) CHECK (business_criticality IN ('critical', 'high', 'medium', 'low')),
    server_id INTEGER REFERENCES servers(id) ON DELETE SET NULL,
    department_id INTEGER REFERENCES departments(id),
    owner_email VARCHAR(100),
    repository_url VARCHAR(255),
    documentation_url VARCHAR(255),
    port INTEGER,
    url VARCHAR(255),
    environment VARCHAR(20) CHECK (environment IN ('production', 'staging', 'development', 'test')),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'deprecated', 'development')),
    compliance_required BOOLEAN DEFAULT false,
    disaster_recovery BOOLEAN DEFAULT false,
    sla_tier INTEGER CHECK (sla_tier IN (1, 2, 3, 4)),
    monthly_cost DECIMAL(10, 2),
    user_count INTEGER,
    last_deployment DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_applications_server ON applications(server_id);
CREATE INDEX idx_applications_department ON applications(department_id);
CREATE INDEX idx_applications_criticality ON applications(business_criticality);
CREATE INDEX idx_applications_status ON applications(status);
-- Ensure logical uniqueness for sample data loads
CREATE UNIQUE INDEX IF NOT EXISTS ux_applications_name ON applications(name);

-- =====================================================
-- 4. INCIDENTS TABLE
-- =====================================================
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    incident_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'resolved', 'closed', 'cancelled')),
    server_id INTEGER REFERENCES servers(id) ON DELETE SET NULL,
    application_id INTEGER REFERENCES applications(id) ON DELETE SET NULL,
    department_id INTEGER REFERENCES departments(id),
    reported_by VARCHAR(100),
    assigned_to VARCHAR(100),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    resolution_time_hours DECIMAL(8, 2),
    root_cause TEXT,
    resolution TEXT,
    impact VARCHAR(20) CHECK (impact IN ('enterprise', 'department', 'team', 'individual')),
    affected_users INTEGER,
    downtime_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_server ON incidents(server_id);
CREATE INDEX idx_incidents_application ON incidents(application_id);
CREATE INDEX idx_incidents_reported_at ON incidents(reported_at);

-- =====================================================
-- 5. RELATIONSHIPS TABLE (Asset Dependencies)
-- =====================================================
CREATE TABLE relationships (
    id SERIAL PRIMARY KEY,
    parent_type VARCHAR(20) CHECK (parent_type IN ('server', 'application')),
    parent_id INTEGER NOT NULL,
    child_type VARCHAR(20) CHECK (child_type IN ('server', 'application')),
    child_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) CHECK (relationship_type IN (
        'depends_on', 'hosts', 'connects_to', 'uses', 'backs_up', 
        'load_balances', 'replicates_to', 'monitors'
    )),
    description TEXT,
    criticality VARCHAR(20) CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_type, parent_id, child_type, child_id, relationship_type)
);

-- =====================================================
-- 6. AUDIT LOG TABLE (Track Changes)
-- =====================================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) CHECK (action IN ('insert', 'update', 'delete')),
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_values JSONB,
    new_values JSONB
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: Server Overview
CREATE VIEW server_overview AS
SELECT 
    s.hostname,
    s.ip_address,
    s.server_type,
    s.environment,
    s.status,
    d.name as department,
    COUNT(DISTINCT a.id) as app_count,
    COUNT(DISTINCT i.id) as incident_count
FROM servers s
LEFT JOIN departments d ON s.department_id = d.id
LEFT JOIN applications a ON a.server_id = s.id
LEFT JOIN incidents i ON i.server_id = s.id
GROUP BY s.id, s.hostname, s.ip_address, s.server_type, s.environment, s.status, d.name;

-- View: Application Health
CREATE VIEW application_health AS
SELECT 
    a.name as application,
    a.version,
    a.business_criticality,
    a.status,
    s.hostname as server,
    d.name as department,
    COUNT(i.id) as total_incidents,
    COUNT(CASE WHEN i.status IN ('open', 'in_progress') THEN 1 END) as open_incidents
FROM applications a
LEFT JOIN servers s ON a.server_id = s.id
LEFT JOIN departments d ON a.department_id = d.id
LEFT JOIN incidents i ON i.application_id = a.id
GROUP BY a.id, a.name, a.version, a.business_criticality, a.status, s.hostname, d.name;

-- View: Department Summary
CREATE VIEW department_summary AS
SELECT 
    d.name as department,
    d.code,
    COUNT(DISTINCT s.id) as server_count,
    COUNT(DISTINCT a.id) as application_count,
    COUNT(DISTINCT i.id) as incident_count,
    SUM(s.cost) as total_server_cost,
    SUM(a.monthly_cost) * 12 as annual_app_cost
FROM departments d
LEFT JOIN servers s ON s.department_id = d.id
LEFT JOIN applications a ON a.department_id = d.id
LEFT JOIN incidents i ON i.department_id = d.id
GROUP BY d.id, d.name, d.code;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function to calculate incident metrics
CREATE OR REPLACE FUNCTION get_incident_metrics(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_incidents BIGINT,
    avg_resolution_hours NUMERIC,
    critical_incidents BIGINT,
    total_downtime_hours NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_incidents,
        AVG(resolution_time_hours) as avg_resolution_hours,
        COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_incidents,
        SUM(downtime_minutes) / 60.0 as total_downtime_hours
    FROM incidents
    WHERE reported_at BETWEEN start_date AND end_date;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all main tables
CREATE TRIGGER update_servers_updated_at BEFORE UPDATE ON servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- GRANT PERMISSIONS (for read-only user)
-- =====================================================
-- Create a read-only user for the MCP server (optional)
-- CREATE USER mcp_reader WITH PASSWORD 'mcp_password';
-- GRANT CONNECT ON DATABASE cmdb TO mcp_reader;
-- GRANT USAGE ON SCHEMA public TO mcp_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_reader;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO mcp_reader;