#region generated meta
import typing
class Inputs(typing.TypedDict):
    leftData: list[dict]
    rightData: list[dict]
    joinType: typing.Literal["inner", "left", "right", "outer"]
    leftKey: typing.Any
    rightKey: typing.Any
    suffixes: list[str] | None
    dropDuplicates: bool | None
class Outputs(typing.TypedDict):
    data: typing.NotRequired[list[dict]]
    matchedRows: typing.NotRequired[int]
    leftUnmatched: typing.NotRequired[int]
    rightUnmatched: typing.NotRequired[int]
    joinType: typing.NotRequired[str]
    keyColumns: typing.NotRequired[list[str]]
#endregion

from oocana import Context
import pandas as pd


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Join two tables based on key columns.

    Supports inner, left, right, and outer joins similar to SQL JOIN operations.
    """

    # Extract parameters
    left_data = params["leftData"]
    right_data = params["rightData"]
    join_type = params["joinType"]
    left_key = params.get("leftKey")
    right_key = params.get("rightKey")
    suffixes = params.get("suffixes") or ["_x", "_y"]
    drop_duplicates = params.get("dropDuplicates", False)

    # Validate inputs
    if not left_data:
        raise ValueError("Left table data cannot be empty")
    if not right_data:
        raise ValueError("Right table data cannot be empty")

    # Convert to DataFrames
    left_df = pd.DataFrame(left_data)
    right_df = pd.DataFrame(right_data)

    # Auto-detect join keys if not specified
    if left_key is None and right_key is None:
        # Use common columns as keys
        common_cols = list(set(left_df.columns) & set(right_df.columns))
        if not common_cols:
            raise ValueError("No common columns found between tables. Please specify leftKey or rightKey.")
        left_key = common_cols
        right_key = common_cols
    elif left_key is None:
        left_key = right_key
    elif right_key is None:
        right_key = left_key

    # Normalize keys to lists
    left_keys = [left_key] if isinstance(left_key, str) else left_key
    right_keys = [right_key] if isinstance(right_key, str) else right_key

    if len(left_keys) != len(right_keys):
        raise ValueError(
            f"Number of left keys ({len(left_keys)}) must match number of right keys ({len(right_keys)})"
        )

    # Validate key columns exist
    for key in left_keys:
        if key not in left_df.columns:
            raise ValueError(f"Left key column '{key}' not found in left table. Available columns: {list(left_df.columns)}")

    for key in right_keys:
        if key not in right_df.columns:
            raise ValueError(f"Right key column '{key}' not found in right table. Available columns: {list(right_df.columns)}")

    # Store original row counts for statistics
    original_left_count = len(left_df)
    original_right_count = len(right_df)

    # Perform the join
    if join_type == "inner":
        merged_df = pd.merge(
            left_df, right_df,
            left_on=left_keys,
            right_on=right_keys,
            how="inner",
            suffixes=tuple(suffixes)
        )
    elif join_type == "left":
        merged_df = pd.merge(
            left_df, right_df,
            left_on=left_keys,
            right_on=right_keys,
            how="left",
            suffixes=tuple(suffixes)
        )
    elif join_type == "right":
        merged_df = pd.merge(
            left_df, right_df,
            left_on=left_keys,
            right_on=right_keys,
            how="right",
            suffixes=tuple(suffixes)
        )
    elif join_type == "outer":
        merged_df = pd.merge(
            left_df, right_df,
            left_on=left_keys,
            right_on=right_keys,
            how="outer",
            suffixes=tuple(suffixes)
        )
    else:
        raise ValueError(f"Invalid join type: {join_type}. Must be one of: inner, left, right, outer")

    # Drop duplicates if requested
    if drop_duplicates:
        merged_df = merged_df.drop_duplicates()

    # Calculate statistics
    matched_rows = len(merged_df)

    # For inner join, calculate unmatched rows
    if join_type == "inner":
        # Find rows from left that didn't match
        left_matched = left_df.merge(
            right_df[right_keys],
            left_on=left_keys,
            right_on=right_keys,
            how="inner"
        )
        left_unmatched = original_left_count - len(left_matched.drop_duplicates(subset=left_keys))

        # Find rows from right that didn't match
        right_matched = right_df.merge(
            left_df[left_keys],
            left_on=right_keys,
            right_on=left_keys,
            how="inner"
        )
        right_unmatched = original_right_count - len(right_matched.drop_duplicates(subset=right_keys))

    elif join_type == "left":
        # All left rows are included
        left_unmatched = 0
        # Right unmatched: rows from right not in result
        right_matched_keys = merged_df[right_keys].drop_duplicates()
        right_unmatched = original_right_count - len(
            right_df.merge(right_matched_keys, on=right_keys, how="inner")
        )

    elif join_type == "right":
        # All right rows are included
        right_unmatched = 0
        # Left unmatched: rows from left not in result
        left_matched_keys = merged_df[left_keys].drop_duplicates()
        left_unmatched = original_left_count - len(
            left_df.merge(left_matched_keys, on=left_keys, how="inner")
        )

    else:  # outer join
        # All rows from both tables are included
        left_unmatched = 0
        right_unmatched = 0

    # Convert result to list of dicts
    result_data = merged_df.to_dict(orient="records")

    # Get all key columns (combine left and right keys)
    all_key_columns = list(set(left_keys + right_keys))

    return {
        "data": result_data,
        "matchedRows": matched_rows,
        "leftUnmatched": left_unmatched,
        "rightUnmatched": right_unmatched,
        "joinType": join_type,
        "keyColumns": all_key_columns
    }
