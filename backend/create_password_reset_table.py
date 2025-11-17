#!/usr/bin/env python3
"""
Create password_resets table in the database
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

def create_password_reset_table():
    """Create the password_resets table"""
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DEBUG: DATABASE_URL = None")
        print("DEBUG: Using development database: PostgreSQL")
        database_url = "postgresql://postgres:password@localhost:5432/gmc_warehouse"
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Create table SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(id),
            reset_token VARCHAR UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_used BOOLEAN DEFAULT FALSE
        );
        """
        
        # Execute the SQL
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        print("✅ Password resets table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating password resets table: {e}")
        return False

if __name__ == "__main__":
    print("Creating password_resets table...")
    success = create_password_reset_table()
    
    if success:
        print("\n🎉 Password reset table setup complete!")
        print("You can now use password reset functionality.")
    else:
        print("\n💥 Failed to create password reset table.")
        sys.exit(1)
