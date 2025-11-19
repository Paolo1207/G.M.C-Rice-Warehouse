-- COMPLETE: Add Historical Sales Data for ALL Branches and ALL Products
-- This script adds 2.5 years of data for every branch-product combination

-- ============================================================
-- YOUR BRANCHES:
-- 1 = Marawoy
-- 2 = Lipa
-- 3 = Malvar
-- 4 = Bulacnin
-- 5 = Boac
-- 6 = Sta. Cruz
-- ============================================================

-- ============================================================
-- YOUR PRODUCTS:
-- 2 = white rice
-- 3 = Sinadomeng
-- 5 = Sinandomeng
-- 6 = Dinorado
-- 7 = Jasmine Rice
-- 8 = Basmati Rice
-- 9 = Brown Rice
-- 10 = Red Rice
-- 11 = Sticky Rice
-- 12 = Wild Rice
-- 14 = Brown rice
-- 15 = Malagkit
-- 31 = Corn rice
-- 4 = Red rice
-- ============================================================

-- ============================================================
-- STEP 1: Verify your branches and products exist
-- ============================================================
SELECT id, name FROM branches ORDER BY id;
SELECT id, name FROM products ORDER BY id;

-- ============================================================
-- STEP 2: Add Historical Sales Data for ALL Combinations
-- ============================================================
-- This will add ~640 transactions per branch-product combination
-- Total: 6 branches × 14 products × ~640 = ~53,760 transactions

DO $$
DECLARE
    v_base_quantity NUMERIC := 25.0;  -- Base daily quantity in kg (adjust if needed)
    v_price_per_kg NUMERIC := 50.0;  -- Price per kg (adjust to your prices)
    v_date DATE;
    v_quantity NUMERIC;
    v_total_amount NUMERIC;
    v_days_back INTEGER := 912;  -- 2.5 years
    v_branch_id INTEGER;
    v_product_id INTEGER;
    v_branch_ids INTEGER[] := ARRAY[1, 2, 3, 4, 5, 6];  -- All your branches
    v_product_ids INTEGER[] := ARRAY[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 31, 4];  -- All your products
    v_transaction_count INTEGER;
    v_total_combinations INTEGER;
    v_current_combination INTEGER := 0;
BEGIN
    v_total_combinations := array_length(v_branch_ids, 1) * array_length(v_product_ids, 1);
    RAISE NOTICE 'Starting data generation for % branch-product combinations...', v_total_combinations;
    
    -- Loop through each branch
    FOREACH v_branch_id IN ARRAY v_branch_ids LOOP
        -- Loop through each product
        FOREACH v_product_id IN ARRAY v_product_ids LOOP
            v_current_combination := v_current_combination + 1;
            v_transaction_count := 0;
            
            -- Generate sales for last 2.5 years
            FOR i IN 0..v_days_back LOOP
                v_date := CURRENT_DATE - (v_days_back - i);
                
                -- 70% chance of sale per day (realistic - not every day has sales)
                IF random() < 0.7 THEN
                    v_quantity := v_base_quantity;
                    
                    -- Weekly pattern: Higher sales on weekdays (Mon-Fri)
                    IF EXTRACT(DOW FROM v_date) BETWEEN 1 AND 5 THEN
                        v_quantity := v_quantity * (1.0 + random() * 0.3);  -- 0-30% higher
                    ELSE
                        v_quantity := v_quantity * (0.7 + random() * 0.2);  -- 30-50% lower on weekends
                    END IF;
                    
                    -- Seasonal variation: Higher in Nov-Feb (holiday season)
                    IF EXTRACT(MONTH FROM v_date) IN (11, 12, 1, 2) THEN
                        v_quantity := v_quantity * (1.1 + random() * 0.1);  -- 10-20% higher
                    END IF;
                    
                    -- Add random variation (±20%)
                    v_quantity := v_quantity * (0.8 + random() * 0.4);
                    
                    -- Ensure minimum quantity of 5 kg
                    v_quantity := GREATEST(5.0, ROUND(v_quantity, 2));
                    
                    -- Calculate total amount
                    v_total_amount := ROUND(v_quantity * v_price_per_kg, 2);
                    
                    -- Insert transaction
                    INSERT INTO sales_transactions (
                        branch_id,
                        product_id,
                        quantity_sold,
                        unit_price,
                        total_amount,
                        transaction_date
                    ) VALUES (
                        v_branch_id,
                        v_product_id,
                        v_quantity,
                        v_price_per_kg,
                        v_total_amount,
                        v_date + (random() * INTERVAL '8 hours')  -- Random time during day
                    );
                    
                    v_transaction_count := v_transaction_count + 1;
                END IF;
            END LOOP;
            
            -- Progress update every 10 combinations
            IF v_current_combination % 10 = 0 THEN
                RAISE NOTICE 'Progress: %/% combinations completed...', v_current_combination, v_total_combinations;
            END IF;
            
            RAISE NOTICE 'Branch % (ID: %), Product %: Inserted % transactions', 
                (SELECT name FROM branches WHERE id = v_branch_id), 
                v_branch_id, 
                v_product_id, 
                v_transaction_count;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE '✅ Historical data generation completed!';
    RAISE NOTICE 'Total combinations processed: %', v_total_combinations;
    RAISE NOTICE 'Expected total transactions: ~%', v_total_combinations * 640;
