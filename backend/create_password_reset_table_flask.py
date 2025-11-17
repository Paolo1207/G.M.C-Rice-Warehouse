#!/usr/bin/env python3
"""
Create password_resets table using Flask app's database connection
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import PasswordReset

def create_password_reset_table():
    """Create the password_resets table using Flask's database connection"""
    
    try:
        with app.app_context():
            # Create all tables (this will create the PasswordReset table)
            db.create_all()
            print("[SUCCESS] Password resets table created successfully!")
            return True
        
    except Exception as e:
        print(f"[ERROR] Error creating password resets table: {e}")
        return False

if __name__ == "__main__":
    print("Creating password_resets table using Flask...")
    success = create_password_reset_table()
    
    if success:
        print("\n[SUCCESS] Password reset table setup complete!")
        print("You can now use password reset functionality.")
    else:
        print("\n[ERROR] Failed to create password reset table.")
        sys.exit(1)
