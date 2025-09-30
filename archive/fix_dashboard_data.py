#!/usr/bin/env python3
"""
Quick fix to add some sales data for today and recent days
"""

from app import create_app
from models import db, SalesTransaction, Branch, Product, InventoryItem
from datetime import datetime, date, timedelta
import random

def fix_dashboard_data():
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing Dashboard Data")
        print("=" * 30)
        
        # Get first branch and first product
        branch = Branch.query.first()
        product = Product.query.first()
        
        if not branch or not product:
            print("❌ No branches or products found!")
            return
        
        print(f"Using: {branch.name} - {product.name}")
        
        # Add sales for today and last 7 days
        for i in range(8):  # Today + 7 days ago
            sale_date = date.today() - timedelta(days=i)
            
            # Add 2-5 transactions per day
            for j in range(random.randint(2, 5)):
                quantity = random.uniform(10, 50)
                unit_price = random.uniform(30, 60)
                total_amount = quantity * unit_price
                
                # Random time during business hours
                hour = random.randint(8, 18)
                minute = random.randint(0, 59)
                
                transaction_datetime = datetime.combine(
                    sale_date, 
                    datetime.min.time().replace(hour=hour, minute=minute)
                )
                
                transaction = SalesTransaction(
                    branch_id=branch.id,
                    product_id=product.id,
                    quantity_sold=round(quantity, 2),
                    unit_price=round(unit_price, 2),
                    total_amount=round(total_amount, 2),
                    transaction_date=transaction_datetime,
                    customer_name=f"Customer {j+1}",
                    customer_contact=f"09{random.randint(10000000, 99999999)}"
                )
                
                db.session.add(transaction)
        
        db.session.commit()
        print("✅ Added sales data for today and last 7 days!")
        
        # Verify the data
        today = date.today()
        today_sales = SalesTransaction.query.filter(
            func.date(SalesTransaction.transaction_date) == today
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        
        print(f"Today's sales: ₱{today_sales or 0:,.2f}")
        
        # Check month sales
        current_month = today.month
        current_year = today.year
        month_sales = SalesTransaction.query.filter(
            and_(
                func.extract('month', SalesTransaction.transaction_date) == current_month,
                func.extract('year', SalesTransaction.transaction_date) == current_year
            )
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        
        print(f"This month's sales: ₱{month_sales or 0:,.2f}")

if __name__ == "__main__":
    fix_dashboard_data()
