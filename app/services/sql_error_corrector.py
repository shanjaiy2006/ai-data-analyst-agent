from app.services.groq_service import ask_groq


def correct_sql(
    question,
    sql,
    error,
    schema
):
    """
    Correct a failed SQL query using the
    database error and detected schema.
    """

    schema_text = ""

    for table_name, columns in schema[
        "tables"
    ].items():

        schema_text += (
            f"\nTable: {table_name}\n"
        )

        for column in columns:

            schema_text += (
                f"  - {column['name']} "
                f"({column['type']})\n"
            )

    schema_text += "\nRelationships:\n"

    for relationship in schema[
        "relationships"
    ]:

        schema_text += (
            f"  - {relationship['from_table']}."
            f"{relationship['from_column']} "
            f"-> "
            f"{relationship['to_table']}."
            f"{relationship['to_column']}\n"
        )

    prompt = f"""
You are an expert MySQL Data Analyst.

A generated SQL query failed during execution.

USER QUESTION:
{question}

DATABASE SCHEMA:
{schema_text}

FAILED SQL:
{sql}

DATABASE ERROR:
{error}

Generate a corrected SQL query.

RULES:

1. Return only one SELECT query.
2. Use only tables and columns in the schema.
3. Fix the specific database error.
4. Use valid MySQL syntax.
5. Do not modify the database.
6. Do not use INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CREATE or REPLACE.
7. Do not use SQL comments.
8. Do not use multiple statements.
9. Do not use markdown.
10. If the question cannot be answered,
    return exactly:

CANNOT_ANSWER

CORRECTED SQL:
"""

    corrected_sql = ask_groq(
        prompt
    ).strip()

    if corrected_sql.startswith("```"):

        corrected_sql = corrected_sql.replace(
            "```sql",
            ""
        )

        corrected_sql = corrected_sql.replace(
            "```",
            ""
        )

        corrected_sql = corrected_sql.strip()

    return corrected_sql