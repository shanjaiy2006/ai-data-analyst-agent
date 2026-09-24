import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_server_connection():
    """
    Connect to the MySQL server without selecting a database.
    """

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def get_connection(database_name=None):
    """
    Connect to MySQL.

    If database_name is provided, use it.
    Otherwise use the default database from .env.
    """

    database = (
        database_name
        if database_name
        else os.getenv("DB_NAME")
    )

    if not database:
        raise ValueError(
            "No database name was provided."
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=database
    )