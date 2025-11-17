-- Create fresh users with plain text passwords
-- This will let your app hash them properly

-- Delete existing users first
DELETE FROM users;

-- Create admin user with plain text password
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('admin@gmc.com', 'adminpass', 'admin', NULL);

-- Create manager users with plain text passwords
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('manager_marawoy@gmc.com', 'managerpass', 'manager', 1),
  ('manager_lipa@gmc.com', 'managerpass', 'manager', 2),
  ('manager_malvar@gmc.com', 'managerpass', 'manager', 3),
  ('manager_bulacnin@gmc.com', 'managerpass', 'manager', 4),
  ('manager_boac@gmc.com', 'managerpass', 'manager', 5),
  ('manager_stacruz@gmc.com', 'managerpass', 'manager', 6);

-- Check the results
SELECT id, email, role, password_hash FROM users;
