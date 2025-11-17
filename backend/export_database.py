#!/usr/bin/env python3
"""
Export PostgreSQL database from Render to SQL dump file.
This script will create a complete SQL dump of your database.
"""
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables.")
    print("Please set DATABASE_URL in your .env file or environment.")
    exit(1)

# Parse the DATABASE_URL
# Format: postgresql://user:password@host:port/database
# Or: postgres://user:password@host:port/database
print(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")

# Output filename
output_file = "database_export.sql"
print(f"\nExporting database to: {output_file}")
print("This may take a few minutes depending on database size...\n")

try:
    # Use pg_dump to export the database
    # pg_dump options:
    # -Fc: Custom format (compressed, can be restored with pg_restore)
    # -Fp: Plain SQL format (readable, can use psql to restore)
    # We'll use plain format for readability and ease of sharing
    
    # Replace postgresql:// with postgres:// if needed (pg_dump expects postgres://)
    dump_url = DATABASE_URL.replace('postgresql://', 'postgres://')
    
    # Run pg_dump
    result = subprocess.run(
        ['pg_dump', dump_url, '--no-owner', '--no-acl', '-F', 'p'],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
    print(f"✅ Successfully exported database to {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Error exporting database:")
    print(f"Error: {e.stderr}")
    print("\nMake sure you have PostgreSQL client tools installed:")
    print("  Windows: Download from https://www.postgresql.org/download/windows/")
    print("  Or use: pip install psycopg2-binary")
except FileNotFoundError:
    print("❌ pg_dump command not found.")
    print("\nPlease install PostgreSQL client tools:")
    print("  Windows: Download from https://www.postgresql.org/download/windows/")
    print("  Or use Docker: docker run --rm -e PGPASSWORD=your_password postgres:alpine pg_dump ...")
    print("\nAlternative: Use the Python-based export below")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

