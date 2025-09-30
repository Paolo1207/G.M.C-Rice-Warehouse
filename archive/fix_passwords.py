#!/usr/bin/env python3
"""
Quick script to fix password hashing in the database
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app
from backend.models import User
from werkzeug.security import generate_password_hash

def fix_passwords():
    with app.app_context():
        # Update admin password
        admin = User.query.filter_by(email='admin@gmc.com').first()
        if admin:
            admin.password_hash = generate_password_hash('adminpass')
            print('✅ Updated admin password')
        else:
            print('❌ Admin user not found')
        
        # Update manager passwords
        managers = User.query.filter_by(role='manager').all()
        for manager in managers:
            manager.password_hash = generate_password_hash('managerpass')
            print(f'✅ Updated manager password: {manager.email}')
        
        from backend.extensions import db
        db.session.commit()
        print('🎉 All passwords updated successfully!')

if __name__ == "__main__":
    fix_passwords()
