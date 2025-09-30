-- Add all manager users for every branch
-- Run this in pgAdmin 4 to create all manager accounts

-- First, let's make sure we have all the branches
INSERT INTO branches (name, location, status) VALUES
  ('Marawoy', 'Marawoy, Lipa City', 'operational'),
  ('Lipa', 'Lipa, Batangas', 'operational'),
  ('Malvar', 'Malvar, Batangas', 'operational'),
  ('Bulacnin', 'Bulacnin, Lipa City', 'operational'),
  ('Boac', 'Boac, Marinduque', 'operational'),
  ('Sta. Cruz', 'Sta. Cruz, Laguna', 'operational')
ON CONFLICT (name) DO NOTHING;

-- Add all manager users with proper password hashes
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('admin@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'admin', NULL),
  ('manager_marawoy@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 1),
  ('manager_lipa@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 2),
  ('manager_malvar@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 3),
  ('manager_bulacnin@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 4),
  ('manager_boac@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 5),
  ('manager_stacruz@gmc.com', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 6)
ON CONFLICT (email) DO UPDATE SET
  password_hash = EXCLUDED.password_hash,
  role = EXCLUDED.role,
  branch_id = EXCLUDED.branch_id;

-- Verify all users were created
SELECT 
  u.id, 
  u.email, 
  u.role, 
  b.name as branch_name,
  u.password_hash
FROM users u
LEFT JOIN branches b ON u.branch_id = b.id
ORDER BY u.id;
