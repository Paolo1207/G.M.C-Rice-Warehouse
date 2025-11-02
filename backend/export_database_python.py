#!/usr/bin/env python3
"""
Export PostgreSQL database using Python (no pg_dump required).
This script connects directly and exports all tables to SQL.
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Try to import required packages
try:
    from sqlalchemy import create_engine, text, inspect
except ImportError:
    print("ERROR: sqlalchemy not installed. Please run: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables.")
    print("Please set DATABASE_URL in your .env file.")
    sys.exit(1)

# Create engine
try:
    # Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy
    if DATABASE_URL.startswith('postgresql://'):
        engine_url = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
    elif DATABASE_URL.startswith('postgres://'):
        engine_url = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://')
    else:
        engine_url = DATABASE_URL
    
    engine = create_engine(engine_url, echo=False)
    print("✅ Connected to database")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    sys.exit(1)

# Output file
output_file = "database_export.sql"
print(f"\nExporting database to: {output_file}")

# Get all tables
inspector = inspect(engine)
tables = inspector.get_table_names()

if not tables:
    print("No tables found in database.")
    sys.exit(1)

print(f"Found {len(tables)} tables: {', '.join(tables)}")

# Start export
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"-- Database Export\n")
    f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"-- Tables: {len(tables)}\n\n")
    
    with engine.connect() as conn:
        # Export schema for each table
        for table in tables:
            print(f"Exporting table: {table}")
            
            # Get CREATE TABLE statement
            try:
                result = conn.execute(text(f"""
                    SELECT 'CREATE TABLE ' || quote_ident(table_name) || ' (' || 
                           string_agg(column_definition, ', ') || ');' as create_stmt
                    FROM (
                        SELECT 
                            table_name,
                            quote_ident(column_name) || ' ' || 
                            CASE 
                                WHEN data_type = 'character varying' THEN 'VARCHAR(' || character_maximum_length || ')'
                                WHEN data_type = 'character' THEN 'CHAR(' || character_maximum_length || ')'
                                WHEN data_type = 'numeric' THEN 'NUMERIC(' || numeric_precision || ',' || numeric_scale || ')'
                                ELSE UPPER(data_type)
                            END ||
                            CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                            CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END
                            as column_definition
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    ) cols
                    GROUP BY table_name;
                """), {"table_name": table})
                
                create_stmt = result.fetchone()
                if create_stmt and create_stmt[0]:
                    f.write(f"\n-- Table: {table}\n")
                    f.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
                    f.write(f"{create_stmt[0]}\n\n")
                    
            except Exception as e:
                print(f"  Warning: Could not export schema for {table}: {e}")
            
            # Export data
            try:
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                if rows:
                    f.write(f"-- Data for table: {table}\n")
                    
                    # Get column names
                    columns = [col for col in result.keys()]
                    col_names = ', '.join([f'"{col}"' for col in columns])
                    
                    # Export rows
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped = val.replace("'", "''")
                                values.append(f"'{escaped}'")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            elif isinstance(val, bool):
                                values.append('TRUE' if val else 'FALSE')
                            else:
                                escaped = str(val).replace("'", "''")
                                values.append(f"'{escaped}'")
                        
                        value_str = ', '.join(values)
                        f.write(f"INSERT INTO {table} ({col_names}) VALUES ({value_str});\n")
                    
                    f.write(f"\n")
                    print(f"  Exported {len(rows)} rows")
                else:
                    print(f"  Table {table} is empty")
                    
            except Exception as e:
                print(f"  Warning: Could not export data for {table}: {e}")

print(f"\n✅ Export complete: {output_file}")
print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")

