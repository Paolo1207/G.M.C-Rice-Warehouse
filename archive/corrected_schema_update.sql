-- CORRECTED Schema Update - Includes all missing columns from models.py
-- This will fix the column mismatch issues

-- Drop and recreate branches table with correct structure
DROP TABLE IF EXISTS branches CASCADE;
CREATE TABLE branches (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  location VARCHAR(255),
  status VARCHAR(32) DEFAULT 'operational'
);

-- Drop and recreate products table with correct structure  
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  category VARCHAR(120),
  barcode VARCHAR(120),
  sku VARCHAR(120),
  description TEXT,
  CONSTRAINT uq_products_name UNIQUE (name)
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  branch_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE SET NULL
);

-- Create inventory_items table
CREATE TABLE IF NOT EXISTS inventory_items (
  id SERIAL PRIMARY KEY,
  branch_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  batch_code VARCHAR(255),
  stock_kg DECIMAL(10,2) NOT NULL DEFAULT 0,
  price_per_unit DECIMAL(10,2),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

-- Create restock_logs table
CREATE TABLE IF NOT EXISTS restock_logs (
  id SERIAL PRIMARY KEY,
  inventory_item_id INTEGER NOT NULL,
  quantity_added DECIMAL(10,2) NOT NULL,
  supplier VARCHAR(255),
  note TEXT,
  created_by VARCHAR(100) DEFAULT 'Admin',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE
);

-- Create sales_transactions table
CREATE TABLE IF NOT EXISTS sales_transactions (
  id SERIAL PRIMARY KEY,
  inventory_item_id INTEGER NOT NULL,
  quantity_sold DECIMAL(10,2) NOT NULL,
  price_per_unit DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  customer_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE
);

-- Create forecast_data table
CREATE TABLE IF NOT EXISTS forecast_data (
  id SERIAL PRIMARY KEY,
  branch_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  forecast_date DATE NOT NULL,
  predicted_demand DECIMAL(10,2) NOT NULL,
  confidence_level DECIMAL(5,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

-- Insert sample branches with status
INSERT INTO branches (name, location, status) VALUES
  ('Marawoy', 'Marawoy, Lipa City', 'operational'),
  ('Lipa', 'Lipa, Batangas', 'operational'),
  ('Malvar', 'Malvar, Batangas', 'operational'),
  ('Sta. Cruz', 'Sta. Cruz, Laguna', 'operational'),
  ('Bulacnin', 'Bulacnin, Lipa City', 'operational'),
  ('Tanauan', 'Tanauan, Batangas', 'operational')
ON CONFLICT (name) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, category, barcode, sku, description) VALUES
  ('Dinorado Rice', 'Rice', 'DIN001', 'DIN-001', 'Premium Dinorado Rice'),
  ('Jasmine Rice', 'Rice', 'JAS001', 'JAS-001', 'Fragrant Jasmine Rice'),
  ('Sinaunang Barrio Rice', 'Rice', 'SIN001', 'SIN-001', 'Traditional Barrio Rice'),
  ('Wellmilled Rice', 'Rice', 'WEL001', 'WEL-001', 'Well-milled Rice'),
  ('Premium Rice', 'Rice', 'PRE001', 'PRE-001', 'Premium Quality Rice'),
  ('Special Rice', 'Rice', 'SPE001', 'SPE-001', 'Special Grade Rice')
ON CONFLICT (name) DO NOTHING;

-- Insert default users
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('admin@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'admin', NULL)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('manager_marawoy@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 1)
ON CONFLICT (email) DO NOTHING;
