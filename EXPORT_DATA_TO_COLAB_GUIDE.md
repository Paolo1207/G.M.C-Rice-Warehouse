# 📊 Export Historical Data to Google Colab Guide

This guide will help you export historical sales data from your Render PostgreSQL database (via pgAdmin4) to test ARIMA, Seasonal, and Random Forest models in Google Colab.

## 🎯 What Data You Need

For time series forecasting models, you need:
- **Date** (transaction_date aggregated by day)
- **Quantity Sold** (daily aggregated quantity_sold)
- **Optional:** Branch ID, Product ID, Unit Price, Total Amount

## 📋 Step-by-Step Instructions

### Step 1: Connect to Your Database in pgAdmin4

1. Open **pgAdmin4**
2. Connect to your **Render PostgreSQL database**
   - Right-click on your server → **Connect**
   - Enter your credentials if prompted

### Step 2: Open Query Tool

1. Right-click on your database → **Query Tool**
2. Or use shortcut: **Tools → Query Tool**

### Step 3: Run Export Query

1. Open the file `export_historical_data_for_colab.sql`
2. Choose the appropriate query based on your needs:
   - **Option 1:** All branches & products (comprehensive)
   - **Option 2:** Specific branch & product (recommended for testing)
   - **Option 3:** Aggregated by branch (branch-level forecasting)
   - **Option 4:** Simple format (date + quantity only)
   - **Option 5:** Custom date range

3. **Modify the query** if needed:
   - Change `branch_id = 1` to your actual branch ID
   - Change `product_id = 1` to your actual product ID
   - Adjust date ranges if needed

4. **Run the query** (F5 or Execute button)

### Step 4: Export Results as CSV

1. After query executes, you'll see results in the **Data Output** tab
2. **Right-click** on the results grid
3. Select **Save As...** or **Export/Import → Export...**
4. Choose format: **CSV**
5. Save the file (e.g., `historical_sales_data.csv`)

**Alternative Method:**
- Click the **Download CSV** button (if available in pgAdmin4)
- Or use: **File → Download → CSV**

### Step 5: Upload to Google Colab

1. Open **Google Colab** (colab.research.google.com)
2. Create a new notebook
3. Upload your CSV file:
   ```python
   from google.colab import files
   uploaded = files.upload()
   ```
4. Or use the **Files** sidebar → **Upload** button

## 📝 Sample Google Colab Notebook Structure

Here's a template for testing your 3 models:

