-- ============================================================
-- EXPORT HISTORICAL SALES DATA FOR GOOGLE COLAB
-- ============================================================
-- This script exports historical sales data from PostgreSQL
-- for testing ARIMA, Seasonal, and Random Forest models
-- 
-- INSTRUCTIONS:
-- 1. Open pgAdmin4 and connect to your Render PostgreSQL database
-- 2. Open Query Tool (Tools > Query Tool)
-- 3. Run the queries below to export data
-- 4. Export results as CSV
-- 5. Upload CSV to Google Colab
-- ============================================================

-- ============================================================
-- OPTION 1: Export ALL Historical Data (All Branches & Products)
-- ============================================================
-- This exports all sales transactions aggregated by day
-- Best for comprehensive analysis across all branches/products

SELECT 
    DATE(transaction_date) as date,
    branch_id,
    product_id,
    b.name as branch_name,
    p.name as product_name,
    SUM(quantity_sold) as daily_quantity_sold,
    AVG(unit_price) as avg_unit_price,
    SUM(total_amount) as daily_total_amount,
    COUNT(*) as transaction_count
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE transaction_date >= CURRENT_DATE - INTERVAL '3 years'  -- Last 3 years
  AND transaction_date <= CURRENT_DATE  -- Up to today
GROUP BY DATE(transaction_date), branch_id, product_id, b.name, p.name
ORDER BY date ASC, branch_id ASC, product_id ASC;

-- ============================================================
-- OPTION 2: Export Data for Specific Branch & Product
-- ============================================================
-- Use this if you want to test models for a specific combination
-- Replace branch_id and product_id with your values

SELECT 
    DATE(transaction_date) as date,
    branch_id,
    product_id,
    b.name as branch_name,
    p.name as product_name,
    SUM(quantity_sold) as daily_quantity_sold,
    AVG(unit_price) as avg_unit_price,
    SUM(total_amount) as daily_total_amount,
    COUNT(*) as transaction_count
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE branch_id = 1  -- CHANGE THIS to your branch_id
  AND product_id = 1  -- CHANGE THIS to your product_id
  AND transaction_date >= CURRENT_DATE - INTERVAL '3 years'
  AND transaction_date <= CURRENT_DATE
GROUP BY DATE(transaction_date), branch_id, product_id, b.name, p.name
ORDER BY date ASC;

-- ============================================================
-- OPTION 3: Export Aggregated Data (All Products per Branch)
-- ============================================================
-- This aggregates all products together per branch per day
-- Useful for branch-level forecasting

SELECT 
    DATE(transaction_date) as date,
    branch_id,
    b.name as branch_name,
    SUM(quantity_sold) as daily_quantity_sold,
    AVG(unit_price) as avg_unit_price,
    SUM(total_amount) as daily_total_amount,
    COUNT(DISTINCT product_id) as products_sold_count,
    COUNT(*) as transaction_count
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
WHERE transaction_date >= CURRENT_DATE - INTERVAL '3 years'
  AND transaction_date <= CURRENT_DATE
GROUP BY DATE(transaction_date), branch_id, b.name
ORDER BY date ASC, branch_id ASC;

-- ============================================================
-- OPTION 4: Simple Time Series Format (Date + Quantity Only)
-- ============================================================
-- Minimal format for time series models
-- Best for ARIMA, Seasonal, Random Forest

SELECT 
    DATE(transaction_date) as date,
    SUM(quantity_sold) as quantity_sold
FROM sales_transactions
WHERE branch_id = 1  -- CHANGE THIS
  AND product_id = 1  -- CHANGE THIS
  AND transaction_date >= CURRENT_DATE - INTERVAL '3 years'
  AND transaction_date <= CURRENT_DATE
GROUP BY DATE(transaction_date)
ORDER BY date ASC;

-- ============================================================
-- OPTION 5: Export with Date Range Filter
-- ============================================================
-- Export data for a specific date range

SELECT 
    DATE(transaction_date) as date,
    branch_id,
    product_id,
    b.name as branch_name,
    p.name as product_name,
    SUM(quantity_sold) as daily_quantity_sold,
    AVG(unit_price) as avg_unit_price,
    SUM(total_amount) as daily_total_amount
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE transaction_date >= '2022-01-01'  -- CHANGE START DATE
  AND transaction_date <= '2024-12-31'  -- CHANGE END DATE
GROUP BY DATE(transaction_date), branch_id, product_id, b.name, p.name
ORDER BY date ASC;

-- ============================================================
-- CHECK YOUR DATA FIRST
-- ============================================================
-- Run these queries first to see what data you have:

-- Check total transactions and date range
SELECT 
    COUNT(*) as total_transactions,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    MAX(transaction_date) - MIN(transaction_date) as date_range_days
FROM sales_transactions;

-- Check branches and products
SELECT id, name FROM branches ORDER BY id;
SELECT id, name FROM products ORDER BY id;

-- Check data availability per branch-product combination
SELECT 
    b.name as branch_name,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as first_sale,
    MAX(st.transaction_date) as last_sale,
    SUM(st.quantity_sold) as total_quantity_sold
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.name, p.name
ORDER BY unique_days DESC;


