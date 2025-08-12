#!/usr/bin/env python3
"""
Test CMDB Database with Sample Queries
This script tests your CMDB setup and shows example queries.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()


async def test_cmdb():
    """Test CMDB database with various queries."""
    
    # Connection details
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    database = os.getenv('PGDATABASE', 'cmdb')
    user = os.getenv('PGUSER', 'mcp_user')
    password = os.getenv('PGPASSWORD', 'mcp_password')
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        console.print(Panel.fit(
            "[bold green]✅ Connected to CMDB Database![/bold green]",
            border_style="green"
        ))
        
        # Test 1: Count records in each table
        console.print("\n[bold cyan]📊 Table Statistics:[/bold cyan]")
        
        tables = ['departments', 'servers', 'applications', 'incidents', 'relationships']
        stats_table = Table(show_header=True)
        stats_table.add_column("Table", style="cyan")
        stats_table.add_column("Record Count", style="green")
        
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            stats_table.add_row(table.capitalize(), str(count))
        
        console.print(stats_table)
        
        # Test 2: Production servers
        console.print("\n[bold cyan]🖥️ Production Servers:[/bold cyan]")
        
        servers = await conn.fetch("""
            SELECT hostname, ip_address, server_type, operating_system, status
            FROM servers 
            WHERE environment = 'production' AND status = 'active'
            LIMIT 5
        """)
        
        server_table = Table(show_header=True)
        server_table.add_column("Hostname", style="yellow")
        server_table.add_column("IP Address", style="cyan")
        server_table.add_column("Type", style="magenta")
        server_table.add_column("OS", style="blue")
        server_table.add_column("Status", style="green")
        
        for server in servers:
            server_table.add_row(
                server['hostname'],
                str(server['ip_address']),
                server['server_type'],
                server['operating_system'],
                server['status']
            )
        
        console.print(server_table)
        
        # Test 3: Critical applications
        console.print("\n[bold cyan]🚨 Business Critical Applications:[/bold cyan]")
        
        apps = await conn.fetch("""
            SELECT a.name, a.version, a.status, s.hostname as server, d.name as department
            FROM applications a
            LEFT JOIN servers s ON a.server_id = s.id
            LEFT JOIN departments d ON a.department_id = d.id
            WHERE a.business_criticality = 'critical'
            ORDER BY a.name
        """)
        
        app_table = Table(show_header=True)
        app_table.add_column("Application", style="yellow")
        app_table.add_column("Version", style="cyan")
        app_table.add_column("Status", style="green")
        app_table.add_column("Server", style="blue")
        app_table.add_column("Department", style="magenta")
        
        for app in apps:
            app_table.add_row(
                app['name'],
                app['version'] or 'N/A',
                app['status'],
                app['server'] or 'N/A',
                app['department'] or 'N/A'
            )
        
        console.print(app_table)
        
        # Test 4: Open incidents
        console.print("\n[bold cyan]⚠️ Open Incidents:[/bold cyan]")
        
        incidents = await conn.fetch("""
            SELECT incident_number, title, severity, status, 
                   reported_at, assigned_to
            FROM incidents
            WHERE status IN ('open', 'in_progress')
            ORDER BY 
                CASE severity 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END
        """)
        
        if incidents:
            inc_table = Table(show_header=True)
            inc_table.add_column("Incident #", style="red")
            inc_table.add_column("Title", style="yellow")
            inc_table.add_column("Severity", style="magenta")
            inc_table.add_column("Status", style="cyan")
            inc_table.add_column("Assigned To", style="green")
            
            for inc in incidents:
                severity_color = {
                    'critical': '[red]CRITICAL[/red]',
                    'high': '[yellow]HIGH[/yellow]',
                    'medium': '[cyan]MEDIUM[/cyan]',
                    'low': '[green]LOW[/green]'
                }.get(inc['severity'], inc['severity'])
                
                inc_table.add_row(
                    inc['incident_number'],
                    inc['title'][:40] + '...' if len(inc['title']) > 40 else inc['title'],
                    severity_color,
                    inc['status'],
                    inc['assigned_to'] or 'Unassigned'
                )
            
            console.print(inc_table)
        else:
            console.print("[green]No open incidents![/green]")
        
        # Test 5: Department summary
        console.print("\n[bold cyan]🏢 Department Infrastructure Summary:[/bold cyan]")
        
        dept_summary = await conn.fetch("""
            SELECT 
                d.name as department,
                COUNT(DISTINCT s.id) as server_count,
                COUNT(DISTINCT a.id) as app_count,
                COUNT(DISTINCT CASE WHEN i.status IN ('open', 'in_progress') THEN i.id END) as open_incidents
            FROM departments d
            LEFT JOIN servers s ON s.department_id = d.id
            LEFT JOIN applications a ON a.department_id = d.id
            LEFT JOIN incidents i ON i.department_id = d.id
            GROUP BY d.id, d.name
            ORDER BY d.name
        """)
        
        dept_table = Table(show_header=True)
        dept_table.add_column("Department", style="cyan")
        dept_table.add_column("Servers", style="green")
        dept_table.add_column("Applications", style="yellow")
        dept_table.add_column("Open Incidents", style="red")
        
        for dept in dept_summary:
            dept_table.add_row(
                dept['department'],
                str(dept['server_count']),
                str(dept['app_count']),
                str(dept['open_incidents'])
            )
        
        console.print(dept_table)
        
        # Test 6: Application dependencies
        console.print("\n[bold cyan]🔗 Critical Dependencies:[/bold cyan]")
        
        deps = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN r.parent_type = 'application' THEN a1.name
                    ELSE s1.hostname
                END as parent,
                r.relationship_type,
                CASE 
                    WHEN r.child_type = 'application' THEN a2.name
                    ELSE s2.hostname
                END as child,
                r.criticality
            FROM relationships r
            LEFT JOIN applications a1 ON r.parent_type = 'application' AND r.parent_id = a1.id
            LEFT JOIN servers s1 ON r.parent_type = 'server' AND r.parent_id = s1.id
            LEFT JOIN applications a2 ON r.child_type = 'application' AND r.child_id = a2.id
            LEFT JOIN servers s2 ON r.child_type = 'server' AND r.child_id = s2.id
            WHERE r.criticality IN ('critical', 'high')
            LIMIT 10
        """)
        
        dep_table = Table(show_header=True)
        dep_table.add_column("Parent", style="cyan")
        dep_table.add_column("Relationship", style="yellow")
        dep_table.add_column("Child", style="green")
        dep_table.add_column("Criticality", style="red")
        
        for dep in deps:
            dep_table.add_row(
                dep['parent'],
                dep['relationship_type'].replace('_', ' '),
                dep['child'],
                dep['criticality'].upper()
            )
        
        console.print(dep_table)
        
        # Close connection
        await conn.close()
        
        # Summary
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "[bold green]✅ CMDB Test Complete![/bold green]\n\n" +
            "Your CMDB is working correctly and contains:\n" +
            "• Production servers with various applications\n" +
            "• Business critical systems\n" +
            "• Active incidents to manage\n" +
            "• Department infrastructure\n" +
            "• Application dependencies\n\n" +
            "[yellow]You can now use the chat interface to query this data naturally![/yellow]",
            border_style="green"
        ))
        
        # Example queries for chat
        console.print("\n[bold cyan]💬 Try these in the chat interface:[/bold cyan]")
        examples = [
            "Show me all production servers",
            "Which applications are critical?",
            "What incidents are currently open?",
            "How many servers does IT department have?",
            "Which servers need patching?",
            "Show me the database servers",
            "What's running on web-prod-01?",
            "Calculate total infrastructure cost",
            "Show me Windows servers in production",
            "Find all applications using PostgreSQL"
        ]
        
        for i, example in enumerate(examples, 1):
            console.print(f"  {i}. [yellow]{example}[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Ensure PostgreSQL is running: sudo service postgresql start")
        console.print("2. Check your .env file has correct credentials")
        console.print("3. Verify database exists: psql -U mcp_user -h localhost -l")
        return False
    
    return True


if __name__ == "__main__":
    print("🔍 Testing CMDB Database...\n")
    success = asyncio.run(test_cmdb())
    
    if success:
        print("\n✅ Ready to use with: streamlit run streamlit_openai_mcp.py")
    else:
        print("\n❌ Please fix the issues above before proceeding.")