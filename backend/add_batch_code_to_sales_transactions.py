#!/usr/bin/env python3
"""
Migration script to add batch_code column to sales_transactions table
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Database URL - update this with your actual database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gmcdb_user:Ch9zA0bxdMgqWwsuUsbfoVRts0qxbhGz@dpg-d3cd1j2li9vc73df7i10-a.oregon-postgres.render.com/gmcdb')

def add_batch_code_column():
    """Add batch_code column to sales_transactions table"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sales_transactions' AND column_name='batch_code'
            """)
            result = conn.execute(check_query)
            if result.fetchone():
                print("Column 'batch_code' already exists in sales_transactions table")
                return True
            
            # Add the column
            alter_query = text("""
                ALTER TABLE sales_transactions 
                ADD COLUMN batch_code VARCHAR(120)
            """)
            conn.execute(alter_query)
            conn.commit()
            print("Successfully added 'batch_code' column to sales_transactions table")
            return True
            
    except ProgrammingError as e:
        print(f"Error adding column: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("Adding batch_code column to sales_transactions table...")
    success = add_batch_code_column()
    sys.exit(0 if success else 1)

