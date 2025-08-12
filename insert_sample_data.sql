-- =====================================================
-- CMDB Sample Data
-- =====================================================
-- This script populates the CMDB with realistic sample data
-- =====================================================

-- Connect to the database
\c cmdb;

-- =====================================================
-- INSERT DEPARTMENTS
-- =====================================================
INSERT INTO departments (name, code, manager, budget, cost_center, location, employee_count) VALUES
('Information Technology', 'IT', 'John Smith', 5000000.00, 'CC-100', 'Building A - Floor 3', 45),
('Finance', 'FIN', 'Sarah Johnson', 2000000.00, 'CC-200', 'Building A - Floor 2', 25),
('Human Resources', 'HR', 'Michael Brown', 1500000.00, 'CC-300', 'Building B - Floor 1', 15),
('Sales', 'SALES', 'Emily Davis', 3000000.00, 'CC-400', 'Building B - Floor 2', 60),
('Marketing', 'MKT', 'David Wilson', 2500000.00, 'CC-500', 'Building B - Floor 3', 30),
('Operations', 'OPS', 'Lisa Anderson', 4000000.00, 'CC-600', 'Building C - Floor 1', 80),
('Engineering', 'ENG', 'Robert Taylor', 6000000.00, 'CC-700', 'Building C - Floor 2', 120),
  ('Customer Support', 'SUP', 'Jennifer Martinez', 1800000.00, 'CC-800', 'Building A - Floor 1', 40)
ON CONFLICT DO NOTHING;

-- =====================================================
-- INSERT SERVERS
-- =====================================================
INSERT INTO servers (hostname, ip_address, server_type, operating_system, os_version, cpu_cores, memory_gb, storage_gb, 
                    environment, status, location, datacenter, rack_position, department_id, purchase_date, 
                    warranty_expires, cost, last_patched) VALUES
-- Production Web Servers
('web-prod-01', '10.10.10.11', 'physical', 'Ubuntu Linux', '22.04 LTS', 16, 64, 1000, 'production', 'active', 'Rack A1', 'DC-East', 'A1-U10', 1, '2023-01-15', '2026-01-15', 15000.00, '2024-12-01'),
('web-prod-02', '10.10.10.12', 'physical', 'Ubuntu Linux', '22.04 LTS', 16, 64, 1000, 'production', 'active', 'Rack A1', 'DC-East', 'A1-U11', 1, '2023-01-15', '2026-01-15', 15000.00, '2024-12-01'),
('web-prod-03', '10.10.10.13', 'virtual', 'Ubuntu Linux', '22.04 LTS', 8, 32, 500, 'production', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 1, '2023-06-01', '2026-06-01', 5000.00, '2024-12-01'),

-- Production Database Servers
('db-prod-01', '10.10.20.11', 'physical', 'Red Hat Linux', '8.6', 32, 256, 5000, 'production', 'active', 'Rack B1', 'DC-East', 'B1-U15', 1, '2022-05-20', '2025-05-20', 45000.00, '2024-11-15'),
('db-prod-02', '10.10.20.12', 'physical', 'Red Hat Linux', '8.6', 32, 256, 5000, 'production', 'active', 'Rack B1', 'DC-East', 'B1-U16', 1, '2022-05-20', '2025-05-20', 45000.00, '2024-11-15'),
('db-prod-replica', '10.10.20.13', 'physical', 'Red Hat Linux', '8.6', 32, 256, 5000, 'production', 'active', 'Rack B2', 'DC-West', 'B2-U10', 1, '2022-05-20', '2025-05-20', 45000.00, '2024-11-15'),

