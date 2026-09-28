from app.services.query_planner import plan_query
from app.database.schema_inspector import get_database_schema
from app.services.sql_generator import generate_sql
from app.services.sql_error_corrector import correct_sql
from app.services.data_analyzer import analyze_data
from app.services.anomaly_detector import detect_anomalies
from app.services.chart_service import generate_chart
from app.services.result_analyzer import analyze_results
from app.services.question_rewriter import rewrite_question

from app.tools.sql_validator import validate_sql
from app.tools.sql_tool import execute_sql


def question_rewriter_node(state):

    question = state["question"]

    conversation = state.get(
        "conversation",
        []
    )

    print("\n[Question Rewriter Node]")

    rewritten_question = rewrite_question(
        question,
        conversation
    )

    print("Original question:")
    print(question)

    print("\nRewritten question:")
    print(rewritten_question)

    return {
        "original_question": question,
        "question": rewritten_question
    }


def schema_node(state):

    database_name = state["database_name"]

    print("\n[Schema Node]")

    print(
        "Active database:",
        database_name
    )

    schema = get_database_schema(
        database_name
    )

    print(
        "Tables found:",
        list(schema["tables"].keys())
    )

    return {
        "schema": schema
    }


def planner_node(state):

    question = state["question"]

    schema = state["schema"]

    plan = plan_query(
        question,
        schema
    )

    print("\n[Planner Node]")

    print("Plan:")
    print(plan)

    return {
        "plan": plan
    }


def sql_generator_node(state):

    question = state["question"]

    schema = state["schema"]

    sql = generate_sql(
        question,
        schema
    )

    print("\n[SQL Generator Node]")

    print("Generated SQL:")
    print(sql)

    return {
        "sql": sql,
        "sql_attempts": 0
    }


def sql_validator_node(state):

    sql = state["sql"]

    print("\n[SQL Validator Node]")

    is_valid, message = validate_sql(
        sql
    )

    print(
        "Validation:",
        message
    )

    return {
        "success": is_valid,
        "error": (
            None
            if is_valid
            else message
        )
    }


def sql_execution_node(state):

    sql = state["sql"]

    database_name = state["database_name"]

    attempts = state.get(
        "sql_attempts",
        0
    )

    print("\n[SQL Execution Node]")

    print(
        "Database:",
        database_name
    )

    try:

        results = execute_sql(
            sql,
            database_name
        )

        print(
            "SQL executed successfully."
        )

        print(
            "Rows returned:",
            len(results)
        )

        return {
            "results": results,
            "result_count": len(results),
            "success": True,
            "error": None,
            "sql_attempts": attempts + 1
        }

    except Exception as e:

        error = str(e)

        print(
            "\nSQL execution error:"
        )

        print(error)

        return {
            "results": [],
            "result_count": 0,
            "success": False,
            "error": error,
            "sql_attempts": attempts + 1
        }


def sql_correction_node(state):

    question = state["question"]

    sql = state["sql"]

    error = state["error"]

    schema = state["schema"]

    attempts = state.get(
        "sql_attempts",
        0
    )

    print("\n[SQL Correction Node]")

    if attempts >= 3:

        print(
            "Maximum SQL correction attempts reached."
        )

        return {
            "success": False,
            "error": (
                "Maximum SQL correction attempts reached."
            )
        }

    corrected_sql = correct_sql(
        question,
        sql,
        error,
        schema
    )

    print("Corrected SQL:")
    print(corrected_sql)

    return {
        "sql": corrected_sql,
        "sql_attempts": attempts + 1
    }


def data_analysis_node(state):

    results = state.get(
        "results",
        []
    )

    plan = state.get(
        "plan",
        {}
    )

    print("\n[Data Analysis Node]")

    if not plan.get(
        "statistics",
        False
    ):

        print(
            "Statistical analysis not required."
        )

        return {
            "data_analysis": None
        }

    data_analysis = analyze_data(
        results
    )

    print(
        "Statistical analysis completed."
    )

    return {
        "data_analysis": data_analysis
    }


