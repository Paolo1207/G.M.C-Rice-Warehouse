-- Quick check to see if sales_transactions data exists and matches the forecast query
-- Run this in pgAdmin to diagnose why forecasts show "0 transactions"

-- ============================================================
-- 1. Check if ANY sales_transactions exist
-- ============================================================
SELECT 
    COUNT(*) as total_transactions_all,
    MIN(transaction_date) as earliest_all,
    MAX(transaction_date) as latest_all
FROM sales_transactions;

-- ============================================================
-- 2. Check transactions in last 2.5 years (912 days)
-- ============================================================
SELECT 
    COUNT(*) as total_transactions_2_5_years,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days_2_5_years,
    MIN(transaction_date) as earliest_2_5_years,
    MAX(transaction_date) as latest_2_5_years
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '912 days';

-- ============================================================
-- 3. Check by branch and product (sample)
-- ============================================================
SELECT 
    b.id as branch_id,
    b.name as branch_name,
    p.id as product_id,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as earliest,
    MAX(st.transaction_date) as latest
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '912 days'
GROUP BY b.id, b.name, p.id, p.name
ORDER BY transaction_count DESC
LIMIT 20;

-- ============================================================
-- 4. Check specific branch-product combination
-- Replace 1 with your actual branch_id and product_id
-- ============================================================
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE branch_id = 1  -- CHANGE THIS to your branch_id
  AND product_id = 2  -- CHANGE THIS to your product_id
  AND transaction_date >= CURRENT_DATE - INTERVAL '912 days';

-- ============================================================
-- 5. Check date format and timezone issues
-- ============================================================
SELECT 
    transaction_date,
    DATE(transaction_date) as date_only,
    transaction_date AT TIME ZONE 'UTC' as utc_time,
    CURRENT_DATE as today,
    CURRENT_DATE - INTERVAL '912 days' as threshold_date
FROM sales_transactions
LIMIT 5;

-- ============================================================
-- 6. Verify the exact query the forecast uses
-- ============================================================
-- This matches the Python code exactly
SELECT 
    COUNT(*) as count,
    MIN(transaction_date) as min_date,
    MAX(transaction_date) as max_date
FROM sales_transactions
WHERE branch_id = 1  -- CHANGE THIS
  AND product_id = 2  -- CHANGE THIS
  AND transaction_date >= (CURRENT_TIMESTAMP - INTERVAL '912 days');






