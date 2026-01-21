#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    method: typing.Literal["random", "stratified", "systematic", "head", "tail"]
    size: float
    params: dict | None
class Outputs(typing.TypedDict):
    sample: typing.NotRequired[list[dict]]
    indices: typing.NotRequired[list[int]]
    sampleSize: typing.NotRequired[int]
    originalSize: typing.NotRequired[int]
    method: typing.NotRequired[str]
#endregion

from oocana import Context
import pandas as pd
import numpy as np


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Sample data using various methods.

    Sampling methods:
    - random: Random sampling (with or without replacement)
    - stratified: Stratified sampling by a column
    - systematic: Systematic sampling (every nth row)
    - head: Take first N rows
    - tail: Take last N rows
    """

    # Extract parameters
    data = params["data"]
    method = params["method"]
    size = params["size"]
    sampling_params = params.get("params") or {}

    if not data:
        raise ValueError("Data cannot be empty")

    if size <= 0:
        raise ValueError("Sample size must be greater than 0")

    df = pd.DataFrame(data)
    original_size = len(df)

    # Calculate actual sample size
    if 0 < size < 1:
        # Treat as proportion
        actual_size = int(original_size * size)
    else:
        # Treat as count
        actual_size = int(size)

    if actual_size > original_size:
        raise ValueError(f"Sample size {actual_size} cannot exceed data size {original_size}")

    # Get sampling parameters
    seed = sampling_params.get("seed")
    replacement = sampling_params.get("replacement", False)

    # Set random seed for reproducibility
    if seed is not None:
        np.random.seed(seed)

    # Perform sampling based on method
    if method == "random":
        sampled_df = df.sample(n=actual_size, replace=replacement, random_state=seed)
        indices = sampled_df.index.tolist()

    elif method == "stratified":
        stratify_column = sampling_params.get("stratifyColumn")
        if not stratify_column:
            raise ValueError("Stratified sampling requires 'stratifyColumn' parameter")

        if stratify_column not in df.columns:
            raise ValueError(f"Stratify column '{stratify_column}' not found. Available: {list(df.columns)}")

        # Calculate sample size for each stratum
        strata_sizes = df[stratify_column].value_counts()
        strata_proportions = strata_sizes / original_size

        sampled_indices = []
        for stratum, proportion in strata_proportions.items():
            stratum_df = df[df[stratify_column] == stratum]
            stratum_size = max(1, int(actual_size * proportion))  # At least 1 from each stratum

            # Ensure we don't exceed stratum size
            stratum_size = min(stratum_size, len(stratum_df))

            stratum_sample = stratum_df.sample(n=stratum_size, replace=replacement, random_state=seed)
            sampled_indices.extend(stratum_sample.index.tolist())

        # Trim to exact size if needed
        if len(sampled_indices) > actual_size:
            sampled_indices = sampled_indices[:actual_size]

        sampled_df = df.loc[sampled_indices]
        indices = sampled_indices

    elif method == "systematic":
        # Systematic sampling: select every k-th element
        step = original_size // actual_size
        if step < 1:
            step = 1

        # Start from a random position if seed is provided
        start = np.random.randint(0, step) if seed is not None else 0
        indices = list(range(start, original_size, step))[:actual_size]
        sampled_df = df.iloc[indices]

    elif method == "head":
        # Take first N rows
        sampled_df = df.head(actual_size)
        indices = list(range(actual_size))

    elif method == "tail":
        # Take last N rows
        sampled_df = df.tail(actual_size)
        indices = list(range(original_size - actual_size, original_size))

    else:
        raise ValueError(f"Invalid sampling method: {method}. Must be one of: random, stratified, systematic, head, tail")

    # Convert to list of dicts
    sample_data = sampled_df.to_dict(orient="records")

    return {
        "sample": sample_data,
        "indices": indices,
        "sampleSize": len(sample_data),
        "originalSize": original_size,
        "method": method
    }
