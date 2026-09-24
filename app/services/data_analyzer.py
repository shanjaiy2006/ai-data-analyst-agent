import pandas as pd


def analyze_data(results):
    """
    Perform generic statistical analysis on SQL results.
    Works with different types of datasets.
    """

    if not results:
        return {
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "numeric_summary": {},
            "missing_values": {},
            "unique_values": {},
            "outliers": {}
        }

    # Convert SQL results into DataFrame
    df = pd.DataFrame(results)

    # Convert Decimal values to float where possible
    for column in df.columns:
        try:
            df[column] = pd.to_numeric(df[column])
        except (ValueError, TypeError):
            pass

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    numeric_summary = {}

    for column in numeric_columns:

        numeric_summary[column] = {
            "mean": float(df[column].mean()),
            "median": float(df[column].median()),
            "min": float(df[column].min()),
            "max": float(df[column].max()),
            "std": float(df[column].std())
            if len(df[column]) > 1 else 0.0
        }

    # Missing values
    missing_values = {}

    for column in df.columns:
        missing_values[column] = int(df[column].isna().sum())

    # Unique values
    unique_values = {}

    for column in df.columns:
        unique_values[column] = int(df[column].nunique())

    # Simple IQR outlier detection
    outliers = {}

    for column in numeric_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        count = (
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        ).sum()

        outliers[column] = int(count)

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "numeric_summary": numeric_summary,
        "missing_values": missing_values,
        "unique_values": unique_values,
        "outliers": outliers
    }