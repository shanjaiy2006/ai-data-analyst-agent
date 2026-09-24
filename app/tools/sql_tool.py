from app.database.connection import get_connection
from app.tools.sql_validator import validate_sql
from app.services.result_formatter import format_results


MAX_ROWS = 1000


def execute_sql(
    query,
    database_name=None
):
    """
    Execute a validated read-only SQL query
    against the selected database.
    """

    query = query.strip()

    is_valid, message = validate_sql(
        query
    )

    if not is_valid:

        raise ValueError(
            f"SQL validation failed: {message}"
        )

    connection = get_connection(
        database_name
    )

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(query)

        results = cursor.fetchmany(
            MAX_ROWS
        )

        results = format_results(
            results,
            MAX_ROWS
        )

        cursor.close()

        return results

    finally:

        connection.close()