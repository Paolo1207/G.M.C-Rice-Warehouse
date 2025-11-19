-- QUICK ADD: All Branches × All Products
-- This is the FASTEST version - one query for everything

-- ============================================================
-- FIRST: Verify your data exists
-- ============================================================
SELECT id, name FROM branches ORDER BY id;
SELECT id, name FROM products ORDER BY id;

-- ============================================================
-- THEN: Run this ONE query to add data for everything
-- ============================================================
-- This adds ~640 transactions per branch-product combination
-- Total: 6 branches × 14 products = 84 combinations × ~640 = ~53,760 transactions

INSERT INTO sales_transactions (branch_id, product_id, quantity_sold, unit_price, total_amount, transaction_date)
SELECT 
    b.id as branch_id,
    p.id as product_id,
    ROUND((15 + (random() * 25))::numeric, 2) as quantity_sold,  -- 15-40 kg range
    50.0 as unit_price,  -- Price per kg (adjust if needed)
    ROUND(((15 + (random() * 25)) * 50)::numeric, 2) as total_amount,  -- quantity × unit_price
    (CURRENT_DATE - (912 - s.day_offset))::date + (random() * INTERVAL '8 hours') as transaction_date
FROM branches b
CROSS JOIN products p
CROSS JOIN generate_series(0, 912) AS s(day_offset)
WHERE 
    -- Only your branches
    b.id IN (1, 2, 3, 4, 5, 6)
    -- Only your products
    AND p.id IN (2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 31, 4)
    -- 70% of days have sales (realistic)
    AND random() < 0.7;

-- ============================================================
-- VERIFY: Check results
-- ============================================================
SELECT 
    b.name as branch,
    p.name as product,
    COUNT(*) as transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    CASE 
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 200 THEN '✅ Excellent'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 100 THEN '✅ Good'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 50 THEN '⚠️ Minimum'
        ELSE '❌ Insufficient'
    END as status
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.name, p.name
ORDER BY b.name, unique_days DESC;

-- Summary
SELECT 
    COUNT(DISTINCT branch_id) as branches,
    COUNT(DISTINCT product_id) as products,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';

