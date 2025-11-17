#!/usr/bin/env python3
"""
Create EmailVerification table migration
Run this script to add the email verification table to your database
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import EmailVerification

def create_email_verification_table():
    """Create the email_verifications table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ EmailVerification table created successfully!")
            
            # Verify the table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'email_verifications' in tables:
                print("✅ Table 'email_verifications' exists in database")
                
                # Show table structure
                columns = inspector.get_columns('email_verifications')
                print("\n📋 Table structure:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ Table 'email_verifications' not found")
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Creating EmailVerification table...")
    success = create_email_verification_table()
    
    if success:
        print("\n🎉 Email verification system is ready!")
        print("\n📧 To configure email sending, set these environment variables:")
        print("   SMTP_SERVER=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SENDER_EMAIL=your-email@gmail.com")
        print("   SENDER_PASSWORD=your-app-password")
        print("   BASE_URL=http://localhost:5000")
    else:
        print("\n❌ Failed to create email verification table")
        sys.exit(1)
