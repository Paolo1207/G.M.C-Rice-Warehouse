-- DIAGNOSTIC: Why Data Source Information Shows "0 Transactions"
-- Run these queries in pgAdmin to find the issue

-- ============================================================
-- STEP 1: Check if data exists at all
-- ============================================================
SELECT 
    'Total Transactions in Database' as check_type,
    COUNT(*) as count,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest
FROM sales_transactions;

-- ============================================================
-- STEP 2: Check date range of your data
-- ============================================================
SELECT 
    'Date Range Check' as check_type,
    MIN(transaction_date) as earliest_transaction,
    MAX(transaction_date) as latest_transaction,
    CURRENT_DATE as today,
    CURRENT_DATE - INTERVAL '912 days' as threshold_date_912_days,
    CASE 
        WHEN MIN(transaction_date) >= (CURRENT_DATE - INTERVAL '912 days') THEN '✅ Data is within range'
        ELSE '❌ Data is OLDER than 912 days - this is the problem!'
    END as status
FROM sales_transactions;

-- ============================================================
-- STEP 3: Check if dates are in the FUTURE (wrong timezone)
-- ============================================================
SELECT 
    'Future Date Check' as check_type,
    COUNT(*) as future_transactions,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE transaction_date > CURRENT_TIMESTAMP;

-- If this shows transactions, your dates are in the future!

-- ============================================================
-- STEP 4: Check specific branch-product combinations
-- ============================================================
SELECT 
    b.id as branch_id,
    b.name as branch_name,
    p.id as product_id,
    p.name as product_name,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest,
    CASE 
        WHEN MIN(transaction_date) >= (CURRENT_DATE - INTERVAL '912 days') THEN '✅ In Range'
        ELSE '❌ Out of Range'
    END as in_range
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.id, b.name, p.id, p.name
ORDER BY total_transactions DESC
LIMIT 20;

-- ============================================================
-- STEP 5: Check what the Python query would find
-- ============================================================
-- This simulates the exact Python query
SELECT 
    'Python Query Simulation' as check_type,
    COUNT(*) as transactions_found,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days_found
FROM sales_transactions
WHERE branch_id = 1  -- CHANGE to your branch_id
  AND product_id = 2  -- CHANGE to your product_id
  AND transaction_date >= (CURRENT_TIMESTAMP - INTERVAL '912 days');

-- ============================================================
-- STEP 6: Check timezone issues
-- ============================================================
SELECT 
    transaction_date,
    transaction_date::date as date_only,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - transaction_date)) / 86400 as days_ago,
    CASE 
        WHEN transaction_date >= (CURRENT_TIMESTAMP - INTERVAL '912 days') THEN '✅ In Range'
        ELSE '❌ Out of Range'
    END as status
FROM sales_transactions
ORDER BY transaction_date DESC
LIMIT 10;

-- ============================================================
-- STEP 7: FIX - If dates are too old, update them
-- ============================================================
-- ONLY RUN THIS IF YOUR DATES ARE TOO OLD!
-- This will update all transaction dates to be within the last 912 days

/*
UPDATE sales_transactions
SET transaction_date = (
    CURRENT_DATE - INTERVAL '912 days' + 
    (RANDOM() * INTERVAL '912 days') +
    (RANDOM() * INTERVAL '8 hours')
)
WHERE transaction_date < (CURRENT_DATE - INTERVAL '912 days');
*/

-- ============================================================
-- STEP 8: Verify after fix
-- ============================================================
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest
FROM sales_transactions
WHERE transaction_date >= (CURRENT_DATE - INTERVAL '912 days');

