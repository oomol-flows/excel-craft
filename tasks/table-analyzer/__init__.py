#region generated meta
import typing


class AnalysisParams(typing.TypedDict, total=False):
    method: str
    threshold: float
    timeColumn: str
    window: int
    bins: int


class Inputs(typing.TypedDict):
    data: list[dict]
    analysisType: typing.Literal["correlation", "distribution", "outliers", "trend", "summary"]
    columns: list[str] | None
    params: AnalysisParams | None


class VisualizationData(typing.TypedDict):
    type: str
    data: dict
    config: dict


class Outputs(typing.TypedDict):
    analysisType: str
    result: dict
    visualizationData: VisualizationData | None


#endregion

from oocana import Context
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest


async def main(params: Inputs, context: Context) -> Outputs:
    """
    Perform advanced statistical analysis on table data.

    Supported analysis types:
    - correlation: Correlation analysis between columns
    - distribution: Data distribution analysis
    - outliers: Outlier detection
    - trend: Trend analysis (requires time column)
    - summary: Statistical summary
    """

    # Extract parameters
    data = params["data"]
    analysis_type = params["analysisType"]
    selected_columns = params.get("columns")
    analysis_params = params.get("params") or {}

    if not data:
        raise ValueError("Data cannot be empty")

    df = pd.DataFrame(data)

    # Get numeric columns if not specified
    if not selected_columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            raise ValueError("No numeric columns found in data")
        selected_columns = numeric_cols
    else:
        # Validate selected columns exist
        for col in selected_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found. Available: {list(df.columns)}")

    result = {}
    viz_data = None

    # Perform analysis based on type
    if analysis_type == "correlation":
        result = analyze_correlation(df, selected_columns, analysis_params)
        viz_data = create_correlation_viz(result)

    elif analysis_type == "distribution":
        result = analyze_distribution(df, selected_columns, analysis_params)
        viz_data = create_distribution_viz(result)

    elif analysis_type == "outliers":
        result = analyze_outliers(df, selected_columns, analysis_params)
        viz_data = create_outliers_viz(result)

    elif analysis_type == "trend":
        result = analyze_trend(df, selected_columns, analysis_params)
        viz_data = create_trend_viz(result)

    elif analysis_type == "summary":
        result = analyze_summary(df, selected_columns)
        viz_data = None  # Summary doesn't need visualization

    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")

    return {
        "analysisType": analysis_type,
        "result": result,
        "visualizationData": viz_data
    }


def analyze_correlation(df: pd.DataFrame, columns: list[str], params: dict) -> dict:
    """Analyze correlation between columns."""
    method = params.get("method", "pearson")  # pearson, spearman, kendall

    # Calculate correlation matrix
    corr_df = df[columns].corr(method=method)
    corr_matrix = corr_df.to_dict()

    # Find strong correlations (|r| > 0.5)
    strong_correlations = []
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns):
            if i < j:  # Avoid duplicates
                corr_value = corr_df.loc[col1, col2]
                if abs(corr_value) > 0.5:
                    strength = "strong" if abs(corr_value) > 0.7 else "moderate"
                    strong_correlations.append({
                        "pair": [col1, col2],
                        "value": float(corr_value),
                        "strength": strength
                    })

    return {
        "correlationMatrix": corr_matrix,
        "strongCorrelations": strong_correlations,
        "method": method
    }


def analyze_distribution(df: pd.DataFrame, columns: list[str], params: dict) -> dict:
    """Analyze data distribution."""
    bins = params.get("bins", 10)

    distributions = {}
    for col in columns:
        data = df[col].dropna()

        # Calculate histogram
        hist, bin_edges = np.histogram(data, bins=bins)

        # Calculate statistics
        mean = float(data.mean())
        median = float(data.median())
        std = float(data.std())
        skewness = float(stats.skew(data))
        kurtosis = float(stats.kurtosis(data))

        # Normality test (Shapiro-Wilk)
        if len(data) >= 3:
            _, p_value = stats.shapiro(data[:5000])  # Limit to 5000 samples for performance
            is_normal = p_value > 0.05
        else:
            is_normal = None
            p_value = None

        distributions[col] = {
            "histogram": {
                "counts": hist.tolist(),
                "binEdges": bin_edges.tolist()
            },
            "statistics": {
                "mean": mean,
                "median": median,
                "std": std,
                "skewness": skewness,
                "kurtosis": kurtosis
            },
            "normalityTest": {
                "isNormal": is_normal,
                "pValue": float(p_value) if p_value is not None else None
            }
        }

    return {"distributions": distributions}


