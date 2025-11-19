-- QUICK ADD: Historical Sales Data for Your Products
-- This is the SIMPLEST version - just run it after setting your branch ID

-- ============================================================
-- FIRST: Get your branch ID
-- ============================================================
SELECT id, name FROM branches;

-- ============================================================
-- THEN: Replace 1 with your branch ID and run this
-- ============================================================
-- This adds ~640 transactions per product (70% of 912 days)
-- Each transaction: 15-40 kg range

INSERT INTO sales_transactions (branch_id, product_id, quantity_sold, unit_price, total_amount, transaction_date)
SELECT 
    1 as branch_id,  -- ⚠️ CHANGE THIS to your branch ID
    product_id,
    ROUND((15 + (random() * 25))::numeric, 2) as quantity_sold,  -- 15-40 kg range
    50.0 as unit_price,  -- Price per kg (adjust if needed)
    ROUND(((15 + (random() * 25)) * 50)::numeric, 2) as total_amount,  -- quantity × unit_price
    (CURRENT_DATE - (912 - s.series))::date + (random() * INTERVAL '8 hours') as transaction_date
FROM (
    SELECT unnest(ARRAY[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 31, 4]) as product_id
) p
CROSS JOIN generate_series(0, 912) s
WHERE random() < 0.7;  -- 70% of days have sales

-- ============================================================
-- VERIFY: Check how much data was added
-- ============================================================
SELECT 
    p.name as product,
    COUNT(*) as transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    ROUND(AVG(st.quantity_sold), 2) as avg_quantity
FROM sales_transactions st
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY p.name
ORDER BY unique_days DESC;

