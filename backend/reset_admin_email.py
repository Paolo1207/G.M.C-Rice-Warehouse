#!/usr/bin/env python3
"""
Reset Admin Email to Default
This script changes the admin user's email back to admin@gmc.com
"""

import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import User

def reset_admin_email():
    """Reset admin user's email to admin@gmc.com"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find the admin user
            admin_user = User.query.filter_by(role='admin').first()
            
            if admin_user:
                old_email = admin_user.email
                new_email = "admin@gmc.com"
                
                if old_email == new_email:
                    print(f"Admin email is already {new_email}. No change needed.")
                    return
                
                # Update the email
                admin_user.email = new_email
                db.session.commit()
                
                print(f"Admin user email updated successfully!")
                print(f"   From: {old_email}")
                print(f"   To: {new_email}")
                print()
                print("You can now log in with admin@gmc.com")
                
            else:
                print("Admin user not found in the database.")
                print("   Make sure you have an admin user in the database.")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error updating admin email: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Resetting admin email to admin@gmc.com...")
    print()
    
    success = reset_admin_email()
    
    if success:
        print()
        print("Admin email reset complete!")
        print("You can now log in with: admin@gmc.com")
    else:
        print()
        print("Failed to reset admin email")
        sys.exit(1)
