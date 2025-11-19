-- READY-TO-USE: Add Historical Sales Data for Your Products
-- This script uses your actual product IDs

-- ============================================================
-- STEP 1: Check your branch IDs first
-- ============================================================
SELECT id, name FROM branches ORDER BY id;

-- ============================================================
-- STEP 2: Add Historical Sales Data
-- ============================================================
-- Replace v_branch_id with your actual branch ID
-- This will add data for ALL your products listed below

DO $$
DECLARE
    v_branch_id INTEGER := 1;  -- ⚠️ CHANGE THIS to your branch ID (run STEP 1 first)
    v_base_quantity NUMERIC := 25.0;  -- Base daily quantity in kg (adjust if needed)
    v_price_per_kg NUMERIC := 50.0;  -- Price per kg (adjust to your prices)
    v_date DATE;
    v_quantity NUMERIC;
    v_total_amount NUMERIC;
    v_days_back INTEGER := 912;  -- 2.5 years
    v_product_id INTEGER;
    v_product_ids INTEGER[] := ARRAY[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 31, 4];  -- Your product IDs
    v_transaction_count INTEGER;
BEGIN
    -- Loop through each product
    FOREACH v_product_id IN ARRAY v_product_ids LOOP
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
        
        RAISE NOTICE 'Product ID %: Inserted % transactions', v_product_id, v_transaction_count;
    END LOOP;
    
    RAISE NOTICE '✅ Historical data generation completed for branch_id=%!', v_branch_id;
    RAISE NOTICE 'Total products processed: %', array_length(v_product_ids, 1);
END $$;

-- ============================================================
-- STEP 3: Add Data for ALL Branches (if you have multiple)
-- ============================================================
-- Uncomment and run this if you want to add data for all branches

/*
DO $$
DECLARE
    v_base_quantity NUMERIC := 25.0;
    v_price_per_kg NUMERIC := 50.0;
    v_date DATE;
    v_quantity NUMERIC;
    v_total_amount NUMERIC;
    v_branch_record RECORD;
    v_product_id INTEGER;
    v_product_ids INTEGER[] := ARRAY[2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 31, 4];
    v_days_back INTEGER := 912;
BEGIN
    -- Loop through all branches
    FOR v_branch_record IN SELECT id, name FROM branches LOOP
        -- Loop through all products
        FOREACH v_product_id IN ARRAY v_product_ids LOOP
            -- Generate sales for last 2.5 years
            FOR i IN 0..v_days_back LOOP
                v_date := CURRENT_DATE - (v_days_back - i);
                
                IF random() < 0.7 THEN
                    v_quantity := v_base_quantity;
                    
                    -- Weekly pattern
                    IF EXTRACT(DOW FROM v_date) BETWEEN 1 AND 5 THEN
                        v_quantity := v_quantity * (1.0 + random() * 0.3);
                    ELSE
                        v_quantity := v_quantity * (0.7 + random() * 0.2);
                    END IF;
                    
                    -- Seasonal variation
                    IF EXTRACT(MONTH FROM v_date) IN (11, 12, 1, 2) THEN
                        v_quantity := v_quantity * (1.1 + random() * 0.1);
                    END IF;
                    
                    v_quantity := v_quantity * (0.8 + random() * 0.4);
                    v_quantity := GREATEST(5.0, ROUND(v_quantity, 2));
                    v_total_amount := ROUND(v_quantity * v_price_per_kg, 2);
                    
                    INSERT INTO sales_transactions (
                        branch_id, product_id, quantity_sold, unit_price, total_amount,
                        transaction_date
                    ) VALUES (
                        v_branch_record.id, v_product_id, v_quantity, v_price_per_kg, v_total_amount,
                        v_date + (random() * INTERVAL '8 hours')
                    );
                END IF;
            END LOOP;
        END LOOP;
        
        RAISE NOTICE 'Completed branch: %', v_branch_record.name;
    END LOOP;
    
    RAISE NOTICE '✅ Historical data generation completed for all branches!';
END $$;
*/

-- ============================================================
-- STEP 4: Verify the data was added
-- ============================================================
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    ROUND((MAX(transaction_date) - MIN(transaction_date))::numeric / 365.25, 2) as years_covered
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';

-- Check by product:
SELECT 
    p.id,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as first_sale,
    MAX(st.transaction_date) as last_sale,
    ROUND(AVG(st.quantity_sold), 2) as avg_daily_quantity
FROM sales_transactions st
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY p.id, p.name
ORDER BY p.id;

-- Check by branch and product:
SELECT 
    b.name as branch_name,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
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
ORDER BY unique_days DESC;

