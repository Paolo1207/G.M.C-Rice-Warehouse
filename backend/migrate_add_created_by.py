#!/usr/bin/env python3
"""
Migration script to add created_by column to restock_logs table
Run this after updating the model to add the new column to existing data
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
from extensions import db

def migrate_restock_logs():
    """Add created_by column to restock_logs table and set default values"""
    print("🔄 Starting migration: Add created_by to restock_logs...")
    
    with app.app_context():
        try:
            # Add the created_by column with default value
            db.engine.execute("""
                ALTER TABLE restock_logs 
                ADD COLUMN created_by VARCHAR(50) DEFAULT 'Admin'
            """)
            print("✅ Added created_by column to restock_logs table")
            
            # Update existing records to have 'Admin' as created_by
            db.engine.execute("""
                UPDATE restock_logs 
                SET created_by = 'Admin' 
                WHERE created_by IS NULL
            """)
            print("✅ Updated existing records with created_by = 'Admin'")
            
            print("🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("Note: If the column already exists, this is expected.")
            return False
    
    return True

if __name__ == "__main__":
    migrate_restock_logs()
