# Fix: Data Source Information Shows "0 Transactions"

## Problem
The Data Source Information box shows "0 transactions" and "0 unique days" even though you added historical sales data.

## Root Cause
**Timezone mismatch** between:
- SQL script: Uses `CURRENT_DATE` (database server time)
- Python code: Was using `datetime.now()` (application server time)

If these are in different timezones, the date comparison fails.

## Solution Applied
Changed `datetime.now()` to `datetime.utcnow()` in the forecast query to match database timezone.

**File:** `backend/Admin_GMC/__init__.py` (line 959)
```python
# Before:
date_threshold = datetime.now() - timedelta(days=912)

# After:
date_threshold = datetime.utcnow() - timedelta(days=912)
```

## How to Verify the Fix

### Step 1: Check if data exists in database
Run this in pgAdmin:

```sql
SELECT 
    COUNT(*) as total,
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest
FROM sales_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '912 days';
```

### Step 2: Check specific branch-product
```sql
SELECT 
    COUNT(*) as transactions,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days
FROM sales_transactions
WHERE branch_id = 1  -- Your branch ID
  AND product_id = 2  -- Your product ID
  AND transaction_date >= CURRENT_DATE - INTERVAL '912 days';
```

### Step 3: Test the forecast
1. Go to Forecast page
2. Select a branch and product
3. Generate forecast
4. Check Data Source Information box
5. Should now show actual transaction counts!

## If Still Showing Zero

### Check 1: Verify data was actually inserted
```sql
SELECT COUNT(*) FROM sales_transactions;
```
If this returns 0, the SQL script didn't run successfully.

### Check 2: Check date range
```sql
SELECT 
    MIN(transaction_date) as earliest,
    MAX(transaction_date) as latest,
    CURRENT_DATE as today,
    CURRENT_DATE - INTERVAL '912 days' as threshold
FROM sales_transactions;
```

The `earliest` date should be >= `threshold` date.

### Check 3: Check branch/product IDs match
```sql
-- Get your actual branch IDs
SELECT id, name FROM branches;

-- Get your actual product IDs  
SELECT id, name FROM products;

-- Check if data exists for specific combination
SELECT COUNT(*) 
FROM sales_transactions
WHERE branch_id = 1 AND product_id = 2;
```

## Expected Results After Fix

After the fix, you should see:
- ✅ **Total Transactions:** 640+ (or actual count)
- ✅ **Unique Days:** 200-300 days
- ✅ **Historical Period:** 912 days (2.5 years)
- ✅ **Data Type:** "✅ Sufficient Data" (green)
- ✅ **Earliest Data:** Actual date (e.g., "2022-06-15")
- ✅ **Latest Data:** Actual date (e.g., "2024-12-31")

