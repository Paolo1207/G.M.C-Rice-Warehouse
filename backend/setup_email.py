#!/usr/bin/env python3
"""
Email Configuration Setup for GMC System
This script helps you configure email sending for the GMC system
"""

import os
import sys

def setup_email_config():
    """Interactive email configuration setup"""
    print("🔧 GMC Email Configuration Setup")
    print("=" * 50)
    print()
    
    print("To enable email verification, you need to configure Gmail SMTP.")
    print("This requires a Gmail account with App Password enabled.")
    print()
    
    # Get email configuration
    sender_email = input("Enter your Gmail address (e.g., yourname@gmail.com): ").strip()
    if not sender_email or '@gmail.com' not in sender_email:
        print("❌ Please enter a valid Gmail address")
        return False
    
    print()
    print("📧 Gmail App Password Setup:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication if not already enabled")
    print("3. Go to 'App passwords' section")
    print("4. Generate an app password for 'Mail'")
    print("5. Copy the 16-character password (no spaces)")
    print()
    
    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    if len(app_password) != 16 or not app_password.isalnum():
        print("❌ App password should be 16 alphanumeric characters")
        return False
    
    # Create .env file
    env_content = f"""# GMC System Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={app_password}
BASE_URL=http://localhost:5000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ Email configuration saved to .env file")
        print()
        print("🚀 Email verification is now enabled!")
        print("When users change their email, they will receive a real verification email.")
        print()
        print("📧 Test the system:")
        print("1. Go to Admin Settings")
        print("2. Change your email address")
        print("3. Check your Gmail inbox for verification email")
        print("4. Click the verification link")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_email_config():
    """Test if email configuration is working"""
    try:
        from email_service import email_service
        
        print("🧪 Testing email configuration...")
        
        if email_service.is_configured:
            print("✅ Email service is configured")
            print(f"📧 Sender: {email_service.sender_email}")
            print(f"🔗 SMTP: {email_service.smtp_server}:{email_service.smtp_port}")
            return True
        else:
            print("❌ Email service is not configured")
            print("Run 'python setup_email.py' to configure")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_email_config()
    else:
        setup_email_config()
