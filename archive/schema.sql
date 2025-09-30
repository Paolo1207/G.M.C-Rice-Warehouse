-- Database: gmc_system (SQLite compatible schema aligned with models.py)

-- Branches table
CREATE TABLE IF NOT EXISTS branches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  location TEXT
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  variant TEXT UNIQUE NOT NULL,
  default_price REAL
);

-- Inventory Items table
CREATE TABLE IF NOT EXISTS inventory_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  branch_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  batch_code TEXT,
  qty_kg REAL NOT NULL DEFAULT 0,
  price_per_unit REAL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (branch_id) REFERENCES branches (id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

-- Inventory Logs table
CREATE TABLE IF NOT EXISTS inventory_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  inventory_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  qty_delta REAL NOT NULL,
  note TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (inventory_id) REFERENCES inventory_items (id) ON DELETE CASCADE
);

-- Seed sample branches
INSERT OR IGNORE INTO branches (name, location) VALUES
  ('Marawoy', 'Marawoy, Lipa City'),
  ('Bulacnin', 'Bulacnin, Lipa City'),
  ('Malvar', 'Malvar, Batangas'),
  ('Sta. Cruz', 'Sta. Cruz, Laguna');

-- Seed sample products
INSERT OR IGNORE INTO products (variant, default_price) VALUES
  ('Dinorado', 50.00),
  ('Jasmine', 45.00),
  ('Sinaunang Barrio', 55.00),
  ('Wellmilled', 40.00);
