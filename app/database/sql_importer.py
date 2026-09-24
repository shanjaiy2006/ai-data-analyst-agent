import os
import re
import uuid

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_server_connection():
    """
    Connect to MySQL server without selecting a database.
    """

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def create_temporary_database():
    """
    Create a unique temporary database for an uploaded SQL file.
    """

    database_name = (
        f"ai_uploaded_"
        f"{uuid.uuid4().hex[:12]}"
    )

    connection = get_server_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            f"CREATE DATABASE `{database_name}`"
        )

        connection.commit()

        cursor.close()

        return database_name

    finally:

        connection.close()


def split_sql_statements(sql_content):
    """
    Split a SQL dump into executable statements.

    sqlparse handles quoted strings, comments and
    multi-line SQL much more reliably than simply
    splitting on semicolons.
    """

    import sqlparse

    statements = sqlparse.split(sql_content)

    cleaned_statements = []

    for statement in statements:

        statement = statement.strip()

        if not statement:
            continue

        cleaned_statements.append(statement)

    return cleaned_statements


def validate_import_statement(statement):
    """
    Allow only database/schema/data statements required
    for importing a user-provided SQL database.

    Dangerous server-level commands are rejected.
    """

    normalized = statement.strip().upper()

    forbidden = [
        "GRANT ",
        "REVOKE ",
        "CREATE USER",
        "ALTER USER",
        "DROP USER",
        "CREATE ROLE",
        "DROP ROLE",
        "LOAD DATA",
        "INTO OUTFILE",
        "INTO DUMPFILE",
        "SHUTDOWN",
        "INSTALL ",
        "UNINSTALL ",
        "SET GLOBAL",
        "SET PERSIST"
    ]

    for keyword in forbidden:

        if keyword in normalized:

            return False, (
                f"Forbidden SQL statement detected: "
                f"{keyword.strip()}"
            )

    allowed_prefixes = (
        "CREATE TABLE",
        "CREATE DATABASE",
        "CREATE INDEX",
        "CREATE UNIQUE INDEX",
        "ALTER TABLE",
        "INSERT INTO",
        "REPLACE INTO",
        "UPDATE",
        "DELETE FROM",
        "DROP TABLE",
        "DROP INDEX",
        "TRUNCATE TABLE",
        "USE ",
        "--",
        "/*",
        "SET ",
    )

    if not normalized.startswith(allowed_prefixes):

        return False, (
            "Unsupported SQL statement in uploaded file."
        )

    return True, "Statement is allowed."


def import_sql_file(file_path):
    """
    Import a user-provided SQL file into a unique
    temporary MySQL database.

    Returns the temporary database name.
    """

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            "Uploaded SQL file was not found."
        )

    if not file_path.lower().endswith(".sql"):

        raise ValueError(
            "Only .sql files are supported."
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        sql_content = file.read()

    if not sql_content.strip():

        raise ValueError(
            "The uploaded SQL file is empty."
        )

    database_name = create_temporary_database()

    connection = None

    try:

        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=database_name
        )

        cursor = connection.cursor()

        statements = split_sql_statements(
            sql_content
        )

        if not statements:

            raise ValueError(
                "No SQL statements were found."
            )

        executed_count = 0

        for statement in statements:

            is_valid, message = (
                validate_import_statement(statement)
            )

            if not is_valid:

                raise ValueError(message)

            normalized = statement.strip().upper()

            # CREATE DATABASE and USE statements are
            # unnecessary because the temporary database
            # is already selected.
            if normalized.startswith(
                "CREATE DATABASE"
            ):
                continue

            if normalized.startswith("USE "):
                continue

            cursor.execute(statement)

            executed_count += 1

        connection.commit()

        cursor.close()

        return {
            "database_name": database_name,
            "statements_executed": executed_count
        }

    except Exception:

        if connection:

            connection.rollback()

        drop_temporary_database(
            database_name
        )

        raise

    finally:

        if connection:
            connection.close()


def drop_temporary_database(database_name):
    """
    Delete an uploaded temporary database.
    """

    if not re.match(
        r"^ai_uploaded_[a-f0-9]{12}$",
        database_name
    ):
        raise ValueError(
            "Invalid temporary database name."
        )

    connection = get_server_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            f"DROP DATABASE IF EXISTS "
            f"`{database_name}`"
        )

        connection.commit()

        cursor.close()

    finally:

        connection.close()

def cleanup_database(database_name):
    """
    Delete a temporary uploaded database.
    """

    drop_temporary_database(
        database_name
    )