def anomaly_detection_node(state):

    results = state.get(
        "results",
        []
    )

    plan = state.get(
        "plan",
        {}
    )

    print(
        "\n[Anomaly Detection Node]"
    )

    if not plan.get(
        "anomaly_detection",
        False
    ):

        print(
            "Anomaly detection not required."
        )

        return {
            "anomalies": None
        }

    anomalies = detect_anomalies(
        results
    )

    print(
        "Anomalies found:",
        anomalies["total_anomalies"]
    )

    return {
        "anomalies": anomalies
    }


def chart_node(state):
    results = state.get("results", [])
    plan = state.get("plan", {})

    print("\n[Chart Node]")

    if not plan.get("chart", False):
        print("Chart generation not required.")
        return {"chart": None}

    if not results:
        print("No results available for chart.")
        return {"chart": None}

    result_columns = list(results[0].keys())

    if len(result_columns) < 2:
        print("Not enough columns available for chart generation.")
        return {"chart": None}

    print("Actual SQL result columns:", result_columns)

    # Planner-selected columns
    x_column = plan.get("chart_x_column")
    y_column = plan.get("chart_y_column")
    chart_type = plan.get("chart_type")

    # Check whether planner-selected columns actually exist
    planner_columns_valid = (
        x_column in result_columns
        and y_column in result_columns
    )

    if planner_columns_valid:
        print("Using planner-selected chart columns.")
    else:
        print("Planner-selected columns do not match SQL result.")
        print("Using automatic chart column detection.")

        # Automatically detect suitable columns
        x_column = None
        y_column = None

        # Find a categorical/string column
        for column in result_columns:
            values = [row.get(column) for row in results]

            if any(isinstance(value, str) for value in values):
                x_column = column
                break

        # Find a numeric column
        for column in result_columns:
            values = [row.get(column) for row in results]

            numeric_values = [
                value
                for value in values
                if isinstance(value, (int, float))
            ]

            if numeric_values:
                y_column = column
                break

        # If no categorical column exists, use first column
        if x_column is None:
            x_column = result_columns[0]

        # If no numeric column exists, use second column
        if y_column is None and len(result_columns) >= 2:
            y_column = result_columns[1]

        print("Automatically selected X column:", x_column)
        print("Automatically selected Y column:", y_column)

    if x_column is None or y_column is None:
        print("Could not determine chart columns.")
        return {"chart": None}

    # Validate data types for chart type
    x_values = [row.get(x_column) for row in results]
    y_values = [row.get(y_column) for row in results]

    x_is_numeric = all(
        isinstance(value, (int, float))
        for value in x_values
        if value is not None
    )

    y_is_numeric = all(
        isinstance(value, (int, float))
        for value in y_values
        if value is not None
    )

    # Scatter charts require numeric X and Y values.
    if chart_type == "scatter":
        if not (x_is_numeric and y_is_numeric):
            print("Scatter chart requires numeric X and Y values.")
            print("Switching to bar chart.")
            chart_type = "bar"

    # If X is categorical and chart type is line,
    # bar chart is safer for arbitrary categorical data.
    if chart_type == "line" and not x_is_numeric:
        print("Line chart selected for categorical X column.")
        print("Switching to bar chart.")
        chart_type = "bar"

    print("Final chart type:", chart_type)
    print("Final X column:", x_column)
    print("Final Y column:", y_column)

    chart = generate_chart(
        results,
        chart_type,
        x_column,
        y_column
    )

    print("Chart:", chart)

    return {
        "chart": chart
    }

def final_insight_node(state):

    question = state["question"]

    sql = state["sql"]

    results = state.get(
        "results",
        []
    )

    data_analysis = state.get(
        "data_analysis"
    )

    anomalies = state.get(
        "anomalies"
    )

    print(
        "\n[Final Insight Node]"
    )

    analysis = analyze_results(
        question,
        sql,
        results,
        data_analysis,
        anomalies
    )

    print(
        "\nFinal AI Insight:"
    )

    print(analysis)

    return {
        "analysis": analysis
    }