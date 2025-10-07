#!/usr/bin/env python3
"""
Add grn_number column to inventory_items table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

def add_grn_column():
    """Add grn_number column to inventory_items table"""
    with app.app_context():
        try:
            # Add the grn_number column using text() for raw SQL
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE inventory_items ADD COLUMN grn_number VARCHAR(120)"))
            db.session.commit()
            print("[SUCCESS] Added grn_number column to inventory_items table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("[INFO] grn_number column already exists")
            else:
                print(f"[ERROR] Failed to add grn_number column: {e}")
                return False
        return True

if __name__ == "__main__":
    add_grn_column()
