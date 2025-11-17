#!/usr/bin/env python3
"""
Verify that grn_number column exists in inventory_items table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def verify_grn_column():
    """Check if grn_number column exists in inventory_items table"""
    with app.app_context():
        try:
            # Check if the column exists by querying the table structure
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'inventory_items' 
                AND column_name = 'grn_number'
            """))
            
            columns = result.fetchall()
            if columns:
                print("[SUCCESS] grn_number column exists in inventory_items table")
                print(f"Column details: {columns[0]}")
                return True
            else:
                print("[ERROR] grn_number column does NOT exist in inventory_items table")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to verify grn_number column: {e}")
            return False

if __name__ == "__main__":
    verify_grn_column()
