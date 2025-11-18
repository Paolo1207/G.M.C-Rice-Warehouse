-- SQL Queries to check forecast data availability in pgAdmin
-- Run these queries in pgAdmin to see how much data you have

-- ============================================================
-- 1. OVERALL DATA SUMMARY
-- ============================================================
SELECT 
    COUNT(*) as total_transactions,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    MAX(transaction_date) - MIN(transaction_date) as date_range_days,
    ROUND((MAX(transaction_date) - MIN(transaction_date))::numeric / 365.25, 2) as years_covered
FROM sales_transactions;

-- ============================================================
-- 2. DATA IN LAST 2-3 YEARS (for forecasting)
-- ============================================================
SELECT 
    'Last 2 Years' as period,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days_with_sales,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2 years'

UNION ALL

SELECT 
    'Last 2.5 Years' as period,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days_with_sales,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'

UNION ALL

SELECT 
    'Last 3 Years' as period,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days_with_sales,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '3 years'
ORDER BY period;

-- ============================================================
-- 3. DATA BY BRANCH AND PRODUCT (Last 2.5 Years)
-- ============================================================
SELECT 
    b.name as branch_name,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as first_sale,
    MAX(st.transaction_date) as last_sale,
    SUM(st.quantity_sold) as total_quantity_kg,
    CASE 
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 200 THEN '✅ Excellent'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 100 THEN '✅ Good'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 50 THEN '⚠️  Minimum'
        ELSE '❌ Insufficient'
    END as forecast_readiness
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.id, b.name, p.id, p.name
ORDER BY transaction_count DESC
LIMIT 50;

-- ============================================================
-- 4. MONTHLY TRANSACTION COUNT (Last 2.5 Years)
-- ============================================================
SELECT 
    TO_CHAR(transaction_date, 'YYYY-MM') as month,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    SUM(quantity_sold) as total_quantity_kg
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
ORDER BY month DESC;

-- ============================================================
-- 5. DATA GAPS CHECK (Days without sales in last 2.5 years)
-- ============================================================
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '2.5 years',
        CURRENT_DATE,
        '1 day'::interval
    )::date as date
),
sales_days AS (
    SELECT DISTINCT DATE(transaction_date) as date
    FROM sales_transactions
    WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
)
SELECT 
    COUNT(*) as total_days_in_period,
    COUNT(sd.date) as days_with_sales,
    COUNT(*) - COUNT(sd.date) as days_without_sales,
    ROUND(COUNT(sd.date)::numeric / COUNT(*)::numeric * 100, 2) as data_coverage_percent
FROM date_series ds
LEFT JOIN sales_days sd ON ds.date = sd.date;

-- ============================================================
-- 6. RECOMMENDATIONS SUMMARY
-- ============================================================
SELECT 
    CASE 
        WHEN COUNT(DISTINCT DATE(transaction_date)) >= 200 THEN 
            '✅ EXCELLENT: You have sufficient data for robust forecasting (200+ days)'
        WHEN COUNT(DISTINCT DATE(transaction_date)) >= 100 THEN 
            '✅ GOOD: You have adequate data for forecasting (100-199 days)'
        WHEN COUNT(DISTINCT DATE(transaction_date)) >= 50 THEN 
            '⚠️  MINIMUM: You have minimum data for basic forecasting (50-99 days)'
        ELSE 
            '❌ INSUFFICIENT: You need more data for reliable forecasting (<50 days)'
    END as recommendation,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    COUNT(*) as total_transactions,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';

