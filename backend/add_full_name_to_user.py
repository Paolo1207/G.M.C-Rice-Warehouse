"""
Migration script to add full_name column to User table
Run this once to update the database schema
"""
from extensions import db
from app import create_app

def add_full_name_column():
    """Add full_name column to User table"""
    app = create_app()
    with app.app_context():
        try:
            # Add the column using raw SQL (SQLAlchemy doesn't have a simple way to alter table)
            db.engine.execute("ALTER TABLE user ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)")
            print("✅ Successfully added full_name column to User table")
        except Exception as e:
            # If column already exists, that's fine
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  Column full_name already exists in User table")
            else:
                print(f"❌ Error adding full_name column: {e}")
                raise

if __name__ == "__main__":
    add_full_name_column()

