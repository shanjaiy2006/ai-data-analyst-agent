import pandas as pd


def detect_anomalies(results):
    """
    Detect numerical outliers using the IQR method.
    Works with any SQL result containing numeric columns.
    """

    if not results:
        return {
            "anomalies_found": False,
            "total_anomalies": 0,
            "details": []
        }

    df = pd.DataFrame(results)

    # Convert numeric-looking columns
    for column in df.columns:
        try:
            df[column] = pd.to_numeric(df[column])
        except (ValueError, TypeError):
            pass

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    anomalies = []

    for column in numeric_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        mask = (
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        )

        anomaly_rows = df[mask]

        for index, row in anomaly_rows.iterrows():

            anomalies.append({
                "row_index": int(index),
                "column": column,
                "value": float(row[column]),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "row": row.to_dict()
            })

    return {
        "anomalies_found": len(anomalies) > 0,
        "total_anomalies": len(anomalies),
        "details": anomalies
    }