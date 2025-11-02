#!/usr/bin/env python3
"""
Migration script to update the unique constraint on inventory_items table
to include batch_code, allowing multiple batches of the same product per branch.

Run this script once to update your database:
    python migrate_batch_constraint.py

This will:
1. Check if the old constraint exists and drop it
2. Check if the new constraint exists and create it if missing
3. Work with both local and production (Render) PostgreSQL databases
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment or use default"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback to local development database
        database_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/gmcdb"
        print("⚠️  Using default local database URL (set DATABASE_URL for production)")
    return database_url

def check_constraint_exists(engine, constraint_name, table_name='inventory_items'):
    """Check if a constraint exists on a table"""
    try:
        with engine.connect() as conn:
            # PostgreSQL query to check if constraint exists
            query = text("""
                SELECT COUNT(*) 
                FROM pg_constraint 
                WHERE conname = :constraint_name 
                AND conrelid = :table_name::regclass
            """)
            result = conn.execute(query, {
                'constraint_name': constraint_name,
                'table_name': table_name
            })
            count = result.scalar()
            return count > 0
    except Exception as e:
        print(f"❌ Error checking constraint: {e}")
        return False

def drop_constraint(engine, constraint_name, table_name='inventory_items'):
    """Drop a constraint if it exists"""
    try:
        with engine.connect() as conn:
            if check_constraint_exists(engine, constraint_name, table_name):
                query = text(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}")
                conn.execute(query)
                conn.commit()
                print(f"✅ Dropped constraint: {constraint_name}")
                return True
            else:
                print(f"ℹ️  Constraint {constraint_name} does not exist (skipping)")
                return False
    except Exception as e:
        print(f"❌ Error dropping constraint {constraint_name}: {e}")
        return False

def create_constraint(engine, constraint_name, table_name='inventory_items'):
    """Create the new unique constraint"""
    try:
        with engine.connect() as conn:
            if check_constraint_exists(engine, constraint_name, table_name):
                print(f"ℹ️  Constraint {constraint_name} already exists (skipping)")
                return True
            
            query = text(f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {constraint_name} 
                UNIQUE (branch_id, product_id, batch_code)
            """)
            conn.execute(query)
            conn.commit()
            print(f"✅ Created constraint: {constraint_name}")
            return True
    except Exception as e:
        print(f"❌ Error creating constraint {constraint_name}: {e}")
        return False

def migrate():
    """Run the migration"""
    print("=" * 60)
    print("🔄 Starting batch constraint migration...")
    print("=" * 60)
    
    database_url = get_database_url()
    
    # Mask the password in the URL for display
    display_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split('://')[-1]
            if ':' in user_pass:
                user = user_pass.split(':')[0]
                display_url = database_url.replace(user_pass, f"{user}:***")
    
    print(f"📊 Database: {display_url}")
    print()
    
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        print()
        
        # Step 1: Drop old constraint if it exists (common names)
        old_constraints = ['uq_branch_product', 'uq_inventory_branch_product']
        for old_constraint in old_constraints:
            drop_constraint(engine, old_constraint)
        
        print()
        
        # Step 2: Create new constraint
        new_constraint = 'uq_branch_product_batch'
        create_constraint(engine, new_constraint)
        
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print("📝 What changed:")
        print("   - Old constraint: (branch_id, product_id) was removed")
        print("   - New constraint: (branch_id, product_id, batch_code) was added")
        print()
        print("✨ You can now add products with the same name but different batch codes!")
        
        return True
        
    except SQLAlchemyError as e:
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Check your DATABASE_URL environment variable")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify database credentials are correct")
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Unexpected error!")
        print("=" * 60)
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

