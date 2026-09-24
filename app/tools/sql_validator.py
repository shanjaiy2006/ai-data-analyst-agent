import re


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "SET",
    "CALL",
    "LOAD",
    "LOCK",
    "UNLOCK"
]


def validate_sql(query):
    """
    Validate AI-generated SQL.

    Only a single read-only SELECT statement
    is allowed.
    """

    if not query:
        return False, "SQL query is empty."

    query = query.strip()

    # AI may explicitly say the question
    # cannot be answered from the schema.
    if query.upper() == "CANNOT_ANSWER":
        return False, (
            "The question cannot be answered "
            "using the available database schema."
        )

    # Remove one trailing semicolon.
    if query.endswith(";"):
        query = query[:-1].strip()

    # Only SELECT statements are allowed.
    if not re.match(
        r"^SELECT\b",
        query,
        re.IGNORECASE
    ):
        return False, (
            "Only SELECT queries are allowed."
        )

    # Prevent multiple statements.
    if ";" in query:
        return False, (
            "Multiple SQL statements are not allowed."
        )

    # Prevent SQL comments.
    if "--" in query:
        return False, (
            "SQL comments are not allowed."
        )

    if "/*" in query or "*/" in query:
        return False, (
            "SQL block comments are not allowed."
        )

    upper_query = query.upper()

    # Block database modification commands.
    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            upper_query
        ):
            return False, (
                f"Forbidden SQL keyword detected: "
                f"{keyword}"
            )

    # Block file-writing operations.
    if re.search(
        r"\bINTO\s+OUTFILE\b",
        upper_query
    ):
        return False, (
            "INTO OUTFILE is not allowed."
        )

    if re.search(
        r"\bINTO\s+DUMPFILE\b",
        upper_query
    ):
        return False, (
            "INTO DUMPFILE is not allowed."
        )

    # Restrict result size.
    limit_match = re.search(
        r"\bLIMIT\s+(\d+)",
        upper_query
    )

    if limit_match:

        limit_value = int(
            limit_match.group(1)
        )

        if limit_value > 10000:
            return False, (
                "LIMIT cannot exceed 10000 rows."
            )

    return True, "SQL query is safe."