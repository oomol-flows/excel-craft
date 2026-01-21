#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    time_column: str
    operation: typing.Literal["resample", "rolling", "shift", "diff", "parseDate", "extractFeatures"]
    params: dict | None
class Outputs(typing.TypedDict):
    data: typing.NotRequired[list[dict]]
    operation: typing.NotRequired[str]
    new_columns: typing.NotRequired[list[str]]
    time_range: typing.NotRequired[dict]
#endregion

from oocana import Context
import pandas as pd
from datetime import datetime
import re


async def main(params: Inputs, context: Context) -> Outputs:
    """Time series data processing with various operations."""

    data = params["data"]
    time_column = params["time_column"]
    operation = params["operation"]
    op_params = params.get("params") or {}

    if not data:
        raise ValueError("Input data cannot be empty")

    if time_column not in data[0]:
        raise ValueError(f"Time column '{time_column}' not found in data")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Parse time column
    try:
        df[time_column] = pd.to_datetime(df[time_column])
    except Exception as e:
        raise ValueError(f"Failed to parse time column '{time_column}': {str(e)}")

    # Sort by time
    df = df.sort_values(time_column)

    new_columns = []

    # Perform operation
    if operation == "resample":
        result_df = _resample(df, time_column, op_params)

    elif operation == "rolling":
        result_df, new_cols = _rolling(df, time_column, op_params)
        new_columns = new_cols

    elif operation == "shift":
        result_df, new_cols = _shift(df, time_column, op_params)
        new_columns = new_cols

    elif operation == "diff":
        result_df, new_cols = _diff(df, time_column, op_params)
        new_columns = new_cols

    elif operation == "parseDate":
        result_df = _parse_date(df, time_column, op_params)

    elif operation == "extractFeatures":
        result_df, new_cols = _extract_features(df, time_column, op_params)
        new_columns = new_cols

    else:
        raise ValueError(f"Unknown operation: {operation}")

    # Get time range
    time_range = {
        "start": str(result_df[time_column].min()),
        "end": str(result_df[time_column].max()),
        "periods": len(result_df)
    }

    # Convert datetime columns to strings for JSON serialization
    for col in result_df.columns:
        if pd.api.types.is_datetime64_any_dtype(result_df[col]):
            result_df[col] = result_df[col].astype(str)

    # Convert back to records
    result_data = result_df.to_dict('records')

    return {
        "data": result_data,
        "operation": operation,
        "new_columns": new_columns,
        "time_range": time_range
    }


def _resample(df: pd.DataFrame, time_column: str, params: dict) -> pd.DataFrame:
    """Resample time series data."""
    freq = params.get("freq", "1D")
    agg_func = params.get("aggFunc", "mean")

    # Set time column as index
    df_indexed = df.set_index(time_column)

    # Resample
    if agg_func == "mean":
        resampled = df_indexed.resample(freq).mean()
    elif agg_func == "sum":
        resampled = df_indexed.resample(freq).sum()
    elif agg_func == "count":
        resampled = df_indexed.resample(freq).count()
    elif agg_func == "min":
        resampled = df_indexed.resample(freq).min()
    elif agg_func == "max":
        resampled = df_indexed.resample(freq).max()
    elif agg_func == "first":
        resampled = df_indexed.resample(freq).first()
    elif agg_func == "last":
        resampled = df_indexed.resample(freq).last()
    else:
        resampled = df_indexed.resample(freq).mean()

    # Reset index to convert time back to column
    result = resampled.reset_index()

    return result


def _rolling(df: pd.DataFrame, time_column: str, params: dict) -> tuple[pd.DataFrame, list[str]]:
    """Apply rolling window operations."""
    window = params.get("window", 3)
    min_periods = params.get("minPeriods", 1)
    center = params.get("center", False)
    agg_func = params.get("aggFunc", "mean")

    result_df = df.copy()
    new_columns = []

    # Apply rolling to numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        new_col_name = f"{col}_rolling_{agg_func}"

        if agg_func == "mean":
            result_df[new_col_name] = df[col].rolling(window=window, min_periods=min_periods, center=center).mean()
        elif agg_func == "sum":
            result_df[new_col_name] = df[col].rolling(window=window, min_periods=min_periods, center=center).sum()
        elif agg_func == "std":
            result_df[new_col_name] = df[col].rolling(window=window, min_periods=min_periods, center=center).std()
        elif agg_func == "min":
            result_df[new_col_name] = df[col].rolling(window=window, min_periods=min_periods, center=center).min()
        elif agg_func == "max":
            result_df[new_col_name] = df[col].rolling(window=window, min_periods=min_periods, center=center).max()

        new_columns.append(new_col_name)

    return result_df, new_columns


def _shift(df: pd.DataFrame, time_column: str, params: dict) -> tuple[pd.DataFrame, list[str]]:
    """Shift data by specified periods."""
    periods = params.get("periods", 1)

    result_df = df.copy()
    new_columns = []

    # Apply shift to numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        new_col_name = f"{col}_shift_{periods}"
        result_df[new_col_name] = df[col].shift(periods)
        new_columns.append(new_col_name)

    return result_df, new_columns


def _diff(df: pd.DataFrame, time_column: str, params: dict) -> tuple[pd.DataFrame, list[str]]:
    """Calculate difference between consecutive values."""
    periods = params.get("periods", 1)

    result_df = df.copy()
    new_columns = []

    # Apply diff to numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        new_col_name = f"{col}_diff"
        result_df[new_col_name] = df[col].diff(periods)
        new_columns.append(new_col_name)

    return result_df, new_columns


def _parse_date(df: pd.DataFrame, time_column: str, params: dict) -> pd.DataFrame:
    """Parse date column with specified format."""
    date_format = params.get("format", None)

    result_df = df.copy()

    if date_format:
        result_df[time_column] = pd.to_datetime(df[time_column], format=date_format)
    else:
        result_df[time_column] = pd.to_datetime(df[time_column])

    return result_df


def _extract_features(df: pd.DataFrame, time_column: str, params: dict) -> tuple[pd.DataFrame, list[str]]:
    """Extract time-based features from date column."""
    features = params.get("features", ["year", "month", "day"])

    result_df = df.copy()
    new_columns = []

    time_series = pd.to_datetime(df[time_column])

    feature_map = {
        "year": lambda dt: dt.year,
        "month": lambda dt: dt.month,
        "day": lambda dt: dt.day,
        "hour": lambda dt: dt.hour,
        "minute": lambda dt: dt.minute,
        "second": lambda dt: dt.second,
        "weekday": lambda dt: dt.dayofweek,
        "quarter": lambda dt: dt.quarter,
        "week": lambda dt: dt.isocalendar().week,
        "dayofyear": lambda dt: dt.dayofyear,
        "is_weekend": lambda dt: dt.dayofweek >= 5
    }

    for feature in features:
        if feature in feature_map:
            col_name = f"{time_column}_{feature}"
            result_df[col_name] = time_series.apply(feature_map[feature])
            new_columns.append(col_name)

    return result_df, new_columns
