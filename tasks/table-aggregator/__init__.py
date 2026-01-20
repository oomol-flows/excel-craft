#region generated meta
import typing

class Aggregation(typing.TypedDict):
    column: str
    function: str
    alias: typing.NotRequired[str]

class PivotConfig(typing.TypedDict):
    index: list[str]
    columns: str
    values: str
    agg_func: str
    fill_value: typing.NotRequired[typing.Any]

class Inputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    mode: str
    group_by: typing.NotRequired[list[str]]
    aggregations: typing.NotRequired[list[Aggregation]]
    pivot: typing.NotRequired[PivotConfig]

class Outputs(typing.TypedDict):
    data: list[dict[str, typing.Any]]
    mode: str
    shape: dict[str, int]
    group_count: typing.NotRequired[int]
    pivot_columns: typing.NotRequired[list[str]]
#endregion

from oocana import Context
import pandas as pd


async def main(params: Inputs, context: Context) -> Outputs:
    """Aggregate table data using GROUP BY or pivot operations."""

    data = params["data"]
    if not data:
        return {
            "data": [],
            "mode": params["mode"],
            "shape": {"rows": 0, "cols": 0}
        }

    mode = params["mode"]

    # Convert to DataFrame
    df = pd.DataFrame(data)

    result_df: pd.DataFrame
    output: Outputs

    if mode == "groupBy":
        # GROUP BY aggregation
        group_by = params.get("group_by")
        aggregations = params.get("aggregations")

        if not group_by:
            raise ValueError("'group_by' parameter required for groupBy mode")
        if not aggregations:
            raise ValueError("'aggregations' parameter required for groupBy mode")

        # Validate group_by columns exist
        for col in group_by:
            if col not in df.columns:
                raise ValueError(f"Group by column '{col}' not found in data")

        # Build aggregation dictionary
        agg_dict: dict[str, typing.Any] = {}
        for agg in aggregations:
            col = agg["column"]
            func = agg["function"]
            alias = agg.get("alias") or f"{col}_{func}"

            if col not in df.columns:
                raise ValueError(f"Aggregation column '{col}' not found in data")

            # Map function name to pandas function
            if func == "sum":
                agg_func = "sum"
            elif func == "avg":
                agg_func = "mean"
            elif func == "count":
                agg_func = "count"
            elif func == "min":
                agg_func = "min"
            elif func == "max":
                agg_func = "max"
            elif func == "median":
                agg_func = "median"
            elif func == "std":
                agg_func = "std"
            elif func == "var":
                agg_func = "var"
            elif func == "countUnique":
                agg_func = "nunique"
            elif func == "first":
                agg_func = "first"
            elif func == "last":
                agg_func = "last"
            elif func == "list":
                agg_func = lambda x: x.tolist()
            else:
                raise ValueError(f"Unsupported aggregation function: {func}")

            # Add to aggregation dict
            if col not in agg_dict:
                agg_dict[col] = []
            agg_dict[col].append((alias, agg_func))

        # Perform group by
        grouped = df.groupby(group_by)

        # Apply aggregations
        agg_results = []
        for col, funcs in agg_dict.items():
            for alias, func in funcs:
                agg_results.append(grouped[col].agg(**{alias: func}))

        # Combine results
        if agg_results:
            result_df = pd.concat(agg_results, axis=1).reset_index()
        else:
            result_df = grouped.size().reset_index(name='count')

        group_count = len(result_df)

        output = {
            "data": result_df.to_dict('records'),
            "mode": "groupBy",
            "shape": {"rows": len(result_df), "cols": len(result_df.columns)},
            "group_count": group_count
        }

    elif mode == "pivot":
        # Pivot table
        pivot_config = params.get("pivot")
        if not pivot_config:
            raise ValueError("'pivot' parameter required for pivot mode")

        index = pivot_config["index"]
        columns = pivot_config["columns"]
        values = pivot_config["values"]
        agg_func = pivot_config["agg_func"]
        fill_value = pivot_config.get("fill_value")

        # Validate columns exist
        for col in index:
            if col not in df.columns:
                raise ValueError(f"Pivot index column '{col}' not found in data")
        if columns not in df.columns:
            raise ValueError(f"Pivot columns '{columns}' not found in data")
        if values not in df.columns:
            raise ValueError(f"Pivot values '{values}' not found in data")

        # Map aggregation function
        if agg_func == "sum":
            agg_fn = "sum"
        elif agg_func == "avg":
            agg_fn = "mean"
        elif agg_func == "count":
            agg_fn = "count"
        elif agg_func == "min":
            agg_fn = "min"
        elif agg_func == "max":
            agg_fn = "max"
        elif agg_func == "median":
            agg_fn = "median"
        else:
            raise ValueError(f"Unsupported aggregation function for pivot: {agg_func}")

        # Create pivot table
        pivot_table = pd.pivot_table(
            df,
            values=values,
            index=index,
            columns=columns,
            aggfunc=agg_fn,
            fill_value=fill_value
        )

        # Reset index to make it a regular DataFrame
        result_df = pivot_table.reset_index()

        # Flatten column names if multi-level
        if isinstance(result_df.columns, pd.MultiIndex):
            result_df.columns = ['_'.join(map(str, col)).strip('_') for col in result_df.columns.values]
        else:
            result_df.columns = [str(col) for col in result_df.columns]

        # Get the pivot columns (generated from the pivot operation)
        pivot_columns = [col for col in result_df.columns if col not in index]

        output = {
            "data": result_df.to_dict('records'),
            "mode": "pivot",
            "shape": {"rows": len(result_df), "cols": len(result_df.columns)},
            "pivot_columns": pivot_columns
        }

    else:
        raise ValueError(f"Unsupported aggregation mode: {mode}")

    return output