-- Application Servers
('app-prod-01', '10.10.30.11', 'virtual', 'Windows Server', '2022', 16, 64, 500, 'production', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 7, '2023-03-10', '2026-03-10', 8000.00, '2024-12-10'),
('app-prod-02', '10.10.30.12', 'virtual', 'Windows Server', '2022', 16, 64, 500, 'production', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 7, '2023-03-10', '2026-03-10', 8000.00, '2024-12-10'),
('app-prod-03', '10.10.30.13', 'cloud', 'Amazon Linux', '2023', 8, 32, 200, 'production', 'active', 'AWS us-east-1', 'AWS', 'Cloud', 7, '2024-01-01', NULL, 3000.00, '2024-12-15'),

-- Development/Test Servers
('dev-server-01', '10.20.10.11', 'virtual', 'Ubuntu Linux', '20.04 LTS', 4, 16, 200, 'development', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 7, '2023-08-01', '2026-08-01', 2000.00, '2024-11-01'),
('dev-server-02', '10.20.10.12', 'virtual', 'CentOS', '8', 4, 16, 200, 'development', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 7, '2023-08-01', '2026-08-01', 2000.00, '2024-11-01'),
('test-server-01', '10.20.20.11', 'virtual', 'Windows Server', '2019', 8, 32, 300, 'test', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 7, '2023-09-01', '2026-09-01', 3000.00, '2024-11-01'),

-- Infrastructure Servers
('mail-server-01', '10.10.40.11', 'physical', 'Windows Server', '2022', 8, 32, 2000, 'production', 'active', 'Rack C1', 'DC-East', 'C1-U20', 1, '2023-02-01', '2026-02-01', 12000.00, '2024-12-05'),
('backup-server-01', '10.10.50.11', 'physical', 'Ubuntu Linux', '22.04 LTS', 16, 64, 20000, 'production', 'active', 'Rack D1', 'DC-East', 'D1-U30', 1, '2022-10-01', '2025-10-01', 25000.00, '2024-11-20'),
('monitor-server-01', '10.10.60.11', 'virtual', 'Ubuntu Linux', '22.04 LTS', 8, 32, 500, 'production', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 1, '2023-11-01', '2026-11-01', 4000.00, '2024-12-01'),

-- Finance Department Servers
('fin-app-01', '10.30.10.11', 'virtual', 'Windows Server', '2022', 8, 32, 300, 'production', 'active', 'VMware Cluster', 'DC-East', 'Virtual', 2, '2023-04-01', '2026-04-01', 5000.00, '2024-12-08'),
('fin-db-01', '10.30.10.12', 'physical', 'Oracle Linux', '8', 16, 128, 3000, 'production', 'active', 'Rack E1', 'DC-East', 'E1-U10', 2, '2022-12-01', '2025-12-01', 35000.00, '2024-11-25'),

-- HR Department Servers
('hr-app-01', '10.40.10.11', 'cloud', 'Windows Server', '2022', 4, 16, 100, 'production', 'active', 'Azure East US', 'Azure', 'Cloud', 3, '2024-02-01', NULL, 1500.00, '2024-12-10'),

-- Decommissioned Server
('old-server-01', '10.99.99.99', 'physical', 'Windows Server', '2012', 4, 8, 500, 'production', 'decommissioned', 'Storage', 'DC-East', 'Retired', 1, '2015-01-01', '2018-01-01', 5000.00, '2020-01-01')
ON CONFLICT DO NOTHING;

-- =====================================================
-- INSERT APPLICATIONS
-- =====================================================
INSERT INTO applications (
  name, version, app_type, programming_language, framework, description,
  business_criticality, server_id, department_id, owner_email,
  port, url, environment, status, compliance_required, disaster_recovery,
  sla_tier, monthly_cost, user_count, last_deployment
) VALUES
-- Core Business Applications
('Corporate Website', '3.2.1', 'web', 'JavaScript', 'React', 'Main corporate website and customer portal', 'critical',
  (SELECT id FROM servers WHERE hostname = 'web-prod-01'),
  (SELECT id FROM departments WHERE name = 'Marketing'),
  'webmaster@company.com', 443, 'https://www.company.com', 'production', 'active', true, true, 1, 5000.00, 100000, '2024-12-01'),
