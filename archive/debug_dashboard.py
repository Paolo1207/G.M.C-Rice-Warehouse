#!/usr/bin/env python3
"""
Debug script to check dashboard data
"""

from app import create_app
from models import db, SalesTransaction, InventoryItem, ForecastData, Branch, Product
from datetime import date, timedelta
from sqlalchemy import func, and_

def debug_dashboard():
    app = create_app()
    
    with app.app_context():
        print("🔍 Debugging Dashboard Data")
        print("=" * 50)
        
        # Check basic counts
        print(f"Sales transactions: {SalesTransaction.query.count()}")
        print(f"Inventory items: {InventoryItem.query.count()}")
        print(f"Forecast data: {ForecastData.query.count()}")
        print(f"Branches: {Branch.query.count()}")
        print(f"Products: {Product.query.count()}")
        
        # Check today's date
        today = date.today()
        print(f"\nToday's date: {today}")
        
        # Check sales data
        print("\n📊 Sales Data Analysis:")
        
        # All sales
        all_sales = SalesTransaction.query.with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        print(f"Total sales amount: ₱{all_sales or 0:,.2f}")
        
        # Today's sales
        today_sales = SalesTransaction.query.filter(
            func.date(SalesTransaction.transaction_date) == today
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        print(f"Today's sales: ₱{today_sales or 0:,.2f}")
        
        # This month's sales
        current_month = today.month
        current_year = today.year
        month_sales = SalesTransaction.query.filter(
            and_(
                func.extract('month', SalesTransaction.transaction_date) == current_month,
                func.extract('year', SalesTransaction.transaction_date) == current_year
            )
        ).with_entities(func.sum(SalesTransaction.total_amount)).scalar()
        print(f"This month's sales: ₱{month_sales or 0:,.2f}")
        
        # Check recent sales dates
        recent_sales = SalesTransaction.query.order_by(SalesTransaction.transaction_date.desc()).limit(5).all()
        print(f"\nRecent sales transactions:")
        for sale in recent_sales:
            print(f"  {sale.transaction_date.date()} - ₱{sale.total_amount:,.2f} ({sale.quantity_sold}kg)")
        
        # Check inventory data
        print("\n📦 Inventory Data Analysis:")
        
        # Low stock items
        low_stock = InventoryItem.query.filter(
            and_(
                InventoryItem.warn_level.isnot(None),
                InventoryItem.stock_kg <= InventoryItem.warn_level
            )
        ).count()
        print(f"Low stock items (with warn_level): {low_stock}")
        
        # Items without warn_level
        no_warn_level = InventoryItem.query.filter(InventoryItem.warn_level.is_(None)).count()
        print(f"Items without warn_level: {no_warn_level}")
        
        # Average stock
        avg_stock = InventoryItem.query.with_entities(func.avg(InventoryItem.stock_kg)).scalar()
        print(f"Average stock: {avg_stock or 0:.2f} kg")
        
        # Check forecast data
        print("\n🔮 Forecast Data Analysis:")
        
        # Recent forecasts
        recent_forecasts = ForecastData.query.order_by(ForecastData.forecast_date.desc()).limit(5).all()
        print(f"Recent forecasts:")
        for forecast in recent_forecasts:
            print(f"  {forecast.forecast_date} - {forecast.predicted_demand:.2f}kg ({forecast.model_type})")
        
        # Check if we have sales data for today
        print(f"\n🎯 Today's Sales Check:")
        today_transactions = SalesTransaction.query.filter(
            func.date(SalesTransaction.transaction_date) == today
        ).all()
        print(f"Transactions today: {len(today_transactions)}")
        
        if not today_transactions:
            print("❌ No sales transactions for today!")
            print("💡 This is why Today's Sales shows ₱0")
            
            # Check if we have any recent sales
            recent_date = SalesTransaction.query.order_by(SalesTransaction.transaction_date.desc()).first()
            if recent_date:
                print(f"Most recent sale: {recent_date.transaction_date.date()}")
            else:
                print("No sales transactions found at all!")

if __name__ == "__main__":
    debug_dashboard()
