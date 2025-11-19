# Forecast Data Usage Verification - 2-3 Years Historical Data

## ✅ Confirmation: 2-3 Years of Data IS Being Used

### Date Threshold in Code
**File:** `backend/Admin_GMC/__init__.py` (line 959)
```python
date_threshold = datetime.now() - timedelta(days=912)  # Approximately 2.5 years
```

**This means:**
- ✅ Retrieves data from **last 912 days**
- ✅ Which equals **2.5 years** (912 ÷ 365.25 = 2.5 years)
- ✅ Covers the **2-3 year range** you requested

## 📊 ETL Pipeline (Extract, Transform, Load)

**Note:** You mentioned "ETS" - I believe you mean **ETL** (Extract, Transform, Load) pipeline, which is what we have implemented.

### The ETL Pipeline Flow:

**File:** `backend/forecasting_service.py`

#### 1. **EXTRACT** (Line 31-40)
```python
def extract(self, historical_data: List[Dict]) -> pd.DataFrame:
    # Loads raw historical sales data from database
    # Receives all transactions from last 912 days
```
- ✅ Extracts ALL transactions from the last 912 days (2.5 years)
- ✅ Gets data for the specific branch and product

#### 2. **TRANSFORM** (Line 42-92)
```python
def transform(self, df: pd.DataFrame) -> pd.Series:
    # Converts transaction_date to datetime
    # Aggregates by day (sums quantity_sold per day)
    # Removes outliers (beyond 3 standard deviations)
    # Fills missing values
```
- ✅ Converts dates to proper format
- ✅ **Aggregates transactions to daily totals** (multiple transactions per day are summed)
- ✅ Removes outliers for data quality
- ✅ Handles missing values

#### 3. **LOAD** (Line 94-111)
```python
def load(self, data: pd.Series) -> pd.Series:
    # Final data preparation and validation
    # Ensures data is ready for modeling
```
- ✅ Final validation
- ✅ Ensures data quality
- ✅ Prepares data for model training

## 🔄 Complete Forecasting Pipeline

### Step-by-Step Process:

1. **Data Retrieval** (Admin_GMC/__init__.py line 960-966)
   - ✅ Gets sales transactions from last **912 days** (2.5 years)
   - ✅ Filters by branch_id and product_id

2. **ETL Pipeline** (forecasting_service.py)
   - ✅ **Extract:** Loads raw transactions
   - ✅ **Transform:** Aggregates to daily data, cleans data
   - ✅ **Load:** Final preparation

3. **Train/Test Split** (forecasting_service.py line 239)
   - ✅ Splits data: **80% training, 20% testing**
   - ✅ Time-series aware (keeps chronological order)

4. **Model Training** (forecasting_service.py)
   - ✅ Trains the selected model (ARIMA, RF, or Seasonal)
   - ✅ Uses the **training data** (80% of your 2.5 years)

5. **Model Evaluation** (forecasting_service.py line 251-269)
   - ✅ Tests on **test data** (20% of your 2.5 years)
   - ✅ Calculates accuracy, MAE, MAPE, RMSE

6. **Forecast Generation** (forecasting_service.py line 271-318)
   - ✅ Generates forecast for future periods
   - ✅ Uses the trained and evaluated model

## 📈 Data Usage Example

If you have data from the last 912 days:

**Example:**
- Total transactions: 640
- Unique days: 250 days
- Date range: 2022-01-01 to 2024-12-31 (912 days)

**ETL Processing:**
- Extract: 640 transactions
- Transform: 250 daily data points (aggregated)
- Load: 250 days ready for modeling

**Train/Test Split:**
- Training: 200 days (80% of 250)
- Testing: 50 days (20% of 250)

**Model Training:**
- Uses 200 days of training data
- Evaluates on 50 days of test data
- Generates forecast for future periods

## ✅ Verification Checklist

To verify your data is being used correctly:

1. **Check Data Source Information Box** (in forecast page)
   - Should show "912 days (2.5 years)" in Historical Period
   - Should show actual transaction count
   - Should show unique days with sales

2. **Check Train/Test Split**
   - Training Data should be ~80% of unique days
   - Test Data should be ~20% of unique days

3. **Run Verification Script**
   ```bash
   python verify_forecast_data_usage.py
   ```

## 🎯 Why 2-3 Years is Important

- **More data = Better accuracy:** More historical patterns to learn from
- **Seasonal patterns:** Captures multiple seasonal cycles (2-3 years = 2-3 cycles)
- **Trend detection:** Better trend identification with longer time series
- **Model reliability:** More data points = more reliable forecasts

## 📝 Summary

✅ **YES, the system IS using 2-3 years of data:**
- Date threshold: **912 days (2.5 years)**
- ETL pipeline: **Extract → Transform → Load**
- All models (ARIMA, RF, Seasonal) use this data
- Train/Test split ensures proper evaluation
- The data flows through the complete pipeline correctly

The forecasting system is correctly configured to use 2-3 years of historical data!

