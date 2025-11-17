# models.py
from datetime import datetime, timedelta
from extensions import db

class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(255))
    status = db.Column(db.String(32), default="operational")  # operational | maintenance | closed

    inventory_items = db.relationship("InventoryItem", back_populates="branch", cascade="all,delete-orphan")
    
    def to_dict(self):
        """Convert branch to dictionary, safely calculating total stock"""
        try:
            # Calculate total stock for this branch
            # Use a safe approach to handle lazy loading issues
            total_stock_kg = 0
            try:
                # Try to access inventory_items safely
                if self.inventory_items:
                    total_stock_kg = sum(float(item.stock_kg or 0) for item in self.inventory_items)
            except Exception as e:
                # If lazy loading fails, query directly
                from sqlalchemy import func
                from extensions import db
                result = db.session.query(func.sum(InventoryItem.stock_kg)).filter_by(branch_id=self.id).scalar()
                total_stock_kg = float(result or 0)
            
            return {
                "id": self.id,
                "name": self.name or "Unknown",
                "location": self.location or "N/A",
                "status": self.status or "operational",
                "total_stock_kg": round(total_stock_kg, 2)
            }
        except Exception as e:
            # Fallback to basic info if anything fails
            print(f"DEBUG Branch.to_dict error for branch {self.id}: {e}")
            return {
                "id": self.id,
                "name": self.name or "Unknown",
                "location": self.location or "N/A",
                "status": self.status or "operational",
                "total_stock_kg": 0
            }

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    category = db.Column(db.String(120))
    barcode = db.Column(db.String(120))
    sku = db.Column(db.String(120))
    description = db.Column(db.Text)

    inventory_items = db.relationship("InventoryItem", back_populates="product", cascade="all,delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("name", name="uq_products_name"),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "barcode": self.barcode,
            "sku": self.sku,
            "description": self.description
        }

class InventoryItem(db.Model):
    __tablename__ = "inventory_items"
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # stock & pricing
    stock_kg = db.Column(db.Float, default=0)
    unit_price = db.Column(db.Float, default=0)
    batch_code = db.Column(db.String(120))
    grn_number = db.Column(db.String(120))

    # optional thresholds/margins
    warn_level = db.Column(db.Float)
    auto_level = db.Column(db.Float)
    margin = db.Column(db.String(20))  # keep string (e.g., "20%")
    
    # timestamps
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship("Branch", back_populates="inventory_items")
    product = db.relationship("Product", back_populates="inventory_items")
    logs = db.relationship("RestockLog", back_populates="inventory_item", cascade="all,delete-orphan")

    __table_args__ = (
        # Allow multiple inventory rows for the same product in a branch as long as batch differs
        db.UniqueConstraint("branch_id", "product_id", "batch_code", name="uq_branch_product_batch"),
    )

    # helper
    @property
    def status(self):
        if self.stock_kg <= 0:
            return "out"
        if self.warn_level is not None and self.stock_kg < self.warn_level:
            return "low"
        return "available"

    def to_dict(self):
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "category": self.product.category,
            "barcode": self.product.barcode,
            "sku": self.product.sku,
            "desc": self.product.description,
            "stock": self.stock_kg,
            "price": self.unit_price,
            "batch": self.batch_code,
            "grn": self.grn_number,
            "warn": self.warn_level,
            "auto": self.auto_level,
            "margin": self.margin,
            "status": self.status,
        }

class RestockLog(db.Model):
    __tablename__ = "restock_logs"
    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False, index=True)
    qty_kg = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(160))
    note = db.Column(db.String(255))
    created_by = db.Column(db.String(50), default="Admin")  # Who performed the restock
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    inventory_item = db.relationship("InventoryItem", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "inventory_item_id": self.inventory_item_id,
            "qty": self.qty_kg,
            "supplier": self.supplier,
            "note": self.note,
            "created_by": self.created_by,
            "date": self.created_at.strftime("%Y-%m-%d"),
            "datetime": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),  # Full timestamp for sorting
            "variant": self.inventory_item.product.name,
            "batch_code": self.inventory_item.batch_code or "",  # Include batch code from inventory item
        }
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default="manager")  # "admin" | "manager"
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True)  # required for manager

