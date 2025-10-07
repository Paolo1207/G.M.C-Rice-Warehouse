# email_service.py - Email sending functionality
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import os
from flask import current_app

class EmailService:
    def __init__(self):
        # Try to load from email_config.py first
        try:
            from email_config import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT
            self.sender_email = SENDER_EMAIL
            self.sender_password = SENDER_PASSWORD
            self.smtp_server = SMTP_SERVER
            self.smtp_port = SMTP_PORT
        except ImportError:
            # Fallback to environment variables
            self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
            self.sender_email = os.getenv('SENDER_EMAIL', 'yourname@gmail.com')
            self.sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
        
        # Check if email is properly configured
        self.is_configured = (
            self.sender_email != 'yourname@gmail.com' and 
            self.sender_password != 'your-app-password' and
            self.sender_password and 
            len(self.sender_password) > 10 and
            '@gmail.com' in self.sender_email and
            'gmcrice2025@gmail.com' in self.sender_email  # Check for our specific Gmail account
        )
        
    def send_verification_email(self, to_email, verification_token, user_name):
        """Send email verification link"""
        try:
            # Check if email is configured
            if not self.is_configured:
                print("Email service not configured - skipping email send")
                return False
                
            # Create verification link
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            verification_link = f"{base_url}/admin/verify-email?token={verification_token}"
            
            # Create email content
            subject = "Verify Your New Email Address - GMC System"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #2e7d32; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0;">GMC Rice Warehouse System</h1>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #2e7d32; margin-top: 0;">Email Verification Required</h2>
                        
                        <p>Hello {user_name},</p>
                        
                        <p>You have requested to change your email address in the GMC System. To complete this change, please verify your new email address by clicking the button below:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_link}" 
                               style="background: #2e7d32; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <p><strong>Important:</strong></p>
                        <ul>
                            <li>This link will expire in 24 hours</li>
                            <li>If you didn't request this change, please ignore this email</li>
                            <li>Your account will remain secure with your current email until verified</li>
                        </ul>
                        
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace;">
                            {verification_link}
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #666;">
                            This is an automated message from the GMC Rice Warehouse System.<br>
                            Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            return self._send_email(to_email, subject, html_content)
            
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False
    
    def send_password_reset_email(self, to_email, reset_token, user_name):
        """Send password reset email"""
        try:
            # Check if email is configured
            if not self.is_configured:
                print("Email service not configured - skipping password reset email")
                return False
                
            # Create reset link
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            reset_link = f"{base_url}/admin/reset-password?token={reset_token}"
            
            # Create email content
            subject = "Password Reset Request - GMC System"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #d32f2f; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0;">GMC Rice Warehouse System</h1>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #d32f2f; margin-top: 0;">Password Reset Request</h2>
                        
                        <p>Hello {user_name},</p>
                        
                        <p>You have requested to reset your password for the GMC System. To reset your password, please click the button below:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" 
                               style="background: #d32f2f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p><strong>Important:</strong></p>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Your account remains secure until you use this link</li>
                        </ul>
                        
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace;">
                            {reset_link}
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #666;">
                            This is an automated message from the GMC Rice Warehouse System.<br>
                            Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            return self._send_email(to_email, subject, html_content)
            
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False

    def send_email_change_notification(self, old_email, new_email, user_name):
        """Send notification to old email about the change"""
        try:
            subject = "Your GMC Account Email Has Been Changed"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #d32f2f; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0;">GMC Rice Warehouse System</h1>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #d32f2f; margin-top: 0;">Email Address Changed</h2>
                        
                        <p>Hello {user_name},</p>
                        
                        <p><strong>Your email address has been successfully changed from:</strong></p>
                        <p style="background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace;">
                            {old_email}
                        </p>
                        
                        <p><strong>To:</strong></p>
                        <p style="background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace;">
                            {new_email}
                        </p>
                        
                        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404;"><strong>Security Notice:</strong> If you did not make this change, please contact your system administrator immediately.</p>
                        </div>
                        
                        <p>You can now log in using your new email address: <strong>{new_email}</strong></p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #666;">
                            This is an automated security notification from the GMC Rice Warehouse System.<br>
                            Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(old_email, subject, html_content)
            
        except Exception as e:
            print(f"Error sending change notification: {e}")
            return False
    
    def _send_email(self, to_email, subject, html_content):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

# Global email service instance
email_service = EmailService()
