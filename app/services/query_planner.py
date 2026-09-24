import json

from app.services.groq_service import ask_groq


def plan_query(question, schema):
    """
    Decide which analytical operations are required
    to answer the user's question.
    """

    schema_text = ""

    for table_name, columns in schema["tables"].items():

        schema_text += f"\nTable: {table_name}\n"

        for column in columns:

            schema_text += (
                f"  - {column['name']} "
                f"({column['type']})\n"
            )

    schema_text += "\nRelationships:\n"

    for relationship in schema["relationships"]:

        schema_text += (
            f"  - {relationship['from_table']}."
            f"{relationship['from_column']} "
            f"-> "
            f"{relationship['to_table']}."
            f"{relationship['to_column']}\n"
        )

    prompt = f"""
You are the planning brain of an AI Data Analyst Agent.

Your job is to decide what analytical operations are
required to answer the user's question.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

AVAILABLE OPERATIONS:

1. SQL
   Always required.

2. statistics
   Use when numerical analysis is useful.

3. anomaly_detection
   Use when the user asks about:
   - unusual values
   - abnormal values
   - anomalies
   - outliers
   - suspicious values

4. chart
   Use when a visual representation would materially
   help answer the question.

5. chart_type
   If chart=true, choose exactly one:
   - bar
   - line
   - pie
   - scatter

6. chart_x_column
   If chart=true, choose an actual column that can
   reasonably appear in the SQL result.

7. chart_y_column
   If chart=true, choose an actual column that can
   reasonably appear in the SQL result.

CHART RULES:

- bar:
  Category comparisons and rankings.

- line:
  Time-based trends.

- pie:
  Small category distributions.

- scatter:
  Relationship between two numerical variables.

IMPORTANT:

1. SQL is always true.
2. Do not request statistics unnecessarily.
3. Do not request anomaly detection unless useful.
4. Do not request a chart unless useful.
5. If chart=false, all chart fields must be null.
6. Do not invent table or column names.
7. Return ONLY valid JSON.
8. Do not use markdown.
9. Do not explain your decision.

Return exactly this structure:

{{
    "sql": true,
    "statistics": false,
    "anomaly_detection": false,
    "chart": false,
    "chart_type": null,
    "chart_x_column": null,
    "chart_y_column": null
}}
"""

    response = ask_groq(
        prompt
    ).strip()

    if response.startswith("```"):

        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        response = response.strip()

    try:

        plan = json.loads(
            response
        )

    except json.JSONDecodeError:

        print(
            "Planner returned invalid JSON."
        )

        plan = {
            "sql": True,
            "statistics": False,
            "anomaly_detection": False,
            "chart": False,
            "chart_type": None,
            "chart_x_column": None,
            "chart_y_column": None
        }

    plan["sql"] = True

    plan["statistics"] = bool(
        plan.get(
            "statistics",
            False
        )
    )

    plan["anomaly_detection"] = bool(
        plan.get(
            "anomaly_detection",
            False
        )
    )

    plan["chart"] = bool(
        plan.get(
            "chart",
            False
        )
    )

    if not plan["chart"]:

        plan["chart_type"] = None
        plan["chart_x_column"] = None
        plan["chart_y_column"] = None

    else:

        allowed_chart_types = {
            "bar",
            "line",
            "pie",
            "scatter"
        }

        chart_type = plan.get(
            "chart_type"
        )

        if chart_type not in allowed_chart_types:

            plan["chart"] = False
            plan["chart_type"] = None
            plan["chart_x_column"] = None
            plan["chart_y_column"] = None

    return plan