from app.database.connection import get_connection


def get_database_schema(database_name=None):
    """
    Dynamically inspect any MySQL database.

    Returns tables, columns, primary keys and
    foreign-key relationships.
    """

    connection = get_connection(
        database_name
    )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()

        schema = {
            "database": database_name,
            "tables": {},
            "relationships": []
        }

        for row in tables:

            table_name = list(
                row.values()
            )[0]

            cursor.execute(
                f"DESCRIBE `{table_name}`"
            )

            columns = cursor.fetchall()

            schema["tables"][table_name] = []

            for column in columns:

                schema["tables"][table_name].append({
                    "name": column["Field"],
                    "type": column["Type"],
                    "nullable": column["Null"],
                    "key": column["Key"],
                    "default": column["Default"]
                })

        cursor.execute(
            """
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
            AND REFERENCED_TABLE_NAME IS NOT NULL
            """
        )

        foreign_keys = cursor.fetchall()

        for fk in foreign_keys:

            schema["relationships"].append({
                "from_table": fk["TABLE_NAME"],
                "from_column": fk["COLUMN_NAME"],
                "to_table": fk["REFERENCED_TABLE_NAME"],
                "to_column": fk["REFERENCED_COLUMN_NAME"]
            })

        return schema

    finally:

        cursor.close()
        connection.close()