('E-Commerce Platform', '5.1.0', 'web', 'Java', 'Spring Boot', 'Online shopping platform', 'critical',
  (SELECT id FROM servers WHERE hostname = 'web-prod-02'),
  (SELECT id FROM departments WHERE name = 'Sales'),
  'ecommerce@company.com', 443, 'https://shop.company.com', 'production', 'active', true, true, 1, 8000.00, 50000, '2024-11-28'),
('Customer Database', '12.2', 'database', 'SQL', 'PostgreSQL', 'Central customer information database', 'critical',
  (SELECT id FROM servers WHERE hostname = 'db-prod-01'),
  (SELECT id FROM departments WHERE name = 'Sales'),
  'dba@company.com', 5432, NULL, 'production', 'active', true, true, 1, 3000.00, NULL, '2024-10-15'),

-- Financial Applications
('ERP System', '2023.4', 'web', 'Java', 'Oracle', 'Enterprise Resource Planning system', 'critical',
  (SELECT id FROM servers WHERE hostname = 'fin-db-01'),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'erp.admin@company.com', 8080, 'https://erp.company.local', 'production', 'active', true, true, 1, 15000.00, 500, '2024-11-20'),
('Payroll System', '8.5.2', 'web', 'C#', '.NET', 'Employee payroll management', 'critical',
  (SELECT id FROM servers WHERE hostname = 'fin-app-01'),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'payroll@company.com', 443, 'https://payroll.company.local', 'production', 'active', true, true, 1, 5000.00, 50, '2024-12-05'),
('Expense Tracker', '2.1.0', 'web', 'Python', 'Django', 'Employee expense submission and approval', 'medium',
  (SELECT id FROM servers WHERE hostname = 'fin-app-01'),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'expenses@company.com', 8000, 'https://expenses.company.local', 'production', 'active', false, false, 3, 1000.00, 200, '2024-11-15'),

-- HR Applications
('HRIS', '15.2', 'web', 'Ruby', 'Rails', 'Human Resources Information System', 'high',
  (SELECT id FROM servers WHERE hostname = 'hr-app-01'),
  (SELECT id FROM departments WHERE name = 'Human Resources'),
  'hr.systems@company.com', 3000, 'https://hr.company.local', 'production', 'active', true, true, 2, 4000.00, 150, '2024-11-01'),
('Recruitment Portal', '3.0.1', 'web', 'PHP', 'Laravel', 'Job posting and application tracking', 'medium',
  (SELECT id FROM servers WHERE hostname = 'hr-app-01'),
  (SELECT id FROM departments WHERE name = 'Human Resources'),
  'recruitment@company.com', 443, 'https://careers.company.com', 'production', 'active', false, false, 3, 2000.00, 5000, '2024-10-20'),

-- IT Applications
('Service Desk', '7.2.1', 'web', 'Python', 'Flask', 'IT ticketing and support system', 'high',
  (SELECT id FROM servers WHERE hostname = 'app-prod-01'),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'servicedesk@company.com', 5000, 'https://helpdesk.company.local', 'production', 'active', false, true, 2, 3000.00, 300, '2024-12-10'),
('Monitoring Dashboard', '4.5.0', 'monitoring', 'Go', 'Grafana', 'Infrastructure monitoring and alerting', 'critical',
  (SELECT id FROM servers WHERE hostname = 'monitor-server-01'),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'monitoring@company.com', 3000, 'https://monitor.company.local', 'production', 'active', false, true, 1, 1500.00, 50, '2024-12-12'),
('Backup Manager', '10.1', 'batch', 'Python', 'Custom', 'Automated backup orchestration', 'critical',
  (SELECT id FROM servers WHERE hostname = 'backup-server-01'),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'backup.admin@company.com', NULL, NULL, 'production', 'active', false, true, 1, 500.00, 5, '2024-11-30'),

