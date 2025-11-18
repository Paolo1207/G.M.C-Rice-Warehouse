# Forecast Model Selection Fix

## Problem Fixed
When a user selected a specific model (ARIMA, RF, or Seasonal) from the dropdown, the system was:
1. Training ALL models first
2. Then trying to find the requested model
3. If the requested model wasn't found or failed, it would fall back to the "best" model (which could be Random Forest even if ARIMA was selected)

## Solution
Now when a user selects a specific model:
1. **ONLY that model is trained** (faster, more efficient)
2. The selected model is used directly
3. If the selected model fails, it falls back to default but preserves the model type name

## Code Changes

### File: `backend/forecasting_service.py`

**Method: `generate_forecast_with_model_selection`**
- Now checks for `requested_model` FIRST
- If a model is requested, it ONLY trains that specific model
- Model matching is case-insensitive (handles "ARIMA", "arima", "ARIMA", etc.)

**Method: `_generate_default_forecast`**
- Now accepts `model_type` parameter
- Preserves the requested model type even when using default forecast

## Model Type Mapping

Frontend sends:
- `"ARIMA"` → Backend uses ARIMA model
- `"RF"` → Backend uses Random Forest model  
- `"Seasonal"` → Backend uses Seasonal Naive model

Backend returns:
- `"ARIMA"` for ARIMA forecasts
- `"RF"` for Random Forest forecasts
- `"Seasonal"` for Seasonal Naive forecasts

## Data Source Information

The **Data Source Information** box is displayed in:
- **File:** `backend/Admin_GMC/templates/admin/admin_forecast.html`
- **Function:** `displayForecastResults()` (line ~432)
- **Data comes from:** `forecast.data_source` object

The data source information is created in:
- **File:** `backend/Admin_GMC/__init__.py`
- **Function:** `api_generate_forecast()` (line ~1059)
- **Code:**
  ```python
  forecast_result['data_source'] = {
      'type': data_source_type,  # 'real_sales_data' or 'estimated_from_inventory'
      'total_transactions': total_transactions,
      'unique_days': unique_days,
      'date_range_days': 912,  # 2.5 years
      'earliest_date': earliest_date.strftime('%Y-%m-%d') if earliest_date else None,
      'latest_date': latest_date.strftime('%Y-%m-%d') if latest_date else None,
      'date_threshold': date_threshold.strftime('%Y-%m-%d'),
      'train_size': forecast_result.get('train_size', 0),
      'test_size': forecast_result.get('test_size', 0)
  }
  ```

## How It Works Now

1. User selects model type from dropdown (ARIMA, RF, or Seasonal)
2. Frontend sends `model_type` in the request
3. Backend receives `model_type` and passes it as `requested_model`
4. Backend checks if `requested_model` is specified
5. If yes, **ONLY that model is trained and used**
6. If no, all models are trained and best one is selected
7. The correct model type is returned and displayed

## Testing

To verify the fix works:
1. Select "ARIMA" from dropdown → Should show "ARIMA" in results
2. Select "RF" from dropdown → Should show "RF" in results
3. Select "Seasonal" from dropdown → Should show "Seasonal" in results

The model type displayed should match what you selected!

