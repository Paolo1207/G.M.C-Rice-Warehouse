#!/usr/bin/env python3
"""
Quick script to add some sample sales data for testing
"""

from app import create_app
from models import db, SalesTransaction, Branch, Product, InventoryItem
from datetime import datetime, timedelta, date
import random

def quick_add_sales():
    app = create_app()
    
    with app.app_context():
        # Get first branch and first product for quick test
        branch = Branch.query.first()
        product = Product.query.first()
        
        if not branch or not product:
            print("No branches or products found!")
            return
        
        print(f"Adding sales data for {branch.name} - {product.name}")
        
        # Add sales for the last 7 days
        for i in range(7):
            sale_date = date.today() - timedelta(days=i)
            
            # Add 1-3 transactions per day
            for j in range(random.randint(1, 3)):
                quantity = random.uniform(5, 25)
                unit_price = random.uniform(30, 50)
                total_amount = quantity * unit_price
                
                transaction = SalesTransaction(
                    branch_id=branch.id,
                    product_id=product.id,
                    quantity_sold=round(quantity, 2),
                    unit_price=round(unit_price, 2),
                    total_amount=round(total_amount, 2),
                    transaction_date=datetime.combine(sale_date, datetime.min.time().replace(hour=random.randint(8, 18))),
                    customer_name=f"Test Customer {j+1}",
                    customer_contact=f"09{random.randint(10000000, 99999999)}"
                )
                
                db.session.add(transaction)
        
        db.session.commit()
        print("✅ Added sample sales data!")

if __name__ == "__main__":
    quick_add_sales()
