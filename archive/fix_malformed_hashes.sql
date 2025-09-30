-- Fix malformed password hashes in Render database
-- Copy and paste these commands into pgAdmin 4

-- Admin user with proper pbkdf2:sha256 hash for 'adminpass'
UPDATE users SET password_hash = 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O' WHERE email = 'admin@gmc.com';

-- Manager users with proper pbkdf2:sha256 hash for 'managerpass'  
UPDATE users SET password_hash = 'pbkdf2:sha256:600000$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4L/8KzKz2O' WHERE role = 'manager';

-- Verify the fix
SELECT email, role, password_hash FROM users;