```python
# ============================================================
# IMPORT LIBRARIES
# ============================================================
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Time Series Libraries
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

# ============================================================
# LOAD DATA
# ============================================================
# Upload your CSV file first, then:
df = pd.read_csv('historical_sales_data.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Sort by date
df = df.sort_values('date').reset_index(drop=True)

# Set date as index
df.set_index('date', inplace=True)

# Use daily_quantity_sold as the time series
ts = df['daily_quantity_sold']

# Display data info
print(f"Data shape: {df.shape}")
print(f"Date range: {ts.index.min()} to {ts.index.min()}")
print(f"Total data points: {len(ts)}")
print(f"\nFirst 10 rows:")
print(ts.head(10))

# ============================================================
# DATA PREPROCESSING (ETL Pipeline)
# ============================================================
# 1. Fill missing dates (if any)
date_range = pd.date_range(start=ts.index.min(), end=ts.index.max(), freq='D')
ts = ts.reindex(date_range, fill_value=0)

# 2. Remove outliers (beyond 3 standard deviations)
mean = ts.mean()
std = ts.std()
ts = ts.clip(lower=0, upper=mean + 3*std)

# 3. Ensure no negative values
ts = ts.clip(lower=0)

print(f"\nAfter preprocessing:")
print(f"Data points: {len(ts)}")
print(f"Mean: {ts.mean():.2f}")
print(f"Std: {ts.std():.2f}")

# ============================================================
# TRAIN/TEST SPLIT
# ============================================================
# Split chronologically: 80% train, 20% test
split_idx = int(len(ts) * 0.8)
train = ts[:split_idx]
test = ts[split_idx:]

print(f"\nTrain size: {len(train)}")
print(f"Test size: {len(test)}")
print(f"Train period: {train.index[0]} to {train.index[-1]}")
print(f"Test period: {test.index[0]} to {test.index[-1]}")

# ============================================================
# MODEL 1: ARIMA
# ============================================================
print("\n" + "="*50)
print("MODEL 1: ARIMA")
print("="*50)

# Train ARIMA model
try:
    arima_model = ARIMA(train, order=(1, 1, 1))
    arima_fitted = arima_model.fit()
    
    # Forecast on test data
    arima_forecast = arima_fitted.forecast(steps=len(test))
    
    # Calculate metrics
    arima_mae = mean_absolute_error(test, arima_forecast)
    arima_rmse = np.sqrt(mean_squared_error(test, arima_forecast))
    arima_mape = mean_absolute_percentage_error(test, arima_forecast) * 100
    
    print(f"MAE: {arima_mae:.2f}")
    print(f"RMSE: {arima_rmse:.2f}")
    print(f"MAPE: {arima_mape:.2f}%")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(train.index, train.values, label='Train', color='blue')
    plt.plot(test.index, test.values, label='Actual', color='green')
    plt.plot(test.index, arima_forecast, label='ARIMA Forecast', color='red', linestyle='--')
    plt.title('ARIMA Model Forecast')
    plt.xlabel('Date')
    plt.ylabel('Quantity Sold')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
except Exception as e:
    print(f"ARIMA Error: {e}")

# ============================================================
# MODEL 2: SEASONAL (Holt-Winters Exponential Smoothing)
# ============================================================
print("\n" + "="*50)
print("MODEL 2: SEASONAL (Holt-Winters)")
print("="*50)

try:
    # Try to detect seasonality
    # If you have weekly seasonality (7 days), use seasonal_periods=7
    # If monthly (30 days), use seasonal_periods=30
    
    # Auto-detect: try weekly first
    seasonal_model = ExponentialSmoothing(
        train, 
        seasonal_periods=7,  # Weekly seasonality
        trend='add',
        seasonal='add'
    )
    seasonal_fitted = seasonal_model.fit()
    
    # Forecast
    seasonal_forecast = seasonal_fitted.forecast(steps=len(test))
    
    # Calculate metrics
    seasonal_mae = mean_absolute_error(test, seasonal_forecast)
    seasonal_rmse = np.sqrt(mean_squared_error(test, seasonal_forecast))
    seasonal_mape = mean_absolute_percentage_error(test, seasonal_forecast) * 100
    
    print(f"MAE: {seasonal_mae:.2f}")
    print(f"RMSE: {seasonal_rmse:.2f}")
    print(f"MAPE: {seasonal_mape:.2f}%")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(train.index, train.values, label='Train', color='blue')
    plt.plot(test.index, test.values, label='Actual', color='green')
    plt.plot(test.index, seasonal_forecast, label='Seasonal Forecast', color='orange', linestyle='--')
    plt.title('Seasonal Model Forecast (Holt-Winters)')
    plt.xlabel('Date')
    plt.ylabel('Quantity Sold')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
except Exception as e:
    print(f"Seasonal Model Error: {e}")

# ============================================================
# MODEL 3: RANDOM FOREST
# ============================================================
print("\n" + "="*50)
print("MODEL 3: RANDOM FOREST")
print("="*50)

try:
    # Create features for Random Forest
    def create_features(df):
        df = df.copy()
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['lag_1'] = df['quantity_sold'].shift(1)
        df['lag_7'] = df['quantity_sold'].shift(7)
        df['lag_30'] = df['quantity_sold'].shift(30)
        df['rolling_mean_7'] = df['quantity_sold'].rolling(window=7).mean()
        df['rolling_mean_30'] = df['quantity_sold'].rolling(window=30).mean()
        return df
    
    # Prepare data
    ts_df = pd.DataFrame({'quantity_sold': ts})
    ts_df = create_features(ts_df)
    ts_df = ts_df.dropna()
    
    # Split again after feature engineering
    split_idx = int(len(ts_df) * 0.8)
    train_df = ts_df[:split_idx]
    test_df = ts_df[split_idx:]
    
    # Features
    feature_cols = ['day_of_week', 'day_of_month', 'month', 'year', 
                    'lag_1', 'lag_7', 'lag_30', 'rolling_mean_7', 'rolling_mean_30']
    
    X_train = train_df[feature_cols]
    y_train = train_df['quantity_sold']
    X_test = test_df[feature_cols]
    y_test = test_df['quantity_sold']
    
    # Train Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    # Forecast
    rf_forecast = rf_model.predict(X_test)
    
    # Calculate metrics
    rf_mae = mean_absolute_error(y_test, rf_forecast)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_forecast))
    rf_mape = mean_absolute_percentage_error(y_test, rf_forecast) * 100
    
    print(f"MAE: {rf_mae:.2f}")
    print(f"RMSE: {rf_rmse:.2f}")
    print(f"MAPE: {rf_mape:.2f}%")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(train_df.index, train_df['quantity_sold'].values, label='Train', color='blue')
    plt.plot(test_df.index, y_test.values, label='Actual', color='green')
    plt.plot(test_df.index, rf_forecast, label='Random Forest Forecast', color='purple', linestyle='--')
    plt.title('Random Forest Model Forecast')
    plt.xlabel('Date')
    plt.ylabel('Quantity Sold')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
except Exception as e:
    print(f"Random Forest Error: {e}")

# ============================================================
# COMPARISON SUMMARY
# ============================================================
print("\n" + "="*50)
print("MODEL COMPARISON SUMMARY")
print("="*50)

comparison = pd.DataFrame({
    'Model': ['ARIMA', 'Seasonal (Holt-Winters)', 'Random Forest'],
    'MAE': [arima_mae, seasonal_mae, rf_mae],
    'RMSE': [arima_rmse, seasonal_rmse, rf_rmse],
    'MAPE (%)': [arima_mape, seasonal_mape, rf_mape]
})

print(comparison.to_string(index=False))

# Plot comparison
plt.figure(figsize=(14, 8))
plt.plot(test.index, test.values, label='Actual', color='black', linewidth=2)
plt.plot(test.index, arima_forecast, label='ARIMA', color='red', linestyle='--')
plt.plot(test.index, seasonal_forecast, label='Seasonal', color='orange', linestyle='--')
plt.plot(test_df.index, rf_forecast, label='Random Forest', color='purple', linestyle='--')
plt.title('Model Comparison: All Forecasts vs Actual')
plt.xlabel('Date')
plt.ylabel('Quantity Sold')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## 🔍 Quick Data Check Queries

Before exporting, run these in pgAdmin4 to check your data:

```sql
-- Check total transactions
SELECT COUNT(*) as total_transactions,
       MIN(transaction_date) as earliest_date,
       MAX(transaction_date) as latest_date
