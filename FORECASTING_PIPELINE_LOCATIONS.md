# Forecasting Pipeline - Code Locations

This document shows exactly where each step of the forecasting pipeline is implemented in the codebase.

## Pipeline Overview

The forecasting pipeline follows this order:
1. **ETL** (Extract → Transform → Load)
2. **Train/Test Split**
3. **Modeling** (Train ARIMA, RF, or Seasonal)
4. **Evaluation** (Calculate MAE, MAPE, RMSE, Accuracy)
5. **Output** (Generate forecast with confidence intervals)

---

## Code Location: `backend/forecasting_service.py`

### Main Entry Point: `generate_arima_forecast()` method

**File:** `backend/forecasting_service.py`  
**Method:** `ForecastingService.generate_arima_forecast()`  
**Lines:** 245-520 (approximately)

---

## STEP 1: ETL PIPELINE (Extract → Transform → Load)

### Location: Lines 271-296 in `generate_arima_forecast()`

```python
# ============================================================
# STEP 1: ETL PIPELINE (Extract → Transform → Load)
# ============================================================
# EXTRACT: Load raw historical sales data
raw_df = self.etl.extract(historical_data)  # Line ~275

# TRANSFORM: Clean, aggregate, and prepare data for modeling
# - Converts transaction_date to datetime
# - Aggregates by day (sum quantity_sold per day)
# - Removes outliers (beyond 3 standard deviations)
# - Clips negative values to 0
# - Fills missing values
processed_data = self.etl.transform(raw_df)  # Line ~286

# LOAD: Final data preparation and validation
# - Ensures minimum data points (pads if needed)
final_data = self.etl.load(processed_data)  # Line ~296
```

### ETL Class Implementation:

**Class:** `ETLPipeline`  
**Location:** Lines 22-109 in `forecasting_service.py`

- **`extract()`** (Lines 31-40): Loads raw historical sales data into DataFrame
- **`transform()`** (Lines 42-92): 
  - Converts dates to datetime
  - Aggregates by day (resample to daily)
  - Removes outliers (3 standard deviations)
  - Clips negative values
  - Fills missing values
- **`load()`** (Lines 94-109): 
  - Validates minimum data points
  - Pads with mean if too short

---

## STEP 2: TRAIN/TEST SPLIT

### Location: Lines 298-302 in `generate_arima_forecast()`

```python
# ============================================================
# STEP 2: TRAIN/TEST SPLIT
# ============================================================
# Split data chronologically: 80% training (older), 20% testing (recent)
train_data, test_data = self.train_test_split(final_data, test_size=0.2)  # Line ~302
```

### Train/Test Split Implementation:

**Method:** `ForecastingService.train_test_split()`  
**Location:** Lines 120-136 in `forecasting_service.py`

- Splits data chronologically (time-series aware)
- 80% for training (older data)
- 20% for testing (recent data)
- Ensures minimum training data (7 days)

---

## STEP 3: MODELING - Train ARIMA Model

### Location: Lines 321-330 in `generate_arima_forecast()`

```python
# ============================================================
# STEP 3: MODELING - Train ARIMA Model
# ============================================================
# Train ARIMA model on training data
# Uses grid search to find best (p, d, q) parameters
model = self.train_arima_model(train_data)  # Line ~326
```

### ARIMA Training Implementation:

**Method:** `ForecastingService.train_arima_model()`  
**Location:** Lines 180-243 in `forecasting_service.py`

- Performs grid search for best ARIMA parameters (p, d, q)
- Tests combinations: (0,1,1), (1,1,1), (2,1,1), (0,1,2), (1,1,2)
- Selects model with lowest AIC (Akaike Information Criterion)
- Returns trained ARIMA model

---

## STEP 4: EVALUATION - Evaluate Model on Test Data

### Location: Lines 332-367 in `generate_arima_forecast()`

