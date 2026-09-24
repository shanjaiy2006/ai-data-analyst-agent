import pandas as pd
from decimal import Decimal


def format_results(results, max_rows=1000):
    """
    Clean SQL results before sending them
    to the analysis pipeline.
    """

    if not results:
        return []

    formatted = []

    for row in results[:max_rows]:

        clean_row = {}

        for key, value in row.items():

            if isinstance(value, Decimal):

                clean_row[key] = float(value)

            elif hasattr(value, "isoformat"):

                clean_row[key] = value.isoformat()

            else:

                clean_row[key] = value

        formatted.append(clean_row)

    return formatted


def create_dataframe(results):

    if not results:

        return pd.DataFrame()

    return pd.DataFrame(results)