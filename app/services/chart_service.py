import os

import pandas as pd
import plotly.express as px


ALLOWED_CHART_TYPES = {
    "bar",
    "line",
    "pie",
    "scatter"
}


def generate_chart(
    results,
    chart_type,
    x_column=None,
    y_column=None,
    output_name="analysis_chart"
):
    """
    Generate a chart based on the analytical
    plan produced by Groq.
    """

    if not results:
        return None

    if chart_type not in ALLOWED_CHART_TYPES:
        return None

    df = pd.DataFrame(results)

    if df.empty:
        return None

    # --------------------------------
    # Validate requested columns
    # --------------------------------

    if x_column and x_column not in df.columns:

        print(
            f"Chart X column not found: {x_column}"
        )

        return None

    if y_column and y_column not in df.columns:

        print(
            f"Chart Y column not found: {y_column}"
        )

        return None

    # --------------------------------
    # Convert numeric-looking columns
    # --------------------------------

    for column in df.columns:

        try:

            df[column] = pd.to_numeric(
                df[column]
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    fig = None

    # ==================================
    # BAR
    # ==================================

    if chart_type == "bar":

        if not x_column or not y_column:
            return None

        fig = px.bar(
            df,
            x=x_column,
            y=y_column,
            title=(
                f"{y_column} by {x_column}"
            )
        )

    # ==================================
    # LINE
    # ==================================

    elif chart_type == "line":

        if not x_column or not y_column:
            return None

        fig = px.line(
            df,
            x=x_column,
            y=y_column,
            title=(
                f"{y_column} over {x_column}"
            )
        )

    # ==================================
    # PIE
    # ==================================

    elif chart_type == "pie":

        if not x_column or not y_column:
            return None

        fig = px.pie(
            df,
            names=x_column,
            values=y_column,
            title=(
                f"{y_column} distribution"
            )
        )

    # ==================================
    # SCATTER
    # ==================================

    elif chart_type == "scatter":

        if not x_column or not y_column:
            return None

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=(
                f"{y_column} vs {x_column}"
            )
        )

    # ==================================
    # Save
    # ==================================

    if fig is None:
        return None

    os.makedirs(
        "data/charts",
        exist_ok=True
    )

    file_path = (
        f"data/charts/"
        f"{output_name}.html"
    )

    fig.write_html(
        file_path
    )

    return file_path