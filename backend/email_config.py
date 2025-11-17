# email_config.py - Email configuration for GMC System
# Update these values with your Gmail credentials

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Your Gmail credentials
SENDER_EMAIL = "gmcrice2025@gmail.com"  # Your actual GMC Gmail account
SENDER_PASSWORD = "gryrymytbsrpxlbb"  # Your Gmail App Password (spaces removed)

# Base URL for verification links
BASE_URL = "http://localhost:5000"

# Instructions:
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-Factor Authentication
# 3. Go to "App passwords" section
# 4. Generate an app password for "Mail"
# 5. Replace SENDER_EMAIL and SENDER_PASSWORD above
# 6. Save this file
