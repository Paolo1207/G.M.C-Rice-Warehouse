-- SIMPLE VERSION: Add Historical Sales Data
-- Use this if you want a simpler, more controlled approach

-- ============================================================
-- First, check your branch and product IDs:
-- ============================================================
SELECT id, name FROM branches;
SELECT id, name FROM products;

-- ============================================================
-- Add sales for ONE branch-product combination
-- ============================================================
-- Replace the values below with your actual IDs and adjust quantities

INSERT INTO sales_transactions (branch_id, product_id, quantity_sold, unit_price, total_amount, transaction_date)
SELECT 
    1 as branch_id,  -- CHANGE: Your branch ID
    1 as product_id,  -- CHANGE: Your product ID
    -- Generate realistic daily quantities (20-35 kg range)
    ROUND((20 + (random() * 15))::numeric, 2) as quantity_sold,
    50.0 as unit_price,  -- Price per kg (adjust if needed)
    -- Calculate total (quantity × unit_price)
    ROUND(((20 + (random() * 15)) * 50)::numeric, 2) as total_amount,
    -- Generate dates for last 2.5 years (912 days)
    (CURRENT_DATE - (912 - generate_series(0, 912)))::date + 
    (random() * INTERVAL '8 hours') as transaction_date
FROM generate_series(0, 912)
WHERE random() < 0.7;  -- 70% of days have sales (realistic)

-- ============================================================
-- Add sales for ALL branch-product combinations
-- ============================================================
-- This adds data for every branch and product combination

INSERT INTO sales_transactions (branch_id, product_id, quantity_sold, unit_price, total_amount, transaction_date)
SELECT 
    b.id as branch_id,
    p.id as product_id,
    ROUND((20 + (random() * 15))::numeric, 2) as quantity_sold,
    50.0 as unit_price,  -- Price per kg (adjust if needed)
    ROUND(((20 + (random() * 15)) * 50)::numeric, 2) as total_amount,
    (CURRENT_DATE - (912 - s.series))::date + (random() * INTERVAL '8 hours') as transaction_date
FROM branches b
CROSS JOIN products p
CROSS JOIN generate_series(0, 912) s
WHERE random() < 0.7;  -- 70% of days have sales

-- ============================================================
-- Verify data was added:
-- ============================================================
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest
FROM sales_transactions;

