#!/usr/bin/env python3
"""
Add sales data for today to test the dashboard
"""

from app import create_app
from models import db, SalesTransaction, Branch, Product
from datetime import datetime, date
import random

def add_today_sales():
    app = create_app()
    
    with app.app_context():
        print("Adding sales data for today...")
        
        # Get all branches and products
        branches = Branch.query.all()
        products = Product.query.all()
        
        if not branches or not products:
            print("No branches or products found!")
            return
        
        today = date.today()
        now = datetime.now()
        
        # Add sales for each branch and product
        for branch in branches:
            for product in products:
                # Add 1-3 sales per product per branch
                for i in range(random.randint(1, 3)):
                    quantity = random.uniform(10, 50)
                    unit_price = random.uniform(30, 60)
                    total_amount = quantity * unit_price
                    
                    # Random time today
                    hour = random.randint(8, 18)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    
                    sale_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute, second=second))
                    
                    sale = SalesTransaction(
                        branch_id=branch.id,
                        product_id=product.id,
                        quantity_sold=round(quantity, 2),
                        unit_price=round(unit_price, 2),
                        total_amount=round(total_amount, 2),
                        transaction_date=sale_time,
                        customer_name=f"Customer {i+1}",
                        customer_contact=f"09{random.randint(10000000, 99999999)}"
                    )
                    
                    db.session.add(sale)
        
        db.session.commit()
        
        # Verify
        today_sales = SalesTransaction.query.filter(
            func.date(SalesTransaction.transaction_date) == today
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        
        print(f"✅ Added sales data for today!")
        print(f"Today's total sales: ₱{today_sales or 0:,.2f}")
        print(f"Total transactions today: {SalesTransaction.query.filter(func.date(SalesTransaction.transaction_date) == today).count()}")

if __name__ == "__main__":
    add_today_sales()