-- Development/Test Applications
('CI/CD Pipeline', '2.3.0', 'api', 'JavaScript', 'Jenkins', 'Continuous Integration and Deployment', 'high',
  (SELECT id FROM servers WHERE hostname = 'dev-server-01'),
  (SELECT id FROM departments WHERE name = 'Engineering'),
  'devops@company.com', 8080, 'https://jenkins.company.local', 'development', 'active', false, false, 2, 2000.00, 100, '2024-12-14'),
('Test Data Generator', '1.0.5', 'batch', 'Python', 'Custom', 'Generate test data for QA', 'low',
  (SELECT id FROM servers WHERE hostname = 'dev-server-02'),
  (SELECT id FROM departments WHERE name = 'Engineering'),
  'qa@company.com', NULL, NULL, 'development', 'active', false, false, 4, 100.00, 20, '2024-11-10'),
('Code Repository', '3.14.0', 'web', 'Ruby', 'GitLab', 'Source code management', 'critical',
  (SELECT id FROM servers WHERE hostname = 'dev-server-01'),
  (SELECT id FROM departments WHERE name = 'Engineering'),
  'git.admin@company.com', 443, 'https://git.company.local', 'development', 'active', false, true, 1, 1000.00, 150, '2024-12-08'),

-- Email and Communication
('Email Server', '2022.2', 'middleware', 'Various', 'Exchange', 'Corporate email system', 'critical',
  (SELECT id FROM servers WHERE hostname = 'mail-server-01'),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'mail.admin@company.com', 25, NULL, 'production', 'active', true, true, 1, 8000.00, 500, '2024-11-25'),
('Team Chat', '5.42.0', 'web', 'JavaScript', 'Slack', 'Internal team communication', 'high',
  (SELECT id FROM servers WHERE hostname = 'app-prod-02'),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'chat.admin@company.com', 443, 'https://company.slack.com', 'production', 'active', false, false, 2, 3000.00, 450, '2024-12-01'),

-- Analytics
('Business Intelligence', '2024.1', 'web', 'Various', 'PowerBI', 'Business analytics and reporting', 'high',
  (SELECT id FROM servers WHERE hostname = 'app-prod-03'),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'bi@company.com', 443, 'https://bi.company.local', 'production', 'active', false, true, 2, 5000.00, 100, '2024-11-18'),
('Data Warehouse', '3.0', 'database', 'SQL', 'Snowflake', 'Central data warehouse', 'high',
  (SELECT id FROM servers WHERE hostname = 'db-prod-02'),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'datawarehouse@company.com', 443, NULL, 'production', 'active', true, true, 2, 10000.00, NULL, '2024-10-30'),

-- Deprecated Application
('Legacy System', '1.0', 'web', 'COBOL', 'Custom', 'Old inventory system', 'low',
  (SELECT id FROM servers WHERE hostname = 'old-server-01'),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'legacy@company.com', 8080, NULL, 'production', 'deprecated', false, false, 4, 500.00, 5, '2020-01-01'),

-- Extra application to reach 20
('Analytics API', '1.4.2', 'api', 'Python', 'FastAPI', 'Provides analytics endpoints for BI', 'high',
  (SELECT id FROM servers WHERE hostname = 'app-prod-03'),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'analytics@company.com', 9000, 'https://api.bi.company.local', 'production', 'active', false, true, 2, 2500.00, 200, '2024-12-12')
ON CONFLICT DO NOTHING;

