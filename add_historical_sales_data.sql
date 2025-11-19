-- SQL Script to Add Historical Sales Data for Forecasting
-- Run this in pgAdmin to add sample historical sales transactions
-- Adjust dates, quantities, and branch/product IDs as needed

-- ============================================================
-- STEP 1: Check your current branches and products
-- ============================================================
-- Run these first to see what branches and products you have:

SELECT id, name FROM branches ORDER BY id;
SELECT id, name FROM products ORDER BY id;

-- ============================================================
-- STEP 2: Add Historical Sales Data (2-3 years back)
-- ============================================================
-- This script adds daily sales transactions for the last 2.5 years
-- Adjust the parameters below based on your actual data:

-- Example: Add sales for Branch ID 1, Product ID 1
-- Replace branch_id and product_id with your actual IDs

-- Generate sales for last 2.5 years (912 days)
-- This creates one transaction per day with varying quantities

DO $$
DECLARE
    v_branch_id INTEGER := 1;  -- CHANGE THIS to your branch ID
    v_product_id INTEGER := 1;  -- CHANGE THIS to your product ID
    v_base_quantity NUMERIC := 25.0;  -- Base daily quantity in kg
    v_date DATE;
    v_quantity NUMERIC;
    v_price_per_kg NUMERIC := 50.0;  -- Price per kg
    v_total_amount NUMERIC;
    v_days_back INTEGER := 912;  -- 2.5 years
    v_counter INTEGER := 0;
BEGIN
    -- Loop through last 2.5 years
    FOR i IN 0..v_days_back LOOP
        v_date := CURRENT_DATE - (v_days_back - i);
        
        -- Skip some days to make it realistic (not every day has sales)
        -- 70% chance of having a sale on any given day
        IF random() < 0.7 THEN
            -- Generate realistic quantity with variation
            -- Base quantity with weekly pattern (higher on weekdays)
            v_quantity := v_base_quantity;
            
            -- Add weekly pattern (higher sales Mon-Fri, lower on weekends)
            IF EXTRACT(DOW FROM v_date) BETWEEN 1 AND 5 THEN
                v_quantity := v_quantity * (1.0 + random() * 0.3);  -- 0-30% higher
            ELSE
                v_quantity := v_quantity * (0.7 + random() * 0.2);  -- 30-50% lower
            END IF;
            
            -- Add seasonal variation (slightly higher in certain months)
            IF EXTRACT(MONTH FROM v_date) IN (11, 12, 1, 2) THEN
                v_quantity := v_quantity * (1.1 + random() * 0.1);  -- 10-20% higher in Nov-Feb
            END IF;
            
            -- Add random variation
            v_quantity := v_quantity * (0.8 + random() * 0.4);  -- ±20% random variation
            
            -- Ensure minimum quantity
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
                transaction_date,
                batch_code
            ) VALUES (
                v_branch_id,
                v_product_id,
                v_quantity,
                v_price_per_kg,
                v_total_amount,
                v_date + (random() * INTERVAL '8 hours'),  -- Random time during day
                NULL  -- Can set batch code if needed
            );
            
            v_counter := v_counter + 1;
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Inserted % transactions for branch_id=%, product_id=%', 
        v_counter, v_branch_id, v_product_id;
END $$;

-- ============================================================
-- STEP 3: Add Data for Multiple Products (Example)
-- ============================================================
-- To add data for multiple products, run the above DO block
-- multiple times with different v_product_id values, or use this:

DO $$
DECLARE
    v_branch_id INTEGER := 1;  -- CHANGE THIS
    v_base_quantity NUMERIC := 25.0;
    v_price_per_kg NUMERIC := 50.0;
    v_date DATE;
    v_quantity NUMERIC;
    v_total_amount NUMERIC;
    v_product_record RECORD;
    v_days_back INTEGER := 912;
BEGIN
    -- Loop through all products (or specific products)
    FOR v_product_record IN 
        SELECT id FROM products 
        -- WHERE id IN (1, 2, 3)  -- Uncomment to limit to specific products
    LOOP
        -- Generate sales for each product
        FOR i IN 0..v_days_back LOOP
            v_date := CURRENT_DATE - (v_days_back - i);
            
            -- 70% chance of sale
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
                    v_branch_id, v_product_record.id, v_quantity, v_price_per_kg, v_total_amount,
                    v_date + (random() * INTERVAL '8 hours')
                );
            END IF;
        END LOOP;
        
        RAISE NOTICE 'Completed product_id=%', v_product_record.id;
    END LOOP;
END $$;

-- ============================================================
-- STEP 4: Add Data for All Branches (Comprehensive)
-- ============================================================
-- This adds historical data for all branch-product combinations

DO $$
DECLARE
    v_base_quantity NUMERIC := 25.0;
    v_price_per_kg NUMERIC := 50.0;
    v_date DATE;
    v_quantity NUMERIC;
    v_total_amount NUMERIC;
    v_branch_record RECORD;
    v_product_record RECORD;
    v_days_back INTEGER := 912;
    v_transaction_count INTEGER;
BEGIN
    -- Loop through all branches
    FOR v_branch_record IN SELECT id, name FROM branches LOOP
        -- Loop through all products
        FOR v_product_record IN SELECT id, name FROM products LOOP
            v_transaction_count := 0;
            
            -- Generate sales for last 2.5 years
            FOR i IN 0..v_days_back LOOP
                v_date := CURRENT_DATE - (v_days_back - i);
                
                -- 70% chance of sale per day
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
                        v_branch_record.id, v_product_record.id, v_quantity, v_price_per_kg, v_total_amount,
                        v_date + (random() * INTERVAL '8 hours')
                    );
                    
                    v_transaction_count := v_transaction_count + 1;
                END IF;
            END LOOP;
            
            RAISE NOTICE 'Branch: %, Product: % - Inserted % transactions', 
                v_branch_record.name, v_product_record.name, v_transaction_count;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Historical data generation completed!';
END $$;

-- ============================================================
-- STEP 5: Verify the data was added
-- ============================================================
-- Run this to check how much data you now have:

SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    MAX(transaction_date) - MIN(transaction_date) as date_range_days
FROM sales_transactions;

-- Check by branch and product:
SELECT 
    b.name as branch_name,
    p.name as product_name,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    MIN(st.transaction_date) as first_sale,
    MAX(st.transaction_date) as last_sale
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.id, b.name, p.id, p.name
ORDER BY unique_days DESC;

-- ============================================================
-- IMPORTANT NOTES:
-- ============================================================
-- 1. Adjust v_branch_id and v_product_id to match your actual IDs
-- 2. Adjust v_base_quantity based on typical daily sales (e.g., 20-30 kg)
-- 3. Adjust v_price_per_kg to match your product prices
-- 4. The script creates ~70% of days with sales (realistic pattern)
-- 5. It includes weekly patterns (higher on weekdays) and seasonal variation
-- 6. Run STEP 1 first to see your branch/product IDs
-- 7. Start with STEP 2 for one product, then expand to STEP 3 or 4
-- 8. After adding data, verify with STEP 5 queries

