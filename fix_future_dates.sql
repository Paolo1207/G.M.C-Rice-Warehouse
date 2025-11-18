-- FIX: Update future dates to be within valid range
-- Your data shows dates up to 2025-11-18 (future!)
-- This will update all future dates to be within the last 912 days

-- ============================================================
-- STEP 1: Check how many future dates exist
-- ============================================================
SELECT 
    COUNT(*) as future_transactions,
    MIN(transaction_date) as earliest_future,
    MAX(transaction_date) as latest_future
FROM sales_transactions
WHERE transaction_date > CURRENT_TIMESTAMP;

-- ============================================================
-- STEP 2: Update future dates to be within valid range
-- ============================================================
-- This updates all transactions with future dates to be within last 912 days
-- It redistributes them randomly across the valid date range

UPDATE sales_transactions
SET transaction_date = (
    CURRENT_DATE - INTERVAL '912 days' + 
    (RANDOM() * INTERVAL '912 days') +
    (RANDOM() * INTERVAL '8 hours')
)
WHERE transaction_date > CURRENT_TIMESTAMP;

-- ============================================================
-- STEP 3: Verify the fix
-- ============================================================
SELECT 
    COUNT(*) as total_transactions,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest,
    CURRENT_TIMESTAMP as now,
    CASE 
        WHEN MAX(transaction_date) <= CURRENT_TIMESTAMP THEN '✅ All dates are valid'
        ELSE '❌ Still has future dates'
    END as status
FROM sales_transactions;

-- ============================================================
-- STEP 4: Check specific branch-product after fix
-- ============================================================
SELECT 
    b.name as branch,
    p.name as product,
    COUNT(*) as transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as earliest,
    MAX(st.transaction_date) as latest
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= (CURRENT_DATE - INTERVAL '912 days')
  AND st.transaction_date <= CURRENT_TIMESTAMP
GROUP BY b.name, p.name
ORDER BY transactions DESC
LIMIT 10;

