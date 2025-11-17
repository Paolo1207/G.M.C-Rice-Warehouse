#!/usr/bin/env python3
"""
Add sample sales data for testing dashboard functionality
"""

from app import create_app
from models import db, SalesTransaction, Branch, Product, InventoryItem
from datetime import datetime, timedelta, date
import random

def add_sample_sales_data():
    app = create_app()
    
    with app.app_context():
        # Get all branches and products
        branches = Branch.query.all()
        products = Product.query.all()
        
        if not branches or not products:
            print("No branches or products found. Please add them first.")
            return
        
        print(f"Found {len(branches)} branches and {len(products)} products")
        
        # Add sales data for the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        sales_count = 0
        
        for branch in branches:
            for product in products:
                # Check if this product exists in this branch's inventory
                inventory_item = InventoryItem.query.filter_by(
                    branch_id=branch.id, 
                    product_id=product.id
                ).first()
                
                if not inventory_item:
                    continue
                
                # Generate sales for this product in this branch
                base_daily_sales = random.uniform(5, 25)  # Base daily sales in kg
                unit_price = inventory_item.unit_price or random.uniform(25, 50)  # Price per kg
                
                # Add sales for each day
                current_date = start_date
                while current_date <= end_date:
                    # Add some randomness and weekend effects
                    if current_date.weekday() >= 5:  # Weekend
                        daily_sales = base_daily_sales * random.uniform(0.3, 0.7)
                    else:  # Weekday
                        daily_sales = base_daily_sales * random.uniform(0.8, 1.5)
                    
                    # Add some transactions per day (1-3 transactions)
                    num_transactions = random.randint(1, 3)
                    
                    for _ in range(num_transactions):
                        # Split daily sales across transactions
                        transaction_quantity = daily_sales / num_transactions * random.uniform(0.5, 1.5)
                        transaction_quantity = max(0.1, transaction_quantity)  # Minimum 0.1 kg
                        
                        # Add some time variation within the day
                        hour = random.randint(8, 18)  # Business hours
                        minute = random.randint(0, 59)
                        
                        transaction_datetime = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
                        
                        # Create sales transaction
                        sales_transaction = SalesTransaction(
                            branch_id=branch.id,
                            product_id=product.id,
                            quantity_sold=round(transaction_quantity, 2),
                            unit_price=round(unit_price, 2),
                            total_amount=round(transaction_quantity * unit_price, 2),
                            transaction_date=transaction_datetime,
                            customer_name=f"Customer {random.randint(1, 100)}",
                            customer_contact=f"09{random.randint(10000000, 99999999)}"
                        )
                        
                        db.session.add(sales_transaction)
                        sales_count += 1
        
        # Commit all transactions
        db.session.commit()
        
        print(f"Added {sales_count} sales transactions")
        print(f"Date range: {start_date} to {end_date}")
        
        # Show some statistics
        total_sales = db.session.query(db.func.sum(SalesTransaction.total_amount)).scalar()
        print(f"Total sales amount: ₱{total_sales:,.2f}")
        
        # Show sales by branch
        print("\nSales by branch:")
        for branch in branches:
            branch_sales = db.session.query(db.func.sum(SalesTransaction.total_amount)).filter(
                SalesTransaction.branch_id == branch.id
            ).scalar() or 0
            print(f"  {branch.name}: ₱{branch_sales:,.2f}")

if __name__ == "__main__":
    add_sample_sales_data()
