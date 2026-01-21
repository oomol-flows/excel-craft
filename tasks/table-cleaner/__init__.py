#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    operations: list[dict]
class Outputs(typing.TypedDict):
    data: typing.NotRequired[list[dict]]
    report: typing.NotRequired[list[dict]]
#endregion

from oocana import Context
import pandas as pd
import re


async def main(params: Inputs, context: Context) -> Outputs:
    """Clean table data with various operations."""

    data = params["data"]
    if not data:
        return {
            "data": [],
            "report": []
        }

    operations = params["operations"]
    if not operations:
        raise ValueError("No operations specified")

    # Convert to DataFrame
    df = pd.DataFrame(data)
    original_count = len(df)

    report: list[Report] = []

    for op in operations:
        op_type = op["type"]
        columns = op.get("columns") or df.columns.tolist()
        op_params = op.get("params") or {}

        # Validate columns exist
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in data")

        affected_count = 0

        if op_type == "dropNull":
            # Drop rows with null values in specified columns
            before = len(df)
            df = df.dropna(subset=columns)
            affected_count = before - len(df)
            report.append({
                "operation": "dropNull",
                "affected": affected_count,
                "details": f"Removed {affected_count} rows with null values in columns: {', '.join(columns)}"
            })

        elif op_type == "fillNull":
            # Fill null values
            fill_value = op_params.get("fillValue")
            method = op_params.get("method")

            for col in columns:
                null_count = int(df[col].isna().sum())

                if method == "mean":
                    fill_val = df[col].mean()
                    df[col] = df[col].fillna(fill_val)
                    report.append({
                        "operation": "fillNull",
                        "affected": null_count,
                        "details": f"Filled {null_count} null values in '{col}' with mean: {fill_val:.2f}"
                    })
                elif method == "median":
                    fill_val = df[col].median()
                    df[col] = df[col].fillna(fill_val)
                    report.append({
                        "operation": "fillNull",
                        "affected": null_count,
                        "details": f"Filled {null_count} null values in '{col}' with median: {fill_val:.2f}"
                    })
                elif method == "mode":
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        fill_val = mode_val[0]
                        df[col] = df[col].fillna(fill_val)
                        report.append({
                            "operation": "fillNull",
                            "affected": null_count,
                            "details": f"Filled {null_count} null values in '{col}' with mode: {fill_val}"
                        })
                elif method == "forward":
                    df[col] = df[col].fillna(method='ffill')
                    report.append({
                        "operation": "fillNull",
                        "affected": null_count,
                        "details": f"Forward filled {null_count} null values in '{col}'"
                    })
                elif method == "backward":
                    df[col] = df[col].fillna(method='bfill')
                    report.append({
                        "operation": "fillNull",
                        "affected": null_count,
                        "details": f"Backward filled {null_count} null values in '{col}'"
                    })
                elif fill_value is not None:
                    df[col] = df[col].fillna(fill_value)
                    report.append({
                        "operation": "fillNull",
                        "affected": null_count,
                        "details": f"Filled {null_count} null values in '{col}' with: {fill_value}"
                    })
                else:
                    raise ValueError("Must specify either 'fillValue' or 'method' for fillNull operation")

        elif op_type == "dropDuplicates":
            # Drop duplicate rows
            before = len(df)
            if columns:
                df = df.drop_duplicates(subset=columns)
            else:
                df = df.drop_duplicates()
            affected_count = before - len(df)
            report.append({
                "operation": "dropDuplicates",
                "affected": affected_count,
                "details": f"Removed {affected_count} duplicate rows"
            })

        elif op_type == "convertType":
            # Convert column types
            target_type = op_params.get("targetType")
            if not target_type:
                raise ValueError("'targetType' parameter required for convertType operation")

            date_format = op_params.get("dateFormat")

            for col in columns:
                affected_count = len(df)
                try:
                    if target_type == "number":
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif target_type == "string":
                        df[col] = df[col].astype(str)
                    elif target_type == "date":
                        if date_format:
                            df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
                        else:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                    elif target_type == "boolean":
                        df[col] = df[col].astype(bool)
                    else:
                        raise ValueError(f"Unsupported target type: {target_type}")

                    report.append({
                        "operation": "convertType",
                        "affected": affected_count,
                        "details": f"Converted column '{col}' to type '{target_type}'"
                    })
                except Exception as e:
                    raise ValueError(f"Failed to convert column '{col}' to '{target_type}': {str(e)}")

        elif op_type == "trim":
            # Trim whitespace from string columns
            for col in columns:
                affected_count = len(df)
                df[col] = df[col].astype(str).str.strip()
                report.append({
                    "operation": "trim",
                    "affected": affected_count,
                    "details": f"Trimmed whitespace from column '{col}'"
                })

        elif op_type == "replace":
            # Replace values
            replace_map = op_params.get("replaceMap")
            pattern = op_params.get("pattern")
            replacement = op_params.get("replacement")

            for col in columns:
                affected_count = len(df)

                if replace_map:
                    df[col] = df[col].replace(replace_map)
                    report.append({
                        "operation": "replace",
                        "affected": affected_count,
                        "details": f"Replaced values in column '{col}' using mapping"
                    })
                elif pattern and replacement is not None:
                    df[col] = df[col].astype(str).str.replace(pattern, replacement, regex=True)
                    report.append({
                        "operation": "replace",
                        "affected": affected_count,
                        "details": f"Replaced pattern '{pattern}' with '{replacement}' in column '{col}'"
                    })
                else:
                    raise ValueError("Must specify either 'replaceMap' or both 'pattern' and 'replacement'")

        elif op_type == "normalize":
            # Normalize numeric columns
            method = op_params.get("method") or "minmax"

            for col in columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise ValueError(f"Column '{col}' is not numeric, cannot normalize")

                affected_count = len(df)

                if method == "minmax":
                    min_val = df[col].min()
                    max_val = df[col].max()
                    if max_val > min_val:
                        df[col] = (df[col] - min_val) / (max_val - min_val)
                    report.append({
                        "operation": "normalize",
                        "affected": affected_count,
                        "details": f"Normalized column '{col}' using min-max scaling"
                    })
                elif method == "zscore":
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df[col] = (df[col] - mean_val) / std_val
                    report.append({
                        "operation": "normalize",
                        "affected": affected_count,
                        "details": f"Normalized column '{col}' using z-score"
                    })
                else:
                    raise ValueError(f"Unsupported normalization method: {method}")

        else:
            raise ValueError(f"Unsupported operation type: {op_type}")

    # Convert back to list of dicts
    result_data = df.to_dict('records')

    return {
        "data": result_data,
        "report": report
    }
