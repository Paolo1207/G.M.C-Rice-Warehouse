#!/usr/bin/env python3
"""
Script to fix malformed password hashes in the database
"""
import os
import sys
from werkzeug.security import generate_password_hash

def create_fixed_hashes():
    """Generate proper password hashes"""
    
    # Generate proper hashes
    admin_hash = generate_password_hash("adminpass")
    manager_hash = generate_password_hash("managerpass")
    
    print("=== FIXED PASSWORD HASHES ===")
    print()
    print("-- Admin user with proper hash")
    print(f"UPDATE users SET password_hash = '{admin_hash}' WHERE email = 'admin@gmc.com';")
    print()
    print("-- Manager users with proper hash")
    print(f"UPDATE users SET password_hash = '{manager_hash}' WHERE role = 'manager';")
    print()
    print("-- Verify the fix")
    print("SELECT email, role, password_hash FROM users;")
    print()
    print("=== COPY THESE SQL COMMANDS TO PGADMIN 4 ===")
    print("Run these commands in your Render database via pgAdmin 4")

if __name__ == "__main__":
    create_fixed_hashes()
