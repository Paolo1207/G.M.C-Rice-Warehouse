# Forecast Data Requirements Guide

## 📊 How Much Data Do You Need?

### For 2-3 Years of Historical Data:

**Time Period:**
- **2 years** = 730 days
- **2.5 years** (current setting) = 912 days  
- **3 years** = 1,095 days

**Data Points Needed:**
- **Minimum:** 50-100 unique days with sales transactions
- **Good:** 100-200 unique days with sales transactions
- **Excellent:** 200+ unique days with sales transactions

### Why This Matters:

The forecast system:
1. **Aggregates transactions by day** - Multiple transactions on the same day are summed
2. **Needs unique days** - Not just transaction count, but days with actual sales
3. **Requires regular data** - Gaps in data reduce forecast accuracy

## 🔍 How to Check Your Data in pgAdmin

### Option 1: Run SQL Queries in pgAdmin

Use the queries in `check_data_availability.sql` file:

1. **Overall Summary:**
```sql
SELECT 
    COUNT(*) as total_transactions,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date,
    MAX(transaction_date) - MIN(transaction_date) as date_range_days
FROM sales_transactions;
```

2. **Check Data for Specific Branch & Product:**
```sql
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    MIN(transaction_date) as earliest_date,
    MAX(transaction_date) as latest_date
FROM sales_transactions
WHERE branch_id = 1  -- Replace with your branch_id
  AND product_id = 1  -- Replace with your product_id
  AND transaction_date >= CURRENT_DATE - INTERVAL '2.5 years';
```

3. **Check All Branch-Product Combinations:**
```sql
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
WHERE st.transaction_date >= CURRENT_DATE - INTERVAL '2.5 years'
GROUP BY b.id, b.name, p.id, p.name
ORDER BY unique_days DESC;
```

### Option 2: Use the Forecast Page

When you generate a forecast, you'll now see a **"Data Source Information"** box that shows:
- ✅ Total transactions used
- ✅ Unique days with sales
- ✅ Date range (earliest to latest)
- ✅ Training/Test data split
- ⚠️ Warnings if data is insufficient

## 📈 Data Quality Indicators

The forecast page will show:

- **✅ Sufficient Data** (Green) - 100+ unique days
- **ℹ️ Minimum Data** (Blue) - 50-99 unique days  
- **⚠️ Limited Data** (Yellow) - Less than 50 unique days
- **⚠️ Estimated Data** (Yellow) - No sales history, using inventory estimates

## 💡 Recommendations

### If You Have Less Than 50 Days of Data:
- Consider reducing the historical period to 1 year instead of 2.5 years
- Focus on collecting more recent sales data
- The forecast will still work but accuracy will be lower

### If You Have 50-100 Days of Data:
- Current 2.5 year setting is fine
- Forecasts will work but more data improves accuracy
- Consider collecting data for 6+ months before relying heavily on forecasts

### If You Have 100+ Days of Data:
- ✅ Excellent! Your data is sufficient for reliable forecasting
- The 2.5 year historical period is appropriate
- Forecasts should be accurate and reliable

## 🔧 How to Add More Data

If you need more historical sales data:

1. **Import historical sales** - Use the Sales module to add past transactions
2. **Backdate transactions** - When adding sales, you can set custom dates
3. **Bulk import** - Use CSV import if you have historical data files

## 📝 Current System Settings

- **Historical Period:** 2.5 years (912 days)
- **Data Source:** SalesTransaction table
- **Aggregation:** Daily (transactions per day are summed)
- **Minimum Required:** 7 days for Seasonal, 10 days for RF, 50+ days for ARIMA

