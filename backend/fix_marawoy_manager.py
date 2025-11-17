#!/usr/bin/env python3
"""
Quick fix to reset manager_marawoy@gmc.com password to default
Uses Flask app context to ensure it works with the database.
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# Import Flask app and database
from app import create_app
from extensions import db
from models import User

def fix_marawoy_manager():
    """Fix Marawoy manager password"""
    print("=" * 60)
    print("Fixing Marawoy Manager Password...")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            email = "manager_marawoy@gmc.com"
            
            print(f"Resetting password for: {email}")
            print(f"New password: managerpass")
            print()
            
            # Find the manager user - try both with and without @gmc.com
            manager = User.query.filter_by(email=email).first()
            
            # If not found, try finding by branch_id for Marawoy (branch_id = 1)
            if not manager:
                print(f"User '{email}' not found, checking branch_id=1 (Marawoy)...")
                manager = User.query.filter_by(role='manager', branch_id=1).first()
                if manager:
                    print(f"Found manager for Marawoy branch, but email is: '{manager.email}'")
                    print("Updating email to include @gmc.com...")
                    manager.email = email  # Fix the email
            
            if not manager:
                print(f"ERROR: Manager for Marawoy branch not found!")
                print()
                print("Checking all manager users...")
                all_managers = User.query.filter_by(role='manager').all()
                if all_managers:
                    print("\nExisting managers:")
                    for m in all_managers:
                        print(f"  - {m.email} (role: {m.role}, branch_id: {m.branch_id})")
                else:
                    print("  No managers found.")
                return False
            
            print(f"Found user: ID={manager.id}, Email={manager.email}, Role={manager.role}, Branch ID={manager.branch_id}")
            print()
            
            # Generate new password hash
            password_hash = generate_password_hash("managerpass")
            
            # Update email (if it was wrong) and password
            manager.email = email  # Ensure email is correct
            manager.password_hash = password_hash
            db.session.commit()
            
            print("Password updated successfully!")
            print()
            print("=" * 60)
            print("Fix complete!")
            print("=" * 60)
            print()
            print("Login Credentials:")
            print(f"   Email: {email}")
            print(f"   Password: managerpass")
            print()
            print("You can now login!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print()
            print("=" * 60)
            print("ERROR: Error fixing password!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = fix_marawoy_manager()
    sys.exit(0 if success else 1)

