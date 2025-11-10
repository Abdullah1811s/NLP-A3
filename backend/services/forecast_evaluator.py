"""
Service for evaluating forecasts against actual prices and calculating error metrics
"""
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from backend.models.forecast import Forecast
from backend.services.data_fetcher import fetch
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def get_forecast_with_errors(ticker: str, forecast_id: Optional[str] = None) -> Dict:
    """
    Get forecast data with actual prices and error overlays for candlestick visualization
    
    Returns forecast data with:
    - Predicted prices
    - Actual prices (where available)
    - Error metrics (difference between predicted and actual)
    - Error percentages
    """
    import traceback
    try:
        # Get latest forecast for ticker
        if forecast_id:
            forecast = Forecast.objects(id=forecast_id).first()
        else:
            forecast = Forecast.objects(ticker=ticker).order_by("-created_at").first()
        
        if not forecast:
            return {
                "success": False,
                "message": f"No forecast found for {ticker}"
            }
        
        forecast_data = forecast.forecast_data
        if not forecast_data:
            return {
                "success": False,
                "message": "Forecast data is empty"
            }
        
        # Convert forecast data to DataFrame
        # Forecast data is a list of dicts with 'Date' as a key
        forecast_df = pd.DataFrame(forecast_data)
        
        # Ensure Date column exists and is datetime
        if 'Date' not in forecast_df.columns:
            # Try to extract from index if it was set as index
            forecast_df.reset_index(inplace=True)
            if 'index' in forecast_df.columns:
                forecast_df.rename(columns={'index': 'Date'}, inplace=True)
            else:
                # Create date range if no date info
                return {
                    "success": False,
                    "message": "Forecast data missing Date information"
                }
        
        # Convert Date to datetime - normalize to timezone-naive datetime64[ns]
        # This ensures compatibility when merging with actual data
        try:
            # Convert to datetime - parse as UTC if timezone info present
            forecast_df['Date'] = pd.to_datetime(forecast_df['Date'], errors='coerce', utc=True)
            
            # Check if we have timezone-aware datetimes and convert to naive
            # Use a try-except since .dt.tz might not work on all Series
            try:
                # Check if any dates are timezone-aware by sampling
                sample_dates = forecast_df['Date'].dropna()
                if len(sample_dates) > 0:
                    # Check if the first valid date is timezone-aware
                    if hasattr(sample_dates.iloc[0], 'tz') and sample_dates.iloc[0].tz is not None:
                        # Convert timezone-aware to naive (UTC -> naive)
                        forecast_df['Date'] = forecast_df['Date'].dt.tz_convert('UTC').dt.tz_localize(None)
                    elif 'UTC' in str(forecast_df['Date'].dtype) or 'datetime64[ns, UTC]' in str(forecast_df['Date'].dtype):
                        # Dtype indicates UTC, convert through string to remove timezone from dtype
                        forecast_df['Date'] = pd.to_datetime(forecast_df['Date'].astype(str), errors='coerce', utc=False)
            except (AttributeError, TypeError, IndexError):
                # If timezone operations fail, try converting through string
                forecast_df['Date'] = pd.to_datetime(forecast_df['Date'].astype(str), errors='coerce', utc=False)
            
            # Normalize to date-only (remove time component) for consistent merging
            forecast_df['Date'] = forecast_df['Date'].dt.normalize()
            
            # Ensure it's datetime64[ns] (timezone-naive)
            forecast_df['Date'] = forecast_df['Date'].astype('datetime64[ns]')
        except Exception as e:
            # Final fallback: convert through string representation
            try:
                # Convert original column to string, then to datetime without UTC
                forecast_df['Date'] = pd.to_datetime(forecast_df['Date'].astype(str), errors='coerce', utc=False)
                forecast_df['Date'] = forecast_df['Date'].dt.normalize().astype('datetime64[ns]')
            except Exception as e2:
                return {
                    "success": False,
                    "message": f"Error converting forecast dates: {str(e2)}"
                }
        
        # Remove rows with invalid dates
        forecast_df = forecast_df[forecast_df['Date'].notna()]
        
        if len(forecast_df) == 0:
            return {
                "success": False,
                "message": "No valid dates in forecast data"
            }
        
        # Get actual prices for the forecast period
        # Fetch historical data covering the forecast period
        start_date = forecast_df['Date'].min()
        end_date = forecast_df['Date'].max()
        days_diff = (end_date - start_date).days + 10  # Add buffer
        
        result = fetch(ticker=ticker, period=f"{max(days_diff, 60)}d")  # Minimum 60 days
        if not result or not result.get("success"):
            return {
                "success": False,
                "message": "Could not fetch actual price data"
            }
        
        hist_data = result.get("hist_df", [])
        if not hist_data:
            return {
                "success": False,
                "message": "No historical data available"
            }
        
        actual_df = pd.DataFrame(hist_data)
        if 'Date' in actual_df.columns:
            # Convert Date to datetime - normalize to timezone-naive datetime64[ns]
            # Hist data comes as ISO strings from data_fetcher, may have timezone info
            try:
                # Convert to datetime - parse as UTC if timezone info present
                actual_df['Date'] = pd.to_datetime(actual_df['Date'], errors='coerce', utc=True)
                
                # Check if we have timezone-aware datetimes and convert to naive
                try:
                    # Check if any dates are timezone-aware by sampling
                    sample_dates = actual_df['Date'].dropna()
                    if len(sample_dates) > 0:
                        # Check if the first valid date is timezone-aware
                        if hasattr(sample_dates.iloc[0], 'tz') and sample_dates.iloc[0].tz is not None:
                            # Convert timezone-aware to naive (UTC -> naive)
                            actual_df['Date'] = actual_df['Date'].dt.tz_convert('UTC').dt.tz_localize(None)
                        elif 'UTC' in str(actual_df['Date'].dtype) or 'datetime64[ns, UTC]' in str(actual_df['Date'].dtype):
                            # Dtype indicates UTC, convert through string to remove timezone from dtype
                            actual_df['Date'] = pd.to_datetime(actual_df['Date'].astype(str), errors='coerce', utc=False)
                except (AttributeError, TypeError, IndexError):
                    # If timezone operations fail, try converting through string
                    actual_df['Date'] = pd.to_datetime(actual_df['Date'].astype(str), errors='coerce', utc=False)
                
                # Normalize to date-only (remove time component) for consistent merging
                actual_df['Date'] = actual_df['Date'].dt.normalize()
                
                # Ensure it's datetime64[ns] (timezone-naive)
                actual_df['Date'] = actual_df['Date'].astype('datetime64[ns]')
            except Exception as e:
                # Final fallback: convert through string representation
                try:
                    # Convert original column to string, then to datetime without UTC
                    actual_df['Date'] = pd.to_datetime(actual_df['Date'].astype(str), errors='coerce', utc=False)
                    actual_df['Date'] = actual_df['Date'].dt.normalize().astype('datetime64[ns]')
                except Exception as e2:
                    return {
                        "success": False,
                        "message": f"Error converting actual dates: {str(e2)}"
                    }
        else:
            return {
                "success": False,
                "message": "Historical data missing Date column"
            }
        
        # Both dataframes now have datetime64[ns] Date columns (timezone-naive)
        # They can be safely merged on the Date column
        
        # Rename forecast columns to have _predicted suffix for clarity
        forecast_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in forecast_cols:
            if col in forecast_df.columns:
                forecast_df.rename(columns={col: f"{col}_predicted"}, inplace=True)
        
        # Merge forecast with actual data
        merged_df = pd.merge(
            forecast_df,
            actual_df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']],
            on='Date',
            how='left',
            suffixes=('', '_actual')
        )
        
        # Rename actual columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in merged_df.columns and f"{col}_predicted" in merged_df.columns:
                merged_df.rename(columns={col: f"{col}_actual"}, inplace=True)
        
        # Calculate errors for Close price (most important metric)
        if 'Close_actual' in merged_df.columns and 'Close_predicted' in merged_df.columns:
            merged_df['error_close'] = merged_df['Close_actual'] - merged_df['Close_predicted']
            merged_df['error_close_percent'] = (
                (merged_df['error_close'] / merged_df['Close_predicted']) * 100
            ).fillna(0)
        else:
            merged_df['error_close'] = None
            merged_df['error_close_percent'] = None
        
        # Calculate errors for other OHLC values (if available)
        if 'Open_actual' in merged_df.columns and 'Open_predicted' in merged_df.columns:
            merged_df['error_open'] = merged_df['Open_actual'] - merged_df['Open_predicted']
        else:
            merged_df['error_open'] = None
            
        if 'High_actual' in merged_df.columns and 'High_predicted' in merged_df.columns:
            merged_df['error_high'] = merged_df['High_actual'] - merged_df['High_predicted']
        else:
            merged_df['error_high'] = None
            
        if 'Low_actual' in merged_df.columns and 'Low_predicted' in merged_df.columns:
            merged_df['error_low'] = merged_df['Low_actual'] - merged_df['Low_predicted']
        else:
            merged_df['error_low'] = None
        
        # Prepare data for frontend (candlestick format)
        candlestick_data = []
        for _, row in merged_df.iterrows():
            # Use actual if available, otherwise use predicted
            open_price = row.get('Open_actual') if 'Open_actual' in row and pd.notna(row.get('Open_actual')) else (row.get('Open_predicted', 0) if 'Open_predicted' in row else 0)
            high_price = row.get('High_actual') if 'High_actual' in row and pd.notna(row.get('High_actual')) else (row.get('High_predicted', 0) if 'High_predicted' in row else 0)
            low_price = row.get('Low_actual') if 'Low_actual' in row and pd.notna(row.get('Low_actual')) else (row.get('Low_predicted', 0) if 'Low_predicted' in row else 0)
            close_price = row.get('Close_actual') if 'Close_actual' in row and pd.notna(row.get('Close_actual')) else (row.get('Close_predicted', 0) if 'Close_predicted' in row else 0)
            predicted_close = row.get('Close_predicted', 0) if 'Close_predicted' in row else 0
            
            candlestick_data.append({
                "date": row['Date'].isoformat() if pd.notna(row['Date']) else None,
                "time": row['Date'].strftime("%H:%M") if pd.notna(row['Date']) else None,
                "open": float(open_price) if pd.notna(open_price) else 0,
                "high": float(high_price) if pd.notna(high_price) else 0,
                "low": float(low_price) if pd.notna(low_price) else 0,
                "close": float(close_price) if pd.notna(close_price) else 0,
                "predicted": float(predicted_close) if pd.notna(predicted_close) else 0,
                "error": float(row.get('error_close', 0)) if 'error_close' in row and pd.notna(row.get('error_close')) else None,
                "error_percent": float(row.get('error_close_percent', 0)) if 'error_close_percent' in row and pd.notna(row.get('error_close_percent')) else None,
                "has_actual": 'Close_actual' in row and pd.notna(row.get('Close_actual'))
            })
        
        # Calculate aggregate error metrics (only for dates with actual data)
        actual_mask = pd.Series([False] * len(merged_df))  # Initialize with False
        mae = None
        rmse = None
        mape = None
        
        if 'Close_actual' in merged_df.columns and 'Close_predicted' in merged_df.columns:
            actual_mask = merged_df['Close_actual'].notna()
            if actual_mask.sum() > 0:
                actual_closes = merged_df.loc[actual_mask, 'Close_actual']
                predicted_closes = merged_df.loc[actual_mask, 'Close_predicted']
                
                mae = float(mean_absolute_error(actual_closes, predicted_closes))
                rmse = float(np.sqrt(mean_squared_error(actual_closes, predicted_closes)))
                mape = float(np.mean(np.abs((actual_closes - predicted_closes) / actual_closes)) * 100)
        
        return {
            "success": True,
            "ticker": ticker,
            "forecast_id": str(forecast.id),
            "forecast_date": forecast.created_at.isoformat() if forecast.created_at else None,
            "candlestick_data": candlestick_data,
            "error_metrics": {
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "evaluated_points": int(actual_mask.sum()) if actual_mask.sum() > 0 else 0,
                "total_forecast_points": len(forecast_data)
            },
            "model_info": forecast.model_info
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_forecast_with_errors: {str(e)}")
        print(f"Traceback: {error_trace}")
        return {
            "success": False,
            "message": f"Error evaluating forecast: {str(e)}",
            "error_details": str(e)
        }


def evaluate_forecast_against_actual(ticker: str, forecast_id: Optional[str] = None) -> Dict:
    """
    Evaluate a forecast by comparing predicted prices with actual prices
    
    This function is called when actual price data becomes available for forecasted dates
    """
    try:
        result = get_forecast_with_errors(ticker, forecast_id)
        
        if not result.get("success"):
            return result
        
        # Update forecast with evaluation results
        if forecast_id:
            forecast = Forecast.objects(id=forecast_id).first()
        else:
            forecast = Forecast.objects(ticker=ticker).order_by("-created_at").first()
        
        if forecast:
            # Store evaluation results in model_info
            if "evaluation" not in forecast.model_info:
                forecast.model_info["evaluation"] = {}
            
            forecast.model_info["evaluation"].update({
                "last_evaluated": datetime.utcnow().isoformat(),
                "error_metrics": result.get("error_metrics", {}),
                "evaluation_status": "completed"
            })
            
            forecast.save()
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in forecast evaluation: {str(e)}"
        }

