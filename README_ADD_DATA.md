# Add Historical Sales Data - Complete Guide

## 📋 Your Setup

### Branches (6):
1. Marawoy
2. Lipa
3. Malvar
4. Bulacnin
5. Boac
6. Sta. Cruz

### Products (14):
- White rice (2)
- Sinadomeng (3)
- Sinandomeng (5)
- Dinorado (6)
- Jasmine Rice (7)
- Basmati Rice (8)
- Brown Rice (9)
- Red Rice (10)
- Sticky Rice (11)
- Wild Rice (12)
- Brown rice (14)
- Malagkit (15)
- Corn rice (31)
- Red rice (4)

**Total Combinations:** 6 branches × 14 products = **84 branch-product combinations**

## 🚀 Quick Start (Recommended)

### Use `QUICK_ADD_ALL_BRANCHES.sql`:

1. **Open pgAdmin** → Connect to your database → Query Tool

2. **Run the verification query first:**
   ```sql
   SELECT id, name FROM branches ORDER BY id;
   SELECT id, name FROM products ORDER BY id;
   ```

3. **Open `QUICK_ADD_ALL_BRANCHES.sql`** in Query Tool

4. **Run the INSERT query** - This will add data for ALL branches and ALL products in one go

5. **Wait for completion** - This will create ~53,760 transactions (takes a few minutes)

6. **Verify with the verification queries** at the bottom of the file

## 📊 What Gets Created

- **~640 transactions** per branch-product combination
- **~200-300 unique days** with sales per combination
- **2.5 years** of historical data (912 days back from today)
- **Realistic patterns:**
  - 70% of days have sales (not every day)
  - Higher sales on weekdays
  - Seasonal variation (higher in Nov-Feb)

## ⚙️ Advanced Option

### Use `add_sales_all_branches_products.sql`:

- More detailed with progress updates
- Includes weekly and seasonal patterns
- Shows progress as it runs
- Better for monitoring large data generation

## ✅ After Adding Data

### Check Your Data:

```sql
-- Overall summary
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    COUNT(DISTINCT branch_id) as branches,
    COUNT(DISTINCT product_id) as products
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';

-- Check each branch-product combination
SELECT 
    b.name as branch,
    p.name as product,
    COUNT(DISTINCT DATE(st.transaction_date)) as unique_days,
    CASE 
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 200 THEN '✅ Excellent'
        WHEN COUNT(DISTINCT DATE(st.transaction_date)) >= 100 THEN '✅ Good'
        ELSE '⚠️ Check'
    END as status
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.name, p.name
ORDER BY unique_days DESC;
```

## 🎯 Expected Results

After running, you should have:
- ✅ **84 branch-product combinations** with data
- ✅ **~200-300 unique days** per combination
- ✅ **Ready for forecasting** - All combinations will show "✅ Sufficient Data" or "✅ Good Data"

## 🔧 Customization

### Adjust Daily Quantities:
In the scripts, change:
```sql
ROUND(15 + (random() * 25), 2)  -- 15-40 kg range
```
To your actual range, e.g.:
```sql
ROUND(20 + (random() * 30), 2)  -- 20-50 kg range
```

### Adjust Price:
Change:
```sql
* 50  -- 50 pesos per kg
```
To your actual price per kg.

### Adjust Sales Frequency:
Change:
```sql
AND random() < 0.7  -- 70% of days
```
To:
```sql
AND random() < 0.8  -- 80% of days (more frequent)
```

## ⚠️ Important Notes

1. **This adds NEW data** - Won't delete existing transactions
2. **Takes time** - ~53,760 transactions takes a few minutes to insert
3. **Each branch has own inventory** - The script respects this by creating separate data per branch
4. **Test first** - Consider running for one branch first to test, then all branches

## 📈 Next Steps

After adding data:
1. ✅ Go to Forecast page in your app
2. ✅ Select any branch and product
3. ✅ Generate forecast
4. ✅ Check "Data Source Information" box - should show "✅ Sufficient Data"
5. ✅ You'll see ~200-300 unique days with sales