-- =====================================================
-- INSERT INCIDENTS
-- =====================================================
INSERT INTO incidents (
  incident_number, title, description, severity, status, server_id, application_id,
  department_id, reported_by, assigned_to, reported_at, resolved_at, closed_at,
  resolution_time_hours, root_cause, resolution, impact, affected_users, downtime_minutes
) VALUES
-- Recent Critical Incidents
('INC-2024-001', 'Database Connection Pool Exhausted', 'Production database running out of connections', 'critical', 'closed',
  (SELECT id FROM servers WHERE hostname = 'db-prod-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Customer Database' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'monitor@company.com', 'John Doe', '2024-12-01 03:00:00', '2024-12-01 04:30:00', '2024-12-01 05:00:00', 1.5,
  'Application not closing connections properly', 'Increased connection pool size and fixed application code', 'enterprise', 500, 90),
('INC-2024-002', 'Website Down - 500 Errors', 'Corporate website showing 500 internal server errors', 'critical', 'closed',
  (SELECT id FROM servers WHERE hostname = 'web-prod-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Corporate Website' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Marketing'),
  'support@company.com', 'Jane Smith', '2024-12-05 14:00:00', '2024-12-05 14:45:00', '2024-12-05 15:00:00', 0.75,
  'Memory leak in application', 'Restarted application and applied hotfix', 'enterprise', 10000, 45),

-- High Priority Incidents
('INC-2024-003', 'Email Delays', 'Emails taking 30+ minutes to deliver', 'high', 'closed',
  (SELECT id FROM servers WHERE hostname = 'mail-server-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Email Server' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'user1@company.com', 'Mike Johnson', '2024-12-08 09:00:00', '2024-12-08 11:00:00', '2024-12-08 12:00:00', 2.0,
  'Mail queue backlog', 'Cleared queue and optimized mail rules', 'department', 200, 0),
('INC-2024-004', 'Slow ERP Performance', 'ERP system responding slowly', 'high', 'resolved',
  (SELECT id FROM servers WHERE hostname = 'fin-db-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'ERP System' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'finance@company.com', 'Sarah Lee', '2024-12-10 10:00:00', '2024-12-10 14:00:00', NULL, 4.0,
  'Database index fragmentation', 'Rebuilt database indexes', 'department', 50, 0),

-- Medium Priority Incidents
('INC-2024-005', 'Backup Job Failed', 'Nightly backup did not complete', 'medium', 'closed',
  (SELECT id FROM servers WHERE hostname = 'backup-server-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Backup Manager' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'monitor@company.com', 'Tom Wilson', '2024-12-09 06:00:00', '2024-12-09 08:00:00', '2024-12-09 09:00:00', 2.0,
  'Insufficient disk space', 'Cleaned up old backups and increased storage', 'team', 0, 0),
('INC-2024-006', 'Cannot Access Test Server', 'Development team cannot connect to test server', 'medium', 'closed',
  (SELECT id FROM servers WHERE hostname = 'test-server-01' LIMIT 1),
  NULL,
  (SELECT id FROM departments WHERE name = 'Engineering'),
  'dev1@company.com', 'Alice Brown', '2024-12-11 13:00:00', '2024-12-11 14:00:00', '2024-12-11 14:30:00', 1.0,
  'Firewall rule changed', 'Updated firewall rules', 'team', 10, 0),
('INC-2024-007', 'Report Generation Error', 'BI reports failing to generate', 'medium', 'in_progress',
  (SELECT id FROM servers WHERE hostname = 'app-prod-02' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Business Intelligence' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'analyst@company.com', 'Bob Martin', '2024-12-12 11:00:00', NULL, NULL, NULL,
  NULL, NULL, 'team', 20, 0),

-- Low Priority Incidents
('INC-2024-008', 'Printer Not Working', 'Finance printer offline', 'low', 'closed',
  NULL, NULL, (SELECT id FROM departments WHERE name = 'Finance'),
  'user2@company.com', 'IT Support', '2024-12-07 15:00:00', '2024-12-07 16:00:00', '2024-12-07 16:00:00', 1.0,
  'Paper jam', 'Cleared paper jam', 'individual', 1, 0),
('INC-2024-009', 'Password Reset Request', 'User locked out of account', 'low', 'closed',
  NULL, (SELECT id FROM applications WHERE name = 'HRIS' ORDER BY id LIMIT 1), (SELECT id FROM departments WHERE name = 'Human Resources'),
  'user3@company.com', 'IT Support', '2024-12-11 09:30:00', '2024-12-11 09:45:00', '2024-12-11 09:45:00', 0.25,
  'Forgot password', 'Reset password', 'individual', 1, 0),
('INC-2024-010', 'Software Installation', 'Need Python installed on workstation', 'low', 'closed',
  NULL, NULL, (SELECT id FROM departments WHERE name = 'Engineering'),
  'dev2@company.com', 'Desktop Support', '2024-12-13 14:00:00', '2024-12-13 15:00:00', '2024-12-13 15:00:00', 1.0,
  'New requirement', 'Installed Python 3.11', 'individual', 1, 0),

-- Open/In Progress Incidents
('INC-2024-011', 'Disk Space Warning', 'Server running low on disk space', 'medium', 'open',
  (SELECT id FROM servers WHERE hostname = 'db-prod-02' LIMIT 1),
  NULL, (SELECT id FROM departments WHERE name = 'Information Technology'),
  'monitor@company.com', 'John Doe', '2024-12-14 08:00:00', NULL, NULL, NULL,
  NULL, NULL, 'team', 0, 0),
('INC-2024-012', 'SSL Certificate Expiring', 'SSL certificate expires in 7 days', 'high', 'in_progress',
  (SELECT id FROM servers WHERE hostname = 'web-prod-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Corporate Website' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'security@company.com', 'Security Team', '2024-12-14 09:00:00', NULL, NULL, NULL,
  NULL, NULL, 'enterprise', 0, 0),
('INC-2024-013', 'Application Memory Leak', 'Memory usage increasing over time', 'medium', 'open',
  (SELECT id FROM servers WHERE hostname = 'app-prod-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'ERP System' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'monitor@company.com', 'Dev Team', '2024-12-14 10:00:00', NULL, NULL, NULL,
  NULL, NULL, 'department', 0, 0),
('INC-2024-014', 'Network Latency', 'High latency to cloud servers', 'medium', 'open',
  (SELECT id FROM servers WHERE hostname = 'app-prod-03' LIMIT 1),
  NULL, (SELECT id FROM departments WHERE name = 'Information Technology'),
  'network@company.com', 'Network Team', '2024-12-14 11:00:00', NULL, NULL, NULL,
  NULL, NULL, 'department', 30, 0),
('INC-2024-015', 'Failed Login Attempts', 'Multiple failed login attempts detected', 'high', 'open',
  NULL, (SELECT id FROM applications WHERE name = 'ERP System' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Finance'),
  'security@company.com', 'Security Team', '2024-12-14 14:00:00', NULL, NULL, NULL,
  NULL, NULL, 'department', 1, 0),

-- Additional incidents to reach at least 20
('INC-2024-016', 'CI/CD Pipeline Failure', 'Builds failing across multiple projects', 'high', 'open',
  (SELECT id FROM servers WHERE hostname = 'dev-server-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'CI/CD Pipeline' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Engineering'),
  'devops@company.com', 'DevOps Team', '2024-12-14 15:00:00', NULL, NULL, NULL,
  'Configuration error in Jenkins plugin', NULL, 'department', 0, 0),
('INC-2024-017', 'Payment Service Timeout', 'Timeouts in checkout flow', 'critical', 'resolved',
  (SELECT id FROM servers WHERE hostname = 'web-prod-02' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'E-Commerce Platform' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Sales'),
  'support@company.com', 'E-Comm Team', '2024-12-13 18:30:00', '2024-12-13 19:10:00', '2024-12-13 19:30:00', 0.67,
  'Downstream payment gateway latency', 'Switched to secondary gateway', 'enterprise', 2000, 20),
('INC-2024-018', 'HR Portal Login Error', 'Users receive authentication errors', 'medium', 'closed',
  (SELECT id FROM servers WHERE hostname = 'hr-app-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'HRIS' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Human Resources'),
  'hr.support@company.com', 'HR IT', '2024-12-12 09:00:00', '2024-12-12 09:40:00', '2024-12-12 10:00:00', 0.67,
  'OAuth misconfiguration', 'Corrected redirect URIs', 'department', 120, 0),
('INC-2024-019', 'Monitoring Alert Storm', 'Excessive alerts due to misconfigured thresholds', 'medium', 'open',
  (SELECT id FROM servers WHERE hostname = 'monitor-server-01' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Monitoring Dashboard' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Information Technology'),
  'monitor@company.com', 'SRE Team', '2024-12-14 07:30:00', NULL, NULL, NULL,
  NULL, NULL, 'team', 0, 0),
('INC-2024-020', 'BI Data Refresh Failed', 'Nightly refresh job failed', 'high', 'in_progress',
  (SELECT id FROM servers WHERE hostname = 'app-prod-03' LIMIT 1),
  (SELECT id FROM applications WHERE name = 'Business Intelligence' ORDER BY id LIMIT 1),
  (SELECT id FROM departments WHERE name = 'Operations'),
  'bi@company.com', 'Data Team', '2024-12-14 02:00:00', NULL, NULL, NULL,
  'ETL pipeline step failed', NULL, 'department', 0, 0)
ON CONFLICT DO NOTHING;

-- =====================================================
-- INSERT RELATIONSHIPS
-- =====================================================
INSERT INTO relationships (parent_type, parent_id, child_type, child_id, relationship_type, description, criticality) VALUES
-- Web apps depend on database
('application', (SELECT id FROM applications WHERE name = 'Corporate Website'),
  'application', (SELECT id FROM applications WHERE name = 'Customer Database'), 'depends_on', 'Website depends on customer database', 'critical'),
('application', (SELECT id FROM applications WHERE name = 'E-Commerce Platform'),
  'application', (SELECT id FROM applications WHERE name = 'Customer Database'), 'depends_on', 'E-commerce platform depends on customer database', 'critical'),

-- Applications hosted on servers
('server', (SELECT id FROM servers WHERE hostname = 'web-prod-01'), 'application', (SELECT id FROM applications WHERE name = 'Corporate Website'), 'hosts', 'Web server hosts corporate website', 'critical'),
('server', (SELECT id FROM servers WHERE hostname = 'web-prod-02'), 'application', (SELECT id FROM applications WHERE name = 'E-Commerce Platform'), 'hosts', 'Web server hosts e-commerce platform', 'critical'),
('server', (SELECT id FROM servers WHERE hostname = 'db-prod-01'), 'application', (SELECT id FROM applications WHERE name = 'Customer Database'), 'hosts', 'Database server hosts customer database', 'critical'),

-- Database replication
('server', (SELECT id FROM servers WHERE hostname = 'db-prod-01'), 'server', (SELECT id FROM servers WHERE hostname = 'db-prod-02'), 'replicates_to', 'Primary database replicates to standby', 'critical'),
('server', (SELECT id FROM servers WHERE hostname = 'db-prod-02'), 'server', (SELECT id FROM servers WHERE hostname = 'db-prod-replica'), 'replicates_to', 'Standby replicates to DR site', 'high'),

-- Load balancing
('server', (SELECT id FROM servers WHERE hostname = 'web-prod-01'), 'server', (SELECT id FROM servers WHERE hostname = 'web-prod-02'), 'load_balances', 'Web traffic load balanced between servers', 'high'),
('server', (SELECT id FROM servers WHERE hostname = 'web-prod-02'), 'server', (SELECT id FROM servers WHERE hostname = 'web-prod-03'), 'load_balances', 'Web traffic load balanced between servers', 'high'),

-- Monitoring relationships
('server', (SELECT id FROM servers WHERE hostname = 'monitor-server-01'), 'server', (SELECT id FROM servers WHERE hostname = 'web-prod-01'), 'monitors', 'Monitoring server monitors web server', 'medium'),
('server', (SELECT id FROM servers WHERE hostname = 'monitor-server-01'), 'server', (SELECT id FROM servers WHERE hostname = 'db-prod-01'), 'monitors', 'Monitoring server monitors database', 'high'),
('server', (SELECT id FROM servers WHERE hostname = 'monitor-server-01'), 'application', (SELECT id FROM applications WHERE name = 'Monitoring Dashboard'), 'monitors', 'Monitoring server monitors all applications', 'medium'),

-- Backup relationships
('server', (SELECT id FROM servers WHERE hostname = 'backup-server-01'), 'server', (SELECT id FROM servers WHERE hostname = 'db-prod-01'), 'backs_up', 'Backup server backs up main database', 'critical'),
('server', (SELECT id FROM servers WHERE hostname = 'backup-server-01'), 'server', (SELECT id FROM servers WHERE hostname = 'fin-db-01'), 'backs_up', 'Backup server backs up financial systems', 'critical'),
('application', (SELECT id FROM applications WHERE name = 'Backup Manager'), 'application', (SELECT id FROM applications WHERE name = 'Customer Database'), 'backs_up', 'Backup manager orchestrates database backups', 'critical'),

-- Application dependencies
('application', (SELECT id FROM applications WHERE name = 'ERP System'), 'application', (SELECT id FROM applications WHERE name = 'Customer Database'), 'depends_on', 'ERP depends on customer database', 'high'),
('application', (SELECT id FROM applications WHERE name = 'Payroll System'), 'application', (SELECT id FROM applications WHERE name = 'ERP System'), 'depends_on', 'Payroll depends on ERP system', 'critical'),
('application', (SELECT id FROM applications WHERE name = 'CI/CD Pipeline'), 'application', (SELECT id FROM applications WHERE name = 'Code Repository'), 'uses', 'CI/CD uses code repository', 'high'),
('application', (SELECT id FROM applications WHERE name = 'Business Intelligence'), 'application', (SELECT id FROM applications WHERE name = 'Data Warehouse'), 'connects_to', 'BI connects to data warehouse', 'high')
ON CONFLICT DO NOTHING;

-- =====================================================
-- CREATE SUMMARY STATISTICS
-- =====================================================

-- Create a dashboard view for quick stats
CREATE OR REPLACE VIEW cmdb_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM servers WHERE status = 'active') as active_servers,
    (SELECT COUNT(*) FROM servers WHERE status = 'maintenance') as maintenance_servers,
    (SELECT COUNT(*) FROM applications WHERE status = 'active') as active_applications,
    (SELECT COUNT(*) FROM incidents WHERE status IN ('open', 'in_progress')) as open_incidents,
    (SELECT COUNT(*) FROM incidents WHERE severity = 'critical' AND status IN ('open', 'in_progress')) as critical_incidents,
    (SELECT AVG(resolution_time_hours) FROM incidents WHERE status = 'closed' AND reported_at > CURRENT_DATE - INTERVAL '30 days') as avg_resolution_hours,
    (SELECT COUNT(DISTINCT department_id) FROM servers) as departments_with_servers,
    (SELECT SUM(cost) FROM servers WHERE status = 'active') as total_server_investment;

-- Show summary
SELECT * FROM cmdb_dashboard;

-- Show table counts
SELECT 
    'Summary of CMDB Data:' as info
UNION ALL
SELECT '-------------------'
UNION ALL
SELECT 'Departments: ' || COUNT(*)::text FROM departments
UNION ALL
SELECT 'Servers: ' || COUNT(*)::text FROM servers
UNION ALL
SELECT 'Applications: ' || COUNT(*)::text FROM applications
UNION ALL
SELECT 'Incidents: ' || COUNT(*)::text FROM incidents
UNION ALL
SELECT 'Relationships: ' || COUNT(*)::text FROM relationships;