```python
# ============================================================
# STEP 4: EVALUATION - Evaluate model on test data
# ============================================================
# Generate predictions on test data and calculate metrics (MAE, MAPE, RMSE, Accuracy)
if len(test_data) > 0:
    # Generate predictions for test period
    test_forecast = model.forecast(steps=len(test_data))  # Line ~339
    
    # Evaluate model
    metrics = self.evaluate_model(test_data, test_forecast_series)  # Line ~333
    accuracy_score = metrics['accuracy']
```

### Evaluation Implementation:

**Method:** `ForecastingService.evaluate_model()`  
**Location:** Lines 138-177 in `forecasting_service.py`

- Calculates **MAE** (Mean Absolute Error)
- Calculates **MAPE** (Mean Absolute Percentage Error)
- Calculates **RMSE** (Root Mean Squared Error)
- Calculates **Accuracy Score** (1 - MAPE/100, clamped to 0-1)

---

## STEP 5: OUTPUT - Generate Forecast for Future Periods

### Location: Lines 369-520 in `generate_arima_forecast()`

```python
# ============================================================
# STEP 5: OUTPUT - Generate forecast for future periods
# ============================================================
# Generate predicted daily demand with confidence intervals (upper/lower)
forecast_result = model.forecast(steps=periods)  # Line ~384
conf_int = model.get_forecast(steps=periods).conf_int()  # Line ~385

# Returns:
# - forecast_values: Predicted daily demand
# - confidence_lower: Lower confidence interval
# - confidence_upper: Upper confidence interval
# - model_type: "ARIMA"
# - accuracy_score: Model accuracy
# - metrics: MAE, MAPE, RMSE
```

### Output Format:

The method returns a dictionary with:
- **`forecast_values`**: List of predicted daily demand (kg) for next N days
- **`confidence_lower`**: Lower bound of 95% confidence interval
- **`confidence_upper`**: Upper bound of 95% confidence interval
- **`model_type`**: "ARIMA"
- **`accuracy_score`**: Model accuracy (0-1)
- **`metrics`**: Dictionary with MAE, MAPE, RMSE, accuracy
- **`train_size`**: Number of days in training set
- **`test_size`**: Number of days in test set

---

## Similar Pipeline for Other Models

The same pipeline structure is used for:
- **Random Forest**: `generate_rf_forecast()` (Lines 536-650)
- **Seasonal Naive**: `generate_seasonal_forecast()` (Lines 652-780)

Both follow the same 5-step pipeline:
1. ETL Pipeline
2. Train/Test Split
3. Modeling (Train model)
4. Evaluation
5. Output

---

## Model Selection

**Method:** `ForecastingService.generate_forecast_with_model_selection()`  
**Location:** Lines 800-871 in `forecasting_service.py`

- If specific model requested: trains only that model
- If no model specified: trains all 3 models (ARIMA, RF, Seasonal)
- Evaluates all models
- Selects best model based on accuracy score
- Returns forecast from best model

---

## Key Files Summary

| Component | File | Lines |
|-----------|------|-------|
| ETL Pipeline Class | `forecasting_service.py` | 22-109 |
| Train/Test Split | `forecasting_service.py` | 120-136 |
| Model Evaluation | `forecasting_service.py` | 138-177 |
| ARIMA Training | `forecasting_service.py` | 180-243 |
| ARIMA Forecast (Full Pipeline) | `forecasting_service.py` | 245-520 |
| RF Forecast (Full Pipeline) | `forecasting_service.py` | 536-650 |
| Seasonal Forecast (Full Pipeline) | `forecasting_service.py` | 652-780 |
| Model Selection | `forecasting_service.py` | 800-871 |

---

## Notes

- All pipeline steps are clearly marked with comment blocks
- Each step is documented with what it does
- The pipeline ensures data quality at each step
- Fallbacks are provided if any step fails
- All forecasts ensure non-negative values
- Confidence intervals are validated and adjusted if needed






