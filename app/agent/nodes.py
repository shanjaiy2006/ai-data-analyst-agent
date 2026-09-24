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

    results = state.get(
        "results",
        []
    )

    plan = state.get(
        "plan",
        {}
    )

    print("\n[Chart Node]")

    if not plan.get(
        "chart",
        False
    ):

        print(
            "Chart generation not required."
        )

        return {
            "chart": None
        }

    if not results:

        print(
            "No results available for chart."
        )

        return {
            "chart": None
        }

    result_columns = set(
        results[0].keys()
    )

    x_column = plan.get(
        "chart_x_column"
    )

    y_column = plan.get(
        "chart_y_column"
    )

    if (
        x_column not in result_columns
        or y_column not in result_columns
    ):

        print(
            "Planner-selected chart columns "
            "are not present in the SQL result."
        )

        print(
            "Available columns:",
            list(result_columns)
        )

        return {
            "chart": None
        }

    chart = generate_chart(
        results,
        plan.get("chart_type"),
        x_column,
        y_column
    )

    print(
        "Chart:",
        chart
    )

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