-- Simple password fix - use the exact same hash as your local working system
-- Run this in pgAdmin 4

-- Check current users first
SELECT id, email, role, password_hash FROM users;

-- Update admin password to match your local system
UPDATE users 
SET password_hash = 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O'
WHERE email = 'admin@gmc.com';

-- Update manager password to match your local system
UPDATE users 
SET password_hash = 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O'
WHERE email = 'manager_marawoy@gmc.com';

-- Check the results
SELECT id, email, role, password_hash FROM users;
