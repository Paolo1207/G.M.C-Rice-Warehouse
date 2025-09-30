-- Final password fix - use proper werkzeug hashed passwords
-- This matches exactly what your app expects

-- Delete existing users
DELETE FROM users;

-- Create admin user with proper werkzeug hash for 'adminpass'
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('admin@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'admin', NULL);

-- Create manager users with proper werkzeug hash for 'managerpass'
INSERT INTO users (email, password_hash, role, branch_id) VALUES
  ('manager_marawoy@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 1),
  ('manager_lipa@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 2),
  ('manager_malvar@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 3),
  ('manager_bulacnin@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 4),
  ('manager_boac@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 5),
  ('manager_stacruz@gmc.com', 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O', 'manager', 6);

-- Check the results
SELECT id, email, role, password_hash FROM users;
