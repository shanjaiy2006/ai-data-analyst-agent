from typing import TypedDict, Any


class AnalystState(TypedDict, total=False):

    question: str

    original_question: str

    conversation: list[dict[str, str]]

    database_name: str

    schema: dict

    plan: dict

    sql: str

    sql_attempts: int

    results: list[dict[str, Any]]

    result_count: int

    data_analysis: dict

    anomalies: dict

    chart: str

    analysis: str

    success: bool

    error: str