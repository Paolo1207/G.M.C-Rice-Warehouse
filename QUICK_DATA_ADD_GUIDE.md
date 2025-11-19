# Quick Guide: Adding Historical Sales Data in pgAdmin

## 🎯 Goal
Add 2-3 years of historical sales data so the forecast system has enough data to work with.

## 📋 Step-by-Step Instructions

### Step 1: Connect to Your Database in pgAdmin
1. Open pgAdmin
2. Connect to your Render PostgreSQL database
3. Navigate to your database (usually `gmcdb` or similar)
4. Right-click on your database → **Query Tool**

### Step 2: Check Your Current Data
Run this first to see what you have:

```sql
-- Check total transactions
SELECT COUNT(*) as total_transactions FROM sales_transactions;

-- Check date range
SELECT 
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days
FROM sales_transactions;

-- Check by branch and product
SELECT 
    b.name as branch,
    p.name as product,
    COUNT(*) as transactions,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.name, p.name
ORDER BY unique_days DESC;
```

### Step 3: Get Your Branch and Product IDs
```sql
SELECT id, name FROM branches ORDER BY id;
SELECT id, name FROM products ORDER BY id;
```

**Note down the IDs** - you'll need them in the next step.

### Step 4: Add Historical Data

#### Option A: Simple Method (Recommended for Testing)
Use `add_historical_sales_simple.sql`:
1. Open the file in pgAdmin Query Tool
2. Replace branch_id and product_id with your actual IDs
3. Adjust quantities if needed (default: 20-35 kg per day)
4. Run the query

#### Option B: Advanced Method (More Realistic Patterns)
Use `add_historical_sales_data.sql`:
1. Open the file in pgAdmin Query Tool
2. Modify the variables at the top:
   - `v_branch_id` - Your branch ID
   - `v_product_id` - Your product ID
   - `v_base_quantity` - Typical daily sales (e.g., 25 kg)
   - `v_price_per_kg` - Your product price
3. Run the DO block

### Step 5: Verify Data Was Added
```sql
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';
```

You should see:
- **Total transactions:** Should be in hundreds or thousands
- **Unique days:** Should be 200+ for good forecasting
- **Date range:** Should cover last 2.5 years

## 📊 What the Scripts Create

The scripts generate:
- **~70% of days** have sales (realistic - not every day has sales)
- **Weekly patterns:** Higher sales on weekdays (Mon-Fri), lower on weekends
- **Seasonal variation:** Slightly higher in Nov-Feb (holiday season)
- **Random variation:** ±20% daily variation for realism
- **Quantity range:** Typically 15-40 kg per day (adjustable)

## ⚙️ Customization

### Adjust Daily Quantities
Change `v_base_quantity` or the quantity range:
```sql
-- For higher volume (30-50 kg per day)
v_base_quantity := 40.0;

-- For lower volume (10-20 kg per day)
v_base_quantity := 15.0;
```

### Adjust Sales Frequency
Change the probability of sales per day:
```sql
-- 80% of days have sales (more frequent)
IF random() < 0.8 THEN

-- 50% of days have sales (less frequent)
IF random() < 0.5 THEN
```

### Add Specific Date Ranges
To add data for a specific period:
```sql
-- Add data for last 1 year only
v_days_back := 365;

-- Add data for last 6 months
v_days_back := 180;
```

## ✅ After Adding Data

1. **Check the forecast page** - Generate a forecast and see the "Data Source Information" box
2. **Verify unique days** - Should show 100+ unique days for good forecasting
3. **Test different products** - Add data for multiple products to test forecasting

## 🚨 Important Notes

- **Don't duplicate existing data** - The scripts add NEW transactions, they won't delete existing ones
- **Start small** - Test with one branch-product first, then expand
- **Adjust quantities** - Match the quantities to your actual business patterns
- **Backup first** - Consider backing up your database before adding large amounts of data

## 📈 Expected Results

After running the scripts, you should have:
- **200-300+ unique days** with sales per branch-product combination
- **2.5 years** of historical data
- **Sufficient data** for reliable forecasting

The forecast system will then use this data for:
- ✅ ETL pipeline processing
- ✅ Train/test split (80/20)
- ✅ Model training (ARIMA, RF, Seasonal)
- ✅ Model evaluation and selection
- ✅ Accurate forecasts

