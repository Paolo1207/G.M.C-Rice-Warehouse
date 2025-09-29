-- Fix user passwords in Render database
-- Run this in pgAdmin 4 to fix login issues

-- Check current users
SELECT id, email, role, password_hash FROM users;

-- Update admin password (simple hash that matches your local setup)
UPDATE users 
SET password_hash = 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O'
WHERE email = 'admin@gmc.com';

-- Update manager password (simple hash that matches your local setup)  
UPDATE users 
SET password_hash = 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O'
WHERE email = 'manager_marawoy@gmc.com';

-- Verify the updates
SELECT id, email, role, password_hash FROM users;
