"""
Script to check forecast data availability in PostgreSQL database
Run this in pgAdmin or via Python to check if you have enough data for 2-3 year forecasting
"""
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Fallback to local PostgreSQL
    database_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/gmcdb"

engine = create_engine(database_url)

def check_forecast_data():
    """Check data availability for forecasting"""
    
    print("=" * 80)
    print("FORECAST DATA AVAILABILITY CHECK")
    print("=" * 80)
    print()
    
    with engine.connect() as conn:
        # Check total transactions
        total_query = text("SELECT COUNT(*) as total FROM sales_transactions")
        total_result = conn.execute(total_query).fetchone()
        total_transactions = total_result[0] if total_result else 0
        
        print(f"📊 Total Sales Transactions: {total_transactions:,}")
        print()
        
        # Check date range
        date_range_query = text("""
            SELECT 
                MIN(transaction_date) as earliest_date,
                MAX(transaction_date) as latest_date,
                MAX(transaction_date) - MIN(transaction_date) as date_range_days
            FROM sales_transactions
        """)
        date_result = conn.execute(date_range_query).fetchone()
        
        if date_result and date_result[0]:
            earliest = date_result[0]
            latest = date_result[1]
            range_days = date_result[2].days if date_result[2] else 0
            
            print(f"📅 Date Range:")
            print(f"   Earliest Transaction: {earliest}")
            print(f"   Latest Transaction: {latest}")
            print(f"   Total Days Covered: {range_days} days ({range_days/365.25:.2f} years)")
            print()
            
            # Check 2-3 year requirement
            two_years_ago = datetime.now() - timedelta(days=730)
            three_years_ago = datetime.now() - timedelta(days=1095)
            two_point_five_years_ago = datetime.now() - timedelta(days=912)
            
            print(f"📈 Forecast Requirements:")
            print(f"   2 years back: {two_years_ago.strftime('%Y-%m-%d')}")
            print(f"   2.5 years back (current setting): {two_point_five_years_ago.strftime('%Y-%m-%d')}")
            print(f"   3 years back: {three_years_ago.strftime('%Y-%m-%d')}")
            print()
            
            # Check transactions in last 2-3 years
            two_year_query = text("""
                SELECT COUNT(*) as count
                FROM sales_transactions
                WHERE transaction_date >= :threshold
            """)
            
            two_year_result = conn.execute(two_year_query, {"threshold": two_years_ago}).fetchone()
            two_year_count = two_year_result[0] if two_year_result else 0
            
            two_point_five_year_result = conn.execute(two_year_query, {"threshold": two_point_five_years_ago}).fetchone()
            two_point_five_year_count = two_point_five_year_result[0] if two_point_five_year_result else 0
            
            three_year_result = conn.execute(two_year_query, {"threshold": three_years_ago}).fetchone()
            three_year_count = three_year_result[0] if three_year_result else 0
            
            print(f"📦 Transactions in Date Range:")
            print(f"   Last 2 years: {two_year_count:,} transactions")
            print(f"   Last 2.5 years: {two_point_five_year_count:,} transactions")
            print(f"   Last 3 years: {three_year_count:,} transactions")
            print()
            
            # Check daily aggregation (how many unique days with sales)
            daily_query = text("""
                SELECT 
                    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
                    COUNT(*) as total_transactions
                FROM sales_transactions
                WHERE transaction_date >= :threshold
            """)
            
            two_year_daily = conn.execute(daily_query, {"threshold": two_years_ago}).fetchone()
            two_point_five_year_daily = conn.execute(daily_query, {"threshold": two_point_five_years_ago}).fetchone()
            three_year_daily = conn.execute(daily_query, {"threshold": three_years_ago}).fetchone()
            
            print(f"📆 Daily Data Points (Unique Days with Sales):")
            if two_year_daily:
                print(f"   Last 2 years: {two_year_daily[0]:,} unique days ({two_year_daily[1]:,} total transactions)")
            if two_point_five_year_daily:
                print(f"   Last 2.5 years: {two_point_five_year_daily[0]:,} unique days ({two_point_five_year_daily[1]:,} total transactions)")
            if three_year_daily:
                print(f"   Last 3 years: {three_year_daily[0]:,} unique days ({three_year_daily[1]:,} total transactions)")
            print()
            
            # Check by branch and product
            branch_product_query = text("""
                SELECT 
                    b.name as branch_name,
                    p.name as product_name,
                    COUNT(*) as transaction_count,
                    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
                    MIN(st.transaction_date) as first_sale,
                    MAX(st.transaction_date) as last_sale
                FROM sales_transactions st
                JOIN branches b ON st.branch_id = b.id
                JOIN products p ON st.product_id = p.id
                WHERE st.transaction_date >= :threshold
                GROUP BY b.id, b.name, p.id, p.name
                ORDER BY transaction_count DESC
                LIMIT 20
            """)
            
            bp_results = conn.execute(branch_product_query, {"threshold": two_point_five_years_ago}).fetchall()
            
            print(f"🏢 Top 20 Branch-Product Combinations (Last 2.5 Years):")
            print(f"{'Branch':<20} {'Product':<25} {'Transactions':<15} {'Unique Days':<15} {'First Sale':<15} {'Last Sale':<15}")
            print("-" * 100)
            for row in bp_results:
                branch_name = row[0] or "N/A"
                product_name = row[1] or "N/A"
                trans_count = row[2] or 0
                unique_days = row[3] or 0
                first_sale = row[4].strftime('%Y-%m-%d') if row[4] else "N/A"
                last_sale = row[5].strftime('%Y-%m-%d') if row[5] else "N/A"
                print(f"{branch_name:<20} {product_name:<25} {trans_count:<15} {unique_days:<15} {first_sale:<15} {last_sale:<15}")
            print()
            
            # Recommendations
            print("=" * 80)
            print("💡 RECOMMENDATIONS:")
            print("=" * 80)
            
            if range_days < 730:
                print("⚠️  WARNING: You have less than 2 years of data!")
                print(f"   Current data span: {range_days} days ({range_days/365.25:.2f} years)")
                print("   Recommendation: Collect more historical data or reduce forecast period")
            elif range_days < 1095:
                print(f"✅ You have {range_days/365.25:.2f} years of data")
                if range_days >= 912:
                    print("   ✓ Sufficient for 2.5 year forecasting (current setting)")
                else:
                    print("   ⚠️  Consider using 2 years instead of 2.5 years")
            else:
                print(f"✅ Excellent! You have {range_days/365.25:.2f} years of data")
                print("   ✓ Sufficient for 2-3 year forecasting")
            
            if two_point_five_year_daily and two_point_five_year_daily[0] < 100:
                print()
                print("⚠️  WARNING: Less than 100 unique days with sales in last 2.5 years")
                print("   Recommendation: Ensure you have regular daily sales data")
                print("   Minimum recommended: 100+ unique days for reliable forecasting")
            
            if two_point_five_year_count < 100:
                print()
                print("⚠️  WARNING: Less than 100 transactions in last 2.5 years")
                print("   Recommendation: More transaction data needed for accurate forecasting")
            
            print()
            print("=" * 80)
            print("📝 MINIMUM DATA REQUIREMENTS FOR FORECASTING:")
            print("=" * 80)
            print("• ARIMA Model: Minimum 50-100 data points (days with sales)")
            print("• Random Forest: Minimum 100+ data points for good accuracy")
            print("• Seasonal Model: Minimum 7 days (one week) for weekly patterns")
            print()
            print("• Ideal: 200+ unique days with sales for robust forecasting")
            print("• Current setting uses 2.5 years (912 days) of historical data")
            print("=" * 80)

if __name__ == "__main__":
    try:
        check_forecast_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

