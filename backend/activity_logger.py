#!/usr/bin/env python3
"""
Activity Logger Service for comprehensive system activity tracking
"""
import json
from datetime import datetime
from extensions import db
from models import ActivityLog, User, Branch

class ActivityLogger:
    """Service for logging all system activities"""
    
    @staticmethod
    def log_activity(user_id=None, user_email=None, action="", description="", details=None, branch_id=None):
        """Log an activity to the database"""
        try:
            activity = ActivityLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                description=description,
                details=json.dumps(details) if details else None,
                branch_id=branch_id
            )
            db.session.add(activity)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def log_password_reset(user_email, success=True):
        """Log password reset activity"""
        action = "password_reset_success" if success else "password_reset_failed"
        description = f"Password reset {'completed' if success else 'failed'} for {user_email}"
        ActivityLogger.log_activity(
            user_email=user_email,
            action=action,
            description=description,
            details={"success": success, "timestamp": datetime.utcnow().isoformat()}
        )
    
    @staticmethod
    def log_email_change(user_email, old_email, new_email, success=True):
        """Log email change activity"""
        action = "email_change_success" if success else "email_change_failed"
        description = f"Email changed from {old_email} to {new_email}" if success else f"Email change failed for {user_email}"
        ActivityLogger.log_activity(
            user_email=user_email,
            action=action,
            description=description,
            details={"old_email": old_email, "new_email": new_email, "success": success}
        )
    
    @staticmethod
    def log_product_add(user_id, user_email, product_name, branch_id, details=None):
        """Log product addition activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Unknown Branch"
        description = f"Added new product '{product_name}' to {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="product_add",
            description=description,
            details=details,
            branch_id=branch_id
        )
    
    @staticmethod
    def log_product_edit(user_id, user_email, product_name, branch_id, changes=None):
        """Log product edit activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Unknown Branch"
        description = f"Edited product '{product_name}' in {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="product_edit",
            description=description,
            details=changes,
            branch_id=branch_id
        )
    
    @staticmethod
    def log_product_delete(user_id, user_email, product_name, branch_id):
        """Log product deletion activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Unknown Branch"
        description = f"Deleted product '{product_name}' from {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="product_delete",
            description=description,
            branch_id=branch_id
        )
    
    @staticmethod
    def log_restock(user_id, user_email, product_name, quantity, branch_id):
        """Log restock activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Unknown Branch"
        description = f"Restocked {quantity}kg of '{product_name}' in {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="restock",
            description=description,
            details={"product_name": product_name, "quantity": quantity},
            branch_id=branch_id
        )
    
    @staticmethod
    def log_sale(user_id, user_email, product_name, quantity, amount, branch_id):
        """Log sale activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Unknown Branch"
        description = f"Sale: {quantity}kg of '{product_name}' for ₱{amount:,.2f} in {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="sale",
            description=description,
            details={"product_name": product_name, "quantity": quantity, "amount": amount},
            branch_id=branch_id
        )
    
    @staticmethod
    def log_user_login(user_id, user_email, branch_id):
        """Log user login activity"""
        branch = Branch.query.get(branch_id) if branch_id else None
        branch_name = branch.name if branch else "Head Office"
        user = User.query.get(user_id) if user_id else None
        role = user.role if user else "Unknown"
        description = f"{role.title()} {user_email} logged in from {branch_name}"
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action="user_login",
            description=description,
            branch_id=branch_id
        )
    
    @staticmethod
    def log_user_management(user_id, user_email, action_type, target_user_email, details=None):
        """Log user management activities"""
        descriptions = {
            "user_create": f"Created new user: {target_user_email}",
            "user_edit": f"Updated user: {target_user_email}",
            "user_delete": f"Deleted user: {target_user_email}",
            "user_activate": f"Activated user: {target_user_email}",
            "user_deactivate": f"Deactivated user: {target_user_email}"
        }
        description = descriptions.get(action_type, f"User management action: {action_type}")
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action=f"user_management_{action_type}",
            description=description,
            details=details
        )
    
    @staticmethod
    def log_system_action(user_id, user_email, action_type, description, details=None):
        """Log general system actions"""
        ActivityLogger.log_activity(
            user_id=user_id,
            user_email=user_email,
            action=f"system_{action_type}",
            description=description,
            details=details
        )
