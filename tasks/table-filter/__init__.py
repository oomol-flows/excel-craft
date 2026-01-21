#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    conditions: list[dict] | None
    columns: list[str] | None
    limit: int | None
    offset: int | None
    sort_by: list[dict] | None
class Outputs(typing.TypedDict):
    data: typing.NotRequired[list[dict]]
    filtered_count: typing.NotRequired[int]
    total_count: typing.NotRequired[int]
    columns: typing.NotRequired[list[str]]
#endregion

from oocana import Context
import pandas as pd


async def main(params: Inputs, context: Context) -> Outputs:
    """Filter and sort table data."""

    data = params["data"]
    if not data:
        return {
            "data": [],
            "filtered_count": 0,
            "total_count": 0,
            "columns": []
        }

    # Convert to DataFrame
    df = pd.DataFrame(data)
    original_count = len(df)

    # Apply conditions (filter rows)
    conditions = params.get("conditions") or []
    for cond in conditions:
        column = cond["column"]
        operator = cond["operator"]
        value = cond.get("value")

        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in data")

        col_data = df[column]

        if operator == "==":
            df = df[col_data == value]
        elif operator == "!=":
            df = df[col_data != value]
        elif operator == ">":
            df = df[col_data > value]
        elif operator == "<":
            df = df[col_data < value]
        elif operator == ">=":
            df = df[col_data >= value]
        elif operator == "<=":
            df = df[col_data <= value]
        elif operator == "contains":
            if not isinstance(value, str):
                raise ValueError(f"'contains' operator requires string value")
            df = df[col_data.astype(str).str.contains(value, na=False)]
        elif operator == "startsWith":
            if not isinstance(value, str):
                raise ValueError(f"'startsWith' operator requires string value")
            df = df[col_data.astype(str).str.startswith(value, na=False)]
        elif operator == "endsWith":
            if not isinstance(value, str):
                raise ValueError(f"'endsWith' operator requires string value")
            df = df[col_data.astype(str).str.endswith(value, na=False)]
        elif operator == "in":
            if not isinstance(value, list):
                raise ValueError(f"'in' operator requires array value")
            df = df[col_data.isin(value)]
        elif operator == "notIn":
            if not isinstance(value, list):
                raise ValueError(f"'notIn' operator requires array value")
            df = df[~col_data.isin(value)]
        elif operator == "isNull":
            df = df[col_data.isna()]
        elif operator == "notNull":
            df = df[col_data.notna()]
        elif operator == "between":
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError(f"'between' operator requires array of 2 values")
            df = df[(col_data >= value[0]) & (col_data <= value[1])]
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    # Apply sorting
    sort_by = params.get("sort_by") or []
    if sort_by:
        sort_columns = [rule["column"] for rule in sort_by]
        sort_ascending = [rule["order"] == "asc" for rule in sort_by]

        # Validate columns exist
        for col in sort_columns:
            if col not in df.columns:
                raise ValueError(f"Sort column '{col}' not found in data")

        df = df.sort_values(by=sort_columns, ascending=sort_ascending)

    # Apply offset and limit (pagination)
    offset = params.get("offset") or 0
    limit = params.get("limit")

    if offset > 0:
        df = df.iloc[offset:]

    if limit:
        df = df.head(limit)

    # Select specific columns
    selected_columns = params.get("columns")
    if selected_columns:
        # Validate columns exist
        for col in selected_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in data")
        df = df[selected_columns]

    # Convert back to list of dicts
    result_data = df.to_dict('records')
    result_columns = df.columns.tolist()

    return {
        "data": result_data,
        "filtered_count": len(result_data),
        "total_count": original_count,
        "columns": result_columns
    }
