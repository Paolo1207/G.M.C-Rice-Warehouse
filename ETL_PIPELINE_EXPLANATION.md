# ETL Pipeline Explanation - What's Shown vs What's Internal

## 📊 What You See on the Forecast Page

### **Data Source Information Box** (Yellow/Orange/Blue Box)
This shows the **OUTPUT** of the **EXTRACT** step:
- **Total Transactions**: Raw count of sales records extracted from database
- **Unique Days with Sales**: Number of distinct days with sales
- **Historical Period**: Date range of the extracted data
- **Earliest/Latest Data**: Date boundaries
- **Data Type**: Whether it's "real_sales_data" or "estimated_from_inventory"

**This is the RESULT of the ETL Extract step** - it shows what data was pulled from the database.

---

## 🔄 What Happens Internally (Not Shown on Page)

### **1. EXTRACT** (ETL Step 1)
- Queries database for last 2-3 years of sales transactions
- Filters by branch_id and product_id
- Excludes future dates
- **Result**: Raw transaction list → Shown in "Data Source Information"

### **2. TRANSFORM** (ETL Step 2) - **NOT SHOWN**
- Converts transaction dates to datetime
- Aggregates multiple transactions per day into daily totals
- Removes outliers (values beyond 3 standard deviations)
- Fills missing days with 0 or forward/backward fill
- Ensures no negative values
- **Result**: Clean daily time series → **This is hidden from the page**

### **3. LOAD** (ETL Step 3) - **NOT SHOWN**
- Validates minimum data points (at least 7 days)
- Pads data if too short
- Final data preparation
- **Result**: Ready-to-use time series → **This is hidden from the page**

### **4. TRAIN/TEST SPLIT (80/20)** - **NOT SHOWN**
- Splits data: 80% for training, 20% for testing
- Time-series aware: earlier data = training, later data = testing
- **Result**: Two datasets → **This is hidden from the page**
- **Note**: The "Training Data" and "Test Data" shown in Data Source Information are calculated but the actual split happens internally

### **5. MODEL TRAINING** - **NOT SHOWN**
- Trains ARIMA/Random Forest/Seasonal model on training data
- Optimizes parameters
- **Result**: Trained model → **This is hidden from the page**

### **6. MODEL EVALUATION** - **SHOWN AT BOTTOM**
- Tests model on test data (20%)
- Calculates MAE, MAPE, RMSE, Accuracy
- **Result**: Evaluation metrics → **Shown in "Forecast Metrics" section**

### **7. FORECAST GENERATION** - **SHOWN**
- Uses trained model to predict future periods
- **Result**: Forecast values → **Shown in forecast chart/table**

---

## 📋 Summary

| Step | What It Does | Shown on Page? |
|------|--------------|----------------|
| **EXTRACT** | Pulls raw sales data from database | ✅ Yes - "Data Source Information" |
| **TRANSFORM** | Cleans, aggregates, removes outliers | ❌ No - Internal only |
| **LOAD** | Validates and prepares data | ❌ No - Internal only |
| **TRAIN/TEST SPLIT** | Splits 80/20 for training/testing | ⚠️ Partially - Shows counts but not the split itself |
| **TRAINING** | Trains the model | ❌ No - Internal only |
| **EVALUATION** | Tests model performance | ✅ Yes - "Forecast Metrics" (MAE, MAPE, etc.) |
| **FORECAST** | Generates future predictions | ✅ Yes - Forecast chart/table |

---

## 🎯 Why Some Steps Are Hidden

- **Transform/Load**: Too technical for end users
- **Train/Test Split**: Internal process, only results matter
- **Training**: Happens automatically, users don't need to see it

**What users need to see:**
- ✅ What data was used (Data Source Information)
- ✅ How well the model performed (Evaluation Metrics)
- ✅ What the forecast predicts (Forecast Results)