def analyze_outliers(df: pd.DataFrame, columns: list[str], params: dict) -> dict:
    """Detect outliers using various methods."""
    method = params.get("method", "iqr")  # iqr, zscore, isolation_forest
    threshold = params.get("threshold", 3.0)

    outlier_indices = set()
    outliers_by_column = {}
    outliers_list = []

    for col in columns:
        data = df[col].dropna()
        col_outliers = []

        if method == "iqr":
            # Interquartile Range method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            for idx in data.index:
                value = data[idx]
                if value < lower_bound or value > upper_bound:
                    outlier_indices.add(int(idx))
                    col_outliers.append(int(idx))
                    outliers_list.append({
                        "row": int(idx),
                        "column": col,
                        "value": float(value),
                        "reason": f"Outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                    })

        elif method == "zscore":
            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            for idx, z_score in zip(data.index, z_scores):
                if z_score > threshold:
                    outlier_indices.add(int(idx))
                    col_outliers.append(int(idx))
                    outliers_list.append({
                        "row": int(idx),
                        "column": col,
                        "value": float(data[idx]),
                        "reason": f"Z-score {z_score:.2f} > {threshold}"
                    })

        elif method == "isolation_forest":
            # Isolation Forest method
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            predictions = iso_forest.fit_predict(data.values.reshape(-1, 1))
            for idx, pred in zip(data.index, predictions):
                if pred == -1:  # Outlier
                    outlier_indices.add(int(idx))
                    col_outliers.append(int(idx))
                    outliers_list.append({
                        "row": int(idx),
                        "column": col,
                        "value": float(data[idx]),
                        "reason": "Detected by Isolation Forest"
                    })

        outliers_by_column[col] = len(col_outliers)

    return {
        "outlierCount": len(outlier_indices),
        "outlierIndices": sorted(list(outlier_indices)),
        "outliersByColumn": outliers_by_column,
        "outliers": outliers_list[:100],  # Limit to first 100 for output size
        "method": method
    }


def analyze_trend(df: pd.DataFrame, columns: list[str], params: dict) -> dict:
    """Analyze trends over time."""
    time_column = params.get("timeColumn")
    method = params.get("method", "linear")  # linear, polynomial, moving_average
    window = params.get("window", 5)

    if not time_column:
        raise ValueError("Trend analysis requires 'timeColumn' parameter")

    if time_column not in df.columns:
        raise ValueError(f"Time column '{time_column}' not found")

    # Sort by time column
    df_sorted = df.sort_values(time_column)

    trends = {}
    for col in columns:
        data = df_sorted[[time_column, col]].dropna()

        if len(data) < 2:
            continue

        x = np.arange(len(data))
        y = data[col].values

        if method == "linear":
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            trend_line = slope * x + intercept

            trends[col] = {
                "method": "linear",
                "slope": float(slope),
                "intercept": float(intercept),
                "rSquared": float(r_value ** 2),
                "pValue": float(p_value),
                "trendLine": trend_line.tolist(),
                "direction": "increasing" if slope > 0 else "decreasing"
            }

        elif method == "moving_average":
            # Moving average
            ma = pd.Series(y).rolling(window=window, center=True).mean()

            trends[col] = {
                "method": "moving_average",
                "window": window,
                "movingAverage": ma.tolist()
            }

        elif method == "polynomial":
            # Polynomial fit (degree 2)
            coeffs = np.polyfit(x, y, 2)
            poly = np.poly1d(coeffs)
            trend_line = poly(x)

            trends[col] = {
                "method": "polynomial",
                "coefficients": coeffs.tolist(),
                "trendLine": trend_line.tolist()
            }

    return {
        "trends": trends,
        "timeColumn": time_column,
        "method": method
    }


def analyze_summary(df: pd.DataFrame, columns: list[str]) -> dict:
    """Generate statistical summary."""
    summary = {}

    for col in columns:
        data = df[col].dropna()

        summary[col] = {
            "count": int(data.count()),
            "mean": float(data.mean()),
            "std": float(data.std()),
            "min": float(data.min()),
            "25%": float(data.quantile(0.25)),
            "50%": float(data.median()),
            "75%": float(data.quantile(0.75)),
            "max": float(data.max())
        }

    return {"summary": summary}


def create_correlation_viz(result: dict) -> VisualizationData:
    """Create visualization data for correlation analysis."""
    return {
        "type": "heatmap",
        "data": result["correlationMatrix"],
        "config": {
            "title": "Correlation Matrix",
            "colorScale": "RdBu",
            "symmetric": True
        }
    }


def create_distribution_viz(result: dict) -> VisualizationData:
    """Create visualization data for distribution analysis."""
    distributions = result["distributions"]
    first_col = list(distributions.keys())[0]

    return {
        "type": "histogram",
        "data": distributions[first_col]["histogram"],
        "config": {
            "title": f"Distribution of {first_col}",
            "xLabel": first_col,
            "yLabel": "Frequency"
        }
    }


def create_outliers_viz(result: dict) -> VisualizationData:
    """Create visualization data for outliers."""
    return {
        "type": "scatter",
        "data": {
            "outliers": result["outliers"]
        },
        "config": {
            "title": f"Outliers ({result['method']} method)",
            "highlightOutliers": True
        }
    }


def create_trend_viz(result: dict) -> VisualizationData:
    """Create visualization data for trend analysis."""
    return {
        "type": "line",
        "data": result["trends"],
        "config": {
            "title": "Trend Analysis",
            "xLabel": result["timeColumn"],
            "showTrendLine": True
        }
    }
