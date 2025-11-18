-- ============================================================
-- QUICK CHECK: Quantity Sold in Database
-- ============================================================
-- Simple queries to quickly verify your sales data
-- ============================================================

-- QUICK OVERVIEW: See total quantity sold
SELECT 
    'Total Transactions' AS metric,
    COUNT(*)::text AS value
FROM sales_transactions
UNION ALL
SELECT 
    'Total Quantity Sold (kg)',
    ROUND(SUM(quantity_sold), 2)::text
FROM sales_transactions
UNION ALL
SELECT 
    'Average Quantity per Transaction (kg)',
    ROUND(AVG(quantity_sold), 2)::text
FROM sales_transactions
UNION ALL
SELECT 
    'Date Range',
    MIN(transaction_date)::text || ' to ' || MAX(transaction_date)::text
FROM sales_transactions;

-- BY BRANCH: See quantity sold per branch
SELECT 
    b.name AS branch,
    COUNT(*) AS transactions,
    ROUND(SUM(st.quantity_sold), 2) AS total_kg,
    ROUND(AVG(st.quantity_sold), 2) AS avg_kg
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
GROUP BY b.id, b.name
ORDER BY total_kg DESC;

-- BY PRODUCT: See quantity sold per product
SELECT 
    p.name AS product,
    COUNT(*) AS transactions,
    ROUND(SUM(st.quantity_sold), 2) AS total_kg,
    ROUND(AVG(st.quantity_sold), 2) AS avg_kg
FROM sales_transactions st
JOIN products p ON st.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_kg DESC;

-- RECENT SALES: Last 20 transactions
SELECT 
    DATE(st.transaction_date) AS date,
    b.name AS branch,
    p.name AS product,
    st.quantity_sold AS kg,
    st.total_amount AS amount
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
ORDER BY st.transaction_date DESC
LIMIT 20;

-- CHECK SPECIFIC: Replace with your branch_id and product_id
-- Example: Check branch_id=1 (Marawoy) and product_id=7 (Jasmine Rice)
SELECT 
    DATE(st.transaction_date) AS date,
    st.quantity_sold AS kg,
    st.total_amount AS amount
FROM sales_transactions st
WHERE st.branch_id = 1    -- Change this
  AND st.product_id = 7   -- Change this
ORDER BY st.transaction_date DESC;

