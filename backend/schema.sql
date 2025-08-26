-- Database: gmc_system

CREATE TABLE IF NOT EXISTS branches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(150) NOT NULL,
  status ENUM('Operational','Maintenance','Closed') NOT NULL DEFAULT 'Operational',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  branch_id INT NOT NULL,
  rice_variant VARCHAR(100) NOT NULL,
  stock_kg INT NOT NULL DEFAULT 0,
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  availability ENUM('Available','Low Stock','Out of Stock') NOT NULL DEFAULT 'Available',
  batch_code VARCHAR(50) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inventory_branch FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

-- Seed sample branches
INSERT INTO branches (name, location, status) VALUES
  ('Marawoy', 'Marawoy, Lipa City', 'Operational'),
  ('Bulacnin', 'Bulacnin, Lipa City', 'Operational'),
  ('Malvar', 'Malvar, Batangas', 'Maintenance'),
  ('Sta. Cruz', 'Sta. Cruz, Laguna', 'Operational')
ON DUPLICATE KEY UPDATE name = VALUES(name);

