-- Database: gmc_system (PostgreSQL compatible schema aligned with models.py)

-- Branches table
CREATE TABLE IF NOT EXISTS branches (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  location VARCHAR(255)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  variant VARCHAR(255) UNIQUE NOT NULL,
  default_price DECIMAL(10,2)
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  branch_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE SET NULL
);

-- Inventory Items table
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

-- Restock Logs table
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

-- Sales Transactions table
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

-- Forecast Data table
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

-- Seed sample branches
INSERT INTO branches (name, location) VALUES
  ('Marawoy', 'Marawoy, Lipa City'),
  ('Lipa', 'Lipa, Batangas'),
  ('Malvar', 'Malvar, Batangas'),
  ('Sta. Cruz', 'Sta. Cruz, Laguna'),
  ('Bulacnin', 'Bulacnin, Lipa City'),
  ('Tanauan', 'Tanauan, Batangas')
ON CONFLICT (name) DO NOTHING;

-- Seed sample products
INSERT INTO products (variant, default_price) VALUES
  ('Dinorado', 50.00),
  ('Jasmine', 45.00),
  ('Sinaunang Barrio', 55.00),
  ('Wellmilled', 40.00),
  ('Premium Rice', 60.00),
  ('Special Rice', 65.00)
ON CONFLICT (variant) DO NOTHING;

-- Create default admin user
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('admin@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'admin', NULL)
ON CONFLICT (email) DO NOTHING;

-- Create default manager user
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('manager_marawoy@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 1)
ON CONFLICT (email) DO NOTHING;