FROM sales_transactions;

-- Check branches and products
SELECT id, name FROM branches;
SELECT id, name FROM products;

-- Check data per branch-product
SELECT 
    b.name as branch,
    p.name as product,
    COUNT(DISTINCT DATE(transaction_date)) as unique_days,
    SUM(quantity_sold) as total_quantity
FROM sales_transactions st
JOIN branches b ON st.branch_id = b.id
JOIN products p ON st.product_id = p.id
GROUP BY b.name, p.name
ORDER BY unique_days DESC;
```

## 💡 Tips

1. **Choose the right query:** Start with Option 2 (specific branch/product) for focused testing
2. **Check data quality:** Run the "CHECK YOUR DATA FIRST" queries before exporting
3. **Date format:** Make sure dates are in YYYY-MM-DD format
4. **Missing dates:** The Colab notebook will handle missing dates by filling with 0
5. **Outliers:** The ETL pipeline in Colab will remove outliers automatically

## 📦 Required Python Packages for Colab

The notebook will install these automatically, but you can also run:

```python
!pip install pandas numpy matplotlib statsmodels scikit-learn
```

## 🎯 Next Steps

1. Export your data using one of the SQL queries
2. Upload to Google Colab
3. Run the notebook to test all 3 models
4. Compare results and choose the best model for your use case

Good luck with your forecasting models! 🚀


