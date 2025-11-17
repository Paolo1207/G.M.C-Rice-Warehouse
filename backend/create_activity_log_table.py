#!/usr/bin/env python3
"""
Create activity_logs table for comprehensive activity tracking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

def create_activity_log_table():
    """Create activity_logs table"""
    with app.app_context():
        try:
            # Create the activity_logs table
            db.create_all()
            print("[SUCCESS] Activity logs table created successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to create activity logs table: {e}")
            return False
        return True

if __name__ == "__main__":
    create_activity_log_table()
