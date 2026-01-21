#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    inspect_level: typing.Literal["basic", "detailed", "quality"] | None
class Outputs(typing.TypedDict):
    summary: typing.NotRequired[dict]
    columns: typing.NotRequired[list[dict]]
    quality: typing.NotRequired[dict]
    preview: typing.NotRequired[list[dict]]
#endregion

from oocana import Context
import pandas as pd
import sys


async def main(params: Inputs, context: Context) -> Outputs:
    """Inspect table structure and data quality."""

    data = params["data"]
    if not data:
        raise ValueError("Input data is empty")

    inspect_level = params.get("inspect_level") or "basic"

    # Convert to DataFrame for analysis
    df = pd.DataFrame(data)

    # Calculate memory usage
    memory_bytes = df.memory_usage(deep=True).sum()
    if memory_bytes < 1024:
        memory_str = f"{memory_bytes} B"
    elif memory_bytes < 1024 * 1024:
        memory_str = f"{memory_bytes / 1024:.1f} KB"
    else:
        memory_str = f"{memory_bytes / (1024 * 1024):.1f} MB"

    # Summary statistics
    summary = {
        "rowCount": len(df),
        "columnCount": len(df.columns),
        "memoryUsage": memory_str
    }

    # Column-level statistics
    columns_info = []
    for col in df.columns:
        col_data = df[col]

        # Determine data type
        dtype_str = str(col_data.dtype)
        if pd.api.types.is_numeric_dtype(col_data):
            data_type = "number"
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            data_type = "date"
        elif pd.api.types.is_bool_dtype(col_data):
            data_type = "boolean"
        elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
            data_type = "string"
        else:
            data_type = "mixed"

        # Basic stats
        null_count = int(col_data.isna().sum())
        unique_count = int(col_data.nunique())
        null_percent = (null_count / len(df) * 100) if len(df) > 0 else 0

        # Sample values
        sample_values = col_data.dropna().head(5).tolist()

        col_info: dict[str, typing.Any] = {
            "name": col,
            "type": data_type,
            "nullCount": null_count,
            "uniqueCount": unique_count,
            "nullPercent": round(null_percent, 2),
            "sampleValues": sample_values
        }

        # Detailed statistics for numeric columns
        if inspect_level in ["detailed", "quality"] and data_type == "number":
            col_info["stats"] = {
                "min": float(col_data.min()) if not col_data.empty else None,
                "max": float(col_data.max()) if not col_data.empty else None,
                "mean": float(col_data.mean()) if not col_data.empty else None,
                "median": float(col_data.median()) if not col_data.empty else None,
                "std": float(col_data.std()) if not col_data.empty else None
            }

        columns_info.append(col_info)

    # Quality assessment
    quality: dict[str, typing.Any] = {}
    if inspect_level == "quality":
        total_cells = len(df) * len(df.columns)
        non_null_cells = df.count().sum()
        completeness = (non_null_cells / total_cells * 100) if total_cells > 0 else 100

        # Check for duplicate rows
        duplicate_rows = int(df.duplicated().sum())

        # Identify issues
        issues = []
        if completeness < 90:
            issues.append(f"Low completeness: {completeness:.1f}%")
        if duplicate_rows > 0:
            issues.append(f"{duplicate_rows} duplicate rows found")
        for col_info in columns_info:
            if col_info["nullPercent"] > 50:
                issues.append(f"Column '{col_info['name']}' has {col_info['nullPercent']:.1f}% missing values")

        quality = {
            "completeness": round(completeness, 2),
            "duplicateRows": duplicate_rows,
            "issues": issues
        }

    # Preview (first 10 rows)
    preview = df.head(10).to_dict('records')

    return {
        "summary": summary,
        "columns": columns_info,
        "quality": quality,
        "preview": preview
    }
