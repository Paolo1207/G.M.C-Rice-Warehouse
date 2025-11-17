#!/usr/bin/env python3
"""
Reset manager password to default credentials
Resets manager_marawoy@gmc.com password back to: managerpass

Run this script:
    python reset_manager_password.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Flask app and database
from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def reset_manager_password():
    """Reset manager_marawoy@gmc.com password to managerpass"""
    print("=" * 60)
    print("🔄 Resetting manager password to default...")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Find the manager user
            email = "manager_marawoy@gmc.com"
            manager = User.query.filter_by(email=email).first()
            
            if not manager:
                print(f"❌ Manager user '{email}' not found in database!")
                print()
                print("💡 Checking all users in database...")
                all_users = User.query.all()
                if all_users:
                    print("\nExisting users:")
                    for u in all_users:
                        print(f"  - {u.email} (role: {u.role})")
                else:
                    print("  No users found in database.")
                return False
            
            # Generate new password hash for "managerpass"
            new_hash = generate_password_hash("managerpass")
            
            # Update the password
            manager.password_hash = new_hash
            db.session.commit()
            
            print(f"✅ Successfully reset password for: {email}")
            print()
            print("📝 New credentials:")
            print(f"   Email: {email}")
            print(f"   Password: managerpass")
            print()
            print("=" * 60)
            print("✅ Password reset complete!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print()
            print("=" * 60)
            print("❌ Error resetting password!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            print("💡 Troubleshooting:")
            print("   1. Check your DATABASE_URL environment variable")
            print("   2. Ensure PostgreSQL is running")
            print("   3. Verify database credentials are correct")
            return False

if __name__ == "__main__":
    success = reset_manager_password()
    sys.exit(0 if success else 1)

