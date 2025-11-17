#!/usr/bin/env python3
"""
Script to check if PostgreSQL tables are created
"""
import os
from sqlalchemy import create_engine, text
from models import Branch, Product, InventoryItem, RestockLog

# Database connection
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/gmcdb"
engine = create_engine(DATABASE_URL)

def check_tables():
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            
            print("🗄️  PostgreSQL Database Tables:")
            print("=" * 40)
            
            if tables:
                for table in tables:
                    print(f"✅ {table}")
                
                print(f"\n📊 Total tables found: {len(tables)}")
                
                # Check if our specific tables exist
                expected_tables = ['branches', 'products', 'inventory_items', 'restock_logs']
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if missing_tables:
                    print(f"\n⚠️  Missing tables: {missing_tables}")
                    print("💡 Run the Flask app to create the tables automatically!")
                else:
                    print("\n🎉 All required tables are present!")
                    
            else:
                print("❌ No tables found in the database")
                print("💡 Run the Flask app to create the tables automatically!")
                
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("💡 Make sure PostgreSQL is running and the database 'gmcdb' exists")

if __name__ == "__main__":
    check_tables()
