from app.services.groq_service import ask_groq


def generate_sql(question, schema):
    """
    Generate a read-only MySQL SELECT query
    using the dynamically detected schema.
    """

    schema_text = ""

    for table_name, columns in schema["tables"].items():

        schema_text += (
            f"\nTable: {table_name}\n"
        )

        for column in columns:

            schema_text += (
                f"  - {column['name']} "
                f"({column['type']})"
            )

            if column["key"] == "PRI":

                schema_text += (
                    " [PRIMARY KEY]"
                )

            schema_text += "\n"

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

Convert the user's natural language question
into a correct MySQL SELECT query.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

RULES:

1. Return only one SELECT query.
2. Use only tables and columns in the schema.
3. Follow foreign-key relationships when joining tables.
4. Use correct MySQL syntax.
5. Use meaningful aliases for calculated columns.
6. Do not modify the database.
7. Never use INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CREATE or REPLACE.
8. Do not use SQL comments.
9. Do not use multiple statements.
10. Do not use markdown.
11. If the question cannot be answered from
    the schema, return exactly:

CANNOT_ANSWER

SQL:
"""

    sql = ask_groq(
        prompt
    ).strip()

    if sql.startswith("```"):

        sql = sql.replace(
            "```sql",
            ""
        )

        sql = sql.replace(
            "```",
            ""
        )

        sql = sql.strip()

    return sql