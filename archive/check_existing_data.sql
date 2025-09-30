-- Check existing data in your PostgreSQL database
-- Run this FIRST to see what data you already have

-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check branches data
SELECT 'BRANCHES:' as table_name, count(*) as record_count FROM branches
UNION ALL
SELECT 'PRODUCTS:', count(*) FROM products
UNION ALL
SELECT 'USERS:', count(*) FROM users
UNION ALL
SELECT 'INVENTORY_ITEMS:', count(*) FROM inventory_items
UNION ALL
SELECT 'RESTOCK_LOGS:', count(*) FROM restock_logs
UNION ALL
SELECT 'SALES_TRANSACTIONS:', count(*) FROM sales_transactions
UNION ALL
SELECT 'FORECAST_DATA:', count(*) FROM forecast_data;

-- Show existing branches
SELECT 'EXISTING BRANCHES:' as info;
SELECT id, name, location FROM branches ORDER BY id;

-- Show existing products  
SELECT 'EXISTING PRODUCTS:' as info;
SELECT id, variant, default_price FROM products ORDER BY id;

-- Show existing users
SELECT 'EXISTING USERS:' as info;
SELECT id, email, role, branch_id FROM users ORDER BY id;