class EmailVerification(db.Model):
    __tablename__ = "email_verifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    new_email = db.Column(db.String, nullable=False)
    verification_token = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class PasswordReset(db.Model):
    __tablename__ = "password_resets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reset_token = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user_email = db.Column(db.String, nullable=True)  # Store email for deleted users
    action = db.Column(db.String, nullable=False)  # reset_password, email_change, add_stock, edit_product, delete_product, restock, etc.
    description = db.Column(db.String, nullable=False)
    details = db.Column(db.Text)  # JSON string for additional details
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref="activity_logs")
    branch = db.relationship("Branch", backref="activity_logs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "action": self.action,
            "description": self.description,
            "details": self.details,
            "branch_name": self.branch.name if self.branch else None,
            "created_at": self.created_at.isoformat(),
            "time_ago": self.get_time_ago()
        }
    
    def get_time_ago(self):
        """Get human-readable time ago"""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

class ForecastData(db.Model):
    __tablename__ = "forecast_data"
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    
    # Forecast details
    forecast_date = db.Column(db.Date, nullable=False)
    forecast_period = db.Column(db.String(20), nullable=False)  # "daily", "weekly", "monthly"
    predicted_demand = db.Column(db.Float, nullable=False)
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)
    model_type = db.Column(db.String(50), default="ARIMA")  # "ARIMA", "ML", "Simple"
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accuracy_score = db.Column(db.Float)  # Model accuracy if available
    
    # Relationships
    branch = db.relationship("Branch")
    product = db.relationship("Product")
    
    def to_dict(self):
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "product_id": self.product_id,
            "branch_name": self.branch.name if self.branch else None,
            "product_name": self.product.name if self.product else None,
            "forecast_date": self.forecast_date.strftime("%Y-%m-%d"),
            "forecast_period": self.forecast_period,
            "predicted_demand": self.predicted_demand,
            "confidence_interval_lower": self.confidence_interval_lower,
            "confidence_interval_upper": self.confidence_interval_upper,
            "model_type": self.model_type,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy_score": self.accuracy_score,
        }

class SalesTransaction(db.Model):
    __tablename__ = "sales_transactions"
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    
    # Transaction details
    quantity_sold = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    batch_code = db.Column(db.String(120), nullable=True)  # Batch code used for this sale
    
    # Customer info (optional)
    customer_name = db.Column(db.String(255))
    customer_contact = db.Column(db.String(100))
    
    # Relationships
    branch = db.relationship("Branch")
    product = db.relationship("Product")
    
    def to_dict(self):
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "product_id": self.product_id,
            "branch_name": self.branch.name if self.branch else None,
            "product_name": self.product.name if self.product else None,
            "quantity_sold": self.quantity_sold,
            "unit_price": self.unit_price,
            "total_amount": self.total_amount,
            "transaction_date": self.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "batch_code": self.batch_code,
            "customer_name": self.customer_name,
            "customer_contact": self.customer_contact,
        }


class ExportLog(db.Model):
    __tablename__ = "export_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    report_type = db.Column(db.String(50), nullable=False)  # sales | forecast | inventory
    filters_json = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)    # csv | xlsx | pdf
    status = db.Column(db.String(20), default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "report_type": self.report_type,
            "filters_json": self.filters_json,
            "file_type": self.file_type,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # low_stock_alert, manual_message, etc.
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(100), nullable=False, default='Admin')
    status = db.Column(db.String(20), nullable=False, default='unread')  # unread, read
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # Relationships
    branch = db.relationship('Branch', backref='notifications')
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "branch_id": self.branch_id,
            "branch_name": self.branch.name if self.branch else None,
            "date": self.date.strftime("%Y-%m-%d"),
            "message": self.message,
            "sender": self.sender,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