END $$;

-- ============================================================
-- STEP 3: Verify the data was added
-- ============================================================
-- Overall summary
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    COUNT(DISTINCT branch_id) as branches_with_data,
    COUNT(DISTINCT product_id) as products_with_data,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    ROUND((MAX(transaction_date) - MIN(transaction_date))::numeric / 365.25, 2) as years_covered
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';

-- Summary by branch
SELECT 
    b.id,
    b.name as branch_name,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    COUNT(DISTINCT st.product_id) as products_count,
    ROUND(AVG(st.quantity_sold), 2) as avg_quantity
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.id, b.name
ORDER BY b.id;

-- Summary by product
SELECT 
    p.id,
    p.name as product_name,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    COUNT(DISTINCT st.branch_id) as branches_count,
    ROUND(AVG(st.quantity_sold), 2) as avg_quantity
FROM sales_transactions st
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY p.id, p.name
ORDER BY p.id;

-- Detailed: Branch-Product combinations with forecast readiness
SELECT 
    b.name as branch_name,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as first_sale,
    MAX(st.transaction_date) as last_sale,
    ROUND(AVG(st.quantity_sold), 2) as avg_daily_quantity,
    CASE 
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 200 THEN '✅ Excellent'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 100 THEN '✅ Good'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 50 THEN '⚠️ Minimum'
        ELSE '❌ Insufficient'
    END as forecast_readiness
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.id, b.name, p.id, p.name
ORDER BY b.name, p.name;

-- Quick check: How many branch-product combinations have sufficient data?
SELECT 
    CASE 
        WHEN unique_days >= 200 THEN '✅ Excellent (200+ days)'
        WHEN unique_days >= 100 THEN '✅ Good (100-199 days)'
        WHEN unique_days >= 50 THEN '⚠️ Minimum (50-99 days)'
        ELSE '❌ Insufficient (<50 days)'
    END as data_quality,
    COUNT(*) as combinations_count
FROM (
    SELECT 
        COUNT(DISTINCT DATE(st.transaction_date)) as unique_days
    FROM sales_transactions st
    WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
    GROUP BY st.branch_id, st.product_id
) subq
GROUP BY 
    CASE 
        WHEN unique_days >= 200 THEN '✅ Excellent (200+ days)'
        WHEN unique_days >= 100 THEN '✅ Good (100-199 days)'
        WHEN unique_days >= 50 THEN '⚠️ Minimum (50-99 days)'
        ELSE '❌ Insufficient (<50 days)'
    END
ORDER BY data_quality;

