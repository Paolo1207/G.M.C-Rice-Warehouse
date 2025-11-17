#!/usr/bin/env python3
"""
Simple test to add data and check API
"""

from app import create_app
from models import db, SalesTransaction, Branch, Product
from datetime import datetime, date
from sqlalchemy import func

def simple_test():
    app = create_app()
    
    with app.app_context():
        # Get first branch and product
        branch = Branch.query.first()
        product = Product.query.first()
        
        if not branch or not product:
            print("No data found")
            return
        
        # Add a simple sale for today
        today = date.today()
        now = datetime.now()
        
        sale = SalesTransaction(
            branch_id=branch.id,
            product_id=product.id,
            quantity_sold=25.0,
            unit_price=45.0,
            total_amount=1125.0,
            transaction_date=now,
            customer_name="Test Customer",
            customer_contact="09123456789"
        )
        
        db.session.add(sale)
        db.session.commit()
        
        print(f"Added sale: ₱{sale.total_amount} for {branch.name}")
        
        # Test the query
        today_sales = SalesTransaction.query.filter(
            func.date(SalesTransaction.transaction_date) == today
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        
        print(f"Today's sales total: ₱{today_sales or 0}")

if __name__ == "__main__":
    simple_test()
