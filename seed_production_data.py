#!/usr/bin/env python3
"""
Production Data Seeding Script for GMC Rice Warehouse
Run this after deploying to Render to initialize the database with sample data.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
from extensions import db
from models import Branch, Product, User, InventoryItem, SalesTransaction, ForecastData

def seed_branches():
    """Create initial branches"""
    print("🌿 Creating branches...")
    branches = [
        "Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"
    ]
    
    for name in branches:
        if not Branch.query.filter_by(name=name).first():
            branch = Branch(name=name, status="operational")
            db.session.add(branch)
            print(f"  ✅ Created branch: {name}")
        else:
            print(f"  ⏭️  Branch already exists: {name}")
    
    db.session.commit()

def seed_products():
    """Create initial rice products"""
    print("🌾 Creating rice products...")
    products = [
        {"name": "Jasmine Rice", "category": "premium", "description": "Premium aromatic rice"},
        {"name": "Basmati Rice", "category": "premium", "description": "Long-grain aromatic rice"},
        {"name": "White Rice", "category": "regular", "description": "Standard white rice"},
        {"name": "Brown Rice", "category": "healthy", "description": "Whole grain brown rice"},
        {"name": "Red Rice", "category": "healthy", "description": "Nutritious red rice"},
        {"name": "Wild Rice", "category": "premium", "description": "Exotic wild rice"},
        {"name": "Sticky Rice", "category": "specialty", "description": "Glutinous rice for special dishes"},
        {"name": "Black Rice", "category": "premium", "description": "Antioxidant-rich black rice"}
    ]
    
    for product_data in products:
        if not Product.query.filter_by(name=product_data["name"]).first():
            product = Product(
                name=product_data["name"],
                category=product_data["category"],
                description=product_data["description"]
            )
            db.session.add(product)
            print(f"  ✅ Created product: {product_data['name']}")
        else:
            print(f"  ⏭️  Product already exists: {product_data['name']}")
    
    db.session.commit()

def seed_users():
    """Create admin and manager users"""
    print("👥 Creating users...")
    
    # Admin user
    if not User.query.filter_by(email="admin@gmc.com").first():
        admin = User(
            email="admin@gmc.com",
            password_hash="admin123",  # Change this in production!
            role="admin",
            branch_id=None
        )
        db.session.add(admin)
        print("  ✅ Created admin user: admin@gmc.com")
    else:
        print("  ⏭️  Admin user already exists")
    
    # Manager users for each branch
    branches = Branch.query.all()
    for branch in branches:
        email = f"{branch.name.lower().replace(' ', '').replace('.', '')}.manager@gmc.com"
        if not User.query.filter_by(email=email).first():
            manager = User(
                email=email,
                password_hash="manager123",  # Change this in production!
                role="manager",
                branch_id=branch.id
            )
            db.session.add(manager)
            print(f"  ✅ Created manager: {email}")
        else:
            print(f"  ⏭️  Manager already exists: {email}")
    
    db.session.commit()

def seed_inventory():
    """Create initial inventory for each branch"""
    print("📦 Creating inventory...")
    
    branches = Branch.query.all()
    products = Product.query.all()
    
    for branch in branches:
        for product in products:
            if not InventoryItem.query.filter_by(branch_id=branch.id, product_id=product.id).first():
                # Generate realistic stock levels
                base_stock = random.randint(100, 500)
                unit_price = random.uniform(45, 85)  # Price per kg
                warn_level = base_stock * 0.2  # 20% of stock as warning level
                
                inventory = InventoryItem(
                    branch_id=branch.id,
                    product_id=product.id,
                    stock_kg=base_stock,
                    unit_price=unit_price,
                    warn_level=warn_level
                )
                db.session.add(inventory)
                print(f"  ✅ Created inventory: {product.name} in {branch.name} ({base_stock}kg)")
    
    db.session.commit()

def seed_sales_data():
    """Create sample sales transactions"""
    print("💰 Creating sample sales data...")
    
    branches = Branch.query.all()
    products = Product.query.all()
    
    # Generate sales for the last 30 days
    for days_ago in range(30):
        sale_date = datetime.now() - timedelta(days=days_ago)
        
        # Random number of sales per day (1-5)
        num_sales = random.randint(1, 5)
        
        for _ in range(num_sales):
            branch = random.choice(branches)
            product = random.choice(products)
            
            # Get inventory item
            inventory = InventoryItem.query.filter_by(
                branch_id=branch.id, 
                product_id=product.id
            ).first()
            
            if inventory:
                # Generate realistic sale quantities
                quantity = random.uniform(5, 50)  # 5-50 kg
                unit_price = inventory.unit_price
                total_amount = quantity * unit_price
                
                sale = SalesTransaction(
                    branch_id=branch.id,
                    product_id=product.id,
                    quantity_sold=quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    sold_at=sale_date
                )
                db.session.add(sale)
    
    db.session.commit()
    print("  ✅ Created sample sales transactions")

def seed_forecast_data():
    """Create sample forecast data"""
    print("🔮 Creating forecast data...")
    
    branches = Branch.query.all()
    products = Product.query.all()
    
    # Generate forecasts for the next 3 months
    for month_offset in range(1, 4):
        forecast_date = datetime.now() + timedelta(days=30 * month_offset)
        
        for branch in branches:
            for product in products:
                # Generate realistic forecast values
                base_demand = random.uniform(20, 80)  # 20-80 kg
                confidence_lower = base_demand * 0.8
                confidence_upper = base_demand * 1.2
                accuracy = random.uniform(70, 95)  # 70-95% accuracy
                
                forecast = ForecastData(
                    branch_id=branch.id,
                    product_id=product.id,
                    forecast_date=forecast_date,
                    predicted_demand=base_demand,
                    confidence_interval_lower=confidence_lower,
                    confidence_interval_upper=confidence_upper,
                    accuracy_score=accuracy
                )
                db.session.add(forecast)
    
    db.session.commit()
    print("  ✅ Created forecast data")

def main():
    """Run the seeding process"""
    print("🚀 Starting GMC Rice Warehouse data seeding...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created")
            
            # Seed data in order
            seed_branches()
            seed_products()
            seed_users()
            seed_inventory()
            seed_sales_data()
            seed_forecast_data()
            
            print("=" * 50)
            print("🎉 Data seeding completed successfully!")
            print("\n📋 Login Credentials:")
            print("  Admin: admin@gmc.com / admin123")
            print("  Manager (Marawoy): marawoymanager@gmc.com / manager123")
            print("  Manager (Lipa): lipamanager@gmc.com / manager123")
            print("  Manager (Malvar): malvarmanager@gmc.com / manager123")
            print("  Manager (Bulacnin): bulacninmanager@gmc.com / manager123")
            print("  Manager (Boac): boacmanager@gmc.com / manager123")
            print("  Manager (Sta. Cruz): stacruzmanager@gmc.com / manager123")
            print("\n⚠️  IMPORTANT: Change these passwords in production!")
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()
