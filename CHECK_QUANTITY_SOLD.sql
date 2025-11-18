-- ============================================================
-- CHECK QUANTITY SOLD IN DATABASE
-- ============================================================
-- This script helps you verify the sales data (quantity_sold) 
-- that was inserted into the sales_transactions table
-- ============================================================

-- 1. OVERVIEW: Total quantity sold by product and branch
-- Shows summary of all sales data
SELECT 
    b.name AS branch_name,
    p.name AS product_name,
    COUNT(st.id) AS total_transactions,
    SUM(st.quantity_sold) AS total_quantity_sold_kg,
    AVG(st.quantity_sold) AS avg_quantity_per_transaction,
    MIN(st.quantity_sold) AS min_quantity,
    MAX(st.quantity_sold) AS max_quantity,
    MIN(st.transaction_date) AS earliest_sale,
    MAX(st.transaction_date) AS latest_sale
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.id, b.name, p.id, p.name
ORDER BY b.name, p.name;

-- 2. QUANTITY SOLD BY DATE (Last 30 days)
-- Shows daily sales totals
SELECT 
    DATE(st.transaction_date) AS sale_date,
    b.name AS branch_name,
    p.name AS product_name,
    COUNT(st.id) AS transactions_count,
    SUM(st.quantity_sold) AS total_quantity_kg,
    AVG(st.quantity_sold) AS avg_quantity_kg
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(st.transaction_date), b.name, p.name
ORDER BY sale_date DESC, b.name, p.name;

-- 3. RECENT TRANSACTIONS (Last 50 transactions)
-- Shows individual transaction details
SELECT 
    st.id,
    st.transaction_date,
    b.name AS branch_name,
    p.name AS product_name,
    st.quantity_sold AS quantity_kg,
    st.unit_price,
    st.total_amount,
    st.branch_id,
    st.product_id
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
ORDER BY st.transaction_date DESC
LIMIT 50;

-- 4. QUANTITY SOLD BY BRANCH (Summary)
-- Shows total quantity sold per branch
SELECT 
    b.name AS branch_name,
    COUNT(DISTINCT st.product_id) AS products_sold,
    COUNT(st.id) AS total_transactions,
    SUM(st.quantity_sold) AS total_quantity_kg,
    AVG(st.quantity_sold) AS avg_quantity_kg,
    MIN(st.transaction_date) AS first_sale,
    MAX(st.transaction_date) AS last_sale
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
GROUP BY b.id, b.name
ORDER BY total_quantity_kg DESC;

-- 5. QUANTITY SOLD BY PRODUCT (Summary)
-- Shows total quantity sold per product across all branches
SELECT 
    p.name AS product_name,
    COUNT(DISTINCT st.branch_id) AS branches_selling,
    COUNT(st.id) AS total_transactions,
    SUM(st.quantity_sold) AS total_quantity_kg,
    AVG(st.quantity_sold) AS avg_quantity_kg,
    MIN(st.transaction_date) AS first_sale,
    MAX(st.transaction_date) AS last_sale
FROM sales_transactions st
JOIN products p ON st.product_id = p.id
GROUP BY p.id, p.name
ORDER BY total_quantity_kg DESC;

-- 6. CHECK SPECIFIC BRANCH AND PRODUCT
-- Replace branch_id and product_id with your values
-- Example: Check "Jasmine Rice" at "Marawoy" branch
SELECT 
    st.id,
    st.transaction_date,
    st.quantity_sold AS quantity_kg,
    st.unit_price,
    st.total_amount
FROM sales_transactions st
WHERE st.branch_id = 1  -- Change this to your branch_id (1=Marawoy, 2=Lipa, etc.)
  AND st.product_id = 7  -- Change this to your product_id (check products table)
ORDER BY st.transaction_date DESC
LIMIT 100;

-- 7. DATE RANGE CHECK
-- Check quantity sold in a specific date range
SELECT 
    DATE(st.transaction_date) AS sale_date,
    b.name AS branch_name,
    p.name AS product_name,
    COUNT(st.id) AS transactions,
    SUM(st.quantity_sold) AS total_quantity_kg
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= '2023-05-21'  -- Change start date
  AND st.transaction_date <= CURRENT_DATE   -- Change end date
GROUP BY DATE(st.transaction_date), b.name, p.name
ORDER BY sale_date DESC;

-- 8. QUICK COUNT: Total transactions and quantity
-- Fast overview of all data
SELECT 
    COUNT(*) AS total_transactions,
    SUM(quantity_sold) AS total_quantity_sold_kg,
    AVG(quantity_sold) AS avg_quantity_kg,
    MIN(transaction_date) AS earliest_date,
    MAX(transaction_date) AS latest_date,
    COUNT(DISTINCT branch_id) AS branches_with_sales,
    COUNT(DISTINCT product_id) AS products_sold
FROM sales_transactions;

-- 9. CHECK FOR ZERO OR NULL QUANTITIES
-- Find any problematic records
SELECT 
    st.id,
    st.transaction_date,
    b.name AS branch_name,
    p.name AS product_name,
    st.quantity_sold,
    st.unit_price,
    st.total_amount
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.quantity_sold IS NULL 
   OR st.quantity_sold <= 0
ORDER BY st.transaction_date DESC;

-- 10. VERIFY DATA FOR FORECASTING
-- Check data that would be used for forecasting (last 2-3 years)
SELECT 
    b.name AS branch_name,
    p.name AS product_name,
    COUNT(st.id) AS transactions,
    SUM(st.quantity_sold) AS total_quantity_kg,
    COUNT(DISTINCT DATE(st.transaction_date)) AS unique_days,
    MIN(st.transaction_date) AS earliest_date,
    MAX(st.transaction_date) AS latest_date,
    DATE_PART('day', MAX(st.transaction_date) - MIN(st.transaction_date)) AS days_span
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '912 days'  -- ~2.5 years
  AND st.transaction_date <= CURRENT_DATE
GROUP BY b.id, b.name, p.id, p.name
HAVING COUNT(st.id) > 0
ORDER BY b.name, p.name;

