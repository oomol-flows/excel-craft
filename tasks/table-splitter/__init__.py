#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    method: typing.Literal["ratio", "condition", "chunks", "stratified"]
    params: dict | None
class Outputs(typing.TypedDict):
    splits: typing.NotRequired[list[dict]]
    method: typing.NotRequired[str]
#endregion

from oocana import Context
import pandas as pd
import numpy as np


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Split table data using various methods.

    Splitting methods:
    - ratio: Split by proportions (e.g., 70/20/10 for train/val/test)
    - condition: Split based on conditions/expressions
    - chunks: Split into fixed-size chunks
    - stratified: Split while maintaining class distribution
    """

    # Extract parameters
    data = params["data"]
    method = params["method"]
    split_params = params.get("params") or {}

    if not data:
        raise ValueError("Data cannot be empty")

    df = pd.DataFrame(data)
    original_size = len(df)

    splits: list[SplitResult] = []

    # Perform splitting based on method
    if method == "ratio":
        splits = split_by_ratio(df, split_params, original_size)

    elif method == "condition":
        splits = split_by_condition(df, split_params, original_size)

    elif method == "chunks":
        splits = split_by_chunks(df, split_params, original_size)

    elif method == "stratified":
        splits = split_stratified(df, split_params, original_size)

    else:
        raise ValueError(f"Invalid splitting method: {method}")

    return {
        "splits": splits,
        "method": method
    }


def split_by_ratio(df: pd.DataFrame, params: SplitParams, original_size: int) -> list[SplitResult]:
    """Split data by ratios."""
    ratios = params.get("ratios")
    names = params.get("names")
    shuffle = params.get("shuffle", False)
    seed = params.get("seed")

    if not ratios:
        raise ValueError("Ratio method requires 'ratios' parameter")

    # Validate ratios sum to approximately 1
    total_ratio = sum(ratios)
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")

    # Generate default names if not provided
    if not names:
        names = [f"split_{i+1}" for i in range(len(ratios))]
    elif len(names) != len(ratios):
        raise ValueError(f"Number of names ({len(names)}) must match number of ratios ({len(ratios)})")

    # Shuffle if requested
    if shuffle:
        df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    # Calculate split sizes
    split_sizes = [int(original_size * ratio) for ratio in ratios]

    # Adjust last split to include remaining rows
    split_sizes[-1] = original_size - sum(split_sizes[:-1])

    # Create splits
    splits = []
    start_idx = 0

    for i, (name, size) in enumerate(zip(names, split_sizes)):
        end_idx = start_idx + size
        split_df = df.iloc[start_idx:end_idx]

        splits.append({
            "name": name,
            "data": split_df.to_dict(orient="records"),
            "size": len(split_df),
            "percentage": (len(split_df) / original_size) * 100
        })

        start_idx = end_idx

    return splits


def split_by_condition(df: pd.DataFrame, params: SplitParams, original_size: int) -> list[SplitResult]:
    """Split data based on conditions."""
    conditions = params.get("conditions")

    if not conditions:
        raise ValueError("Condition method requires 'conditions' parameter")

    splits = []
    remaining_df = df.copy()

    for condition in conditions:
        name = condition.get("name")
        expression = condition.get("expression")

        if not name or not expression:
            raise ValueError("Each condition must have 'name' and 'expression'")

        try:
            # Evaluate condition - replace column references
            # e.g., "{age} >= 18" becomes "df['age'] >= 18"
            eval_expr = expression
            for col in df.columns:
                eval_expr = eval_expr.replace(f"{{{col}}}", f"df['{col}']")

            # Create mask
            mask = eval(eval_expr, {"df": df})
            split_df = df[mask]

            splits.append({
                "name": name,
                "data": split_df.to_dict(orient="records"),
                "size": len(split_df),
                "percentage": (len(split_df) / original_size) * 100
            })

            # Remove matched rows from remaining
            remaining_df = remaining_df[~remaining_df.index.isin(split_df.index)]

        except Exception as e:
            raise ValueError(f"Error evaluating condition '{expression}': {str(e)}")

    # Add remaining rows as a final split
    if len(remaining_df) > 0:
        splits.append({
            "name": "remaining",
            "data": remaining_df.to_dict(orient="records"),
            "size": len(remaining_df),
            "percentage": (len(remaining_df) / original_size) * 100
        })

    return splits


def split_by_chunks(df: pd.DataFrame, params: SplitParams, original_size: int) -> list[SplitResult]:
    """Split data into fixed-size chunks."""
    chunk_size = params.get("chunkSize")

    if not chunk_size:
        raise ValueError("Chunks method requires 'chunkSize' parameter")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than 0")

    splits = []
    num_chunks = (original_size + chunk_size - 1) // chunk_size  # Ceiling division

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, original_size)
        chunk_df = df.iloc[start_idx:end_idx]

        splits.append({
            "name": f"chunk_{i+1}",
            "data": chunk_df.to_dict(orient="records"),
            "size": len(chunk_df),
            "percentage": (len(chunk_df) / original_size) * 100
        })

    return splits


def split_stratified(df: pd.DataFrame, params: SplitParams, original_size: int) -> list[SplitResult]:
    """Split data while maintaining class distribution."""
    stratify_column = params.get("stratifyColumn")
    ratios = params.get("ratios")
    names = params.get("names")
    seed = params.get("seed")

    if not stratify_column:
        raise ValueError("Stratified method requires 'stratifyColumn' parameter")

    if not ratios:
        raise ValueError("Stratified method requires 'ratios' parameter")

    if stratify_column not in df.columns:
        raise ValueError(f"Stratify column '{stratify_column}' not found. Available: {list(df.columns)}")

    # Validate ratios
    total_ratio = sum(ratios)
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")

    # Generate default names
    if not names:
        names = [f"split_{i+1}" for i in range(len(ratios))]
    elif len(names) != len(ratios):
        raise ValueError(f"Number of names must match number of ratios")

    # Initialize splits
    split_dfs = [pd.DataFrame() for _ in range(len(ratios))]

    # Split each stratum according to ratios
    for stratum_value in df[stratify_column].unique():
        stratum_df = df[df[stratify_column] == stratum_value]

        # Shuffle within stratum
        if seed is not None:
            stratum_df = stratum_df.sample(frac=1, random_state=seed).reset_index(drop=True)

        stratum_size = len(stratum_df)
        start_idx = 0

        for i, ratio in enumerate(ratios):
            if i == len(ratios) - 1:
                # Last split gets remaining rows
                end_idx = stratum_size
            else:
                end_idx = start_idx + int(stratum_size * ratio)

            split_dfs[i] = pd.concat([split_dfs[i], stratum_df.iloc[start_idx:end_idx]])
            start_idx = end_idx

    # Convert to output format
    splits = []
    for name, split_df in zip(names, split_dfs):
        splits.append({
            "name": name,
            "data": split_df.to_dict(orient="records"),
            "size": len(split_df),
            "percentage": (len(split_df) / original_size) * 100
        })

    return splits
