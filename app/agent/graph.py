from langgraph.graph import StateGraph, START, END

from app.agent.state import AnalystState

from app.agent.nodes import (
    question_rewriter_node,
    schema_node,
    planner_node,
    sql_generator_node,
    sql_validator_node,
    sql_execution_node,
    sql_correction_node,
    data_analysis_node,
    anomaly_detection_node,
    chart_node,
    final_insight_node
)


def build_graph():

    graph = StateGraph(AnalystState)

    # -----------------------------------------
    # Nodes
    # -----------------------------------------

    graph.add_node(
        "question_rewriter",
        question_rewriter_node
    )

    graph.add_node(
        "schema",
        schema_node
    )

    graph.add_node(
        "planner",
        planner_node
    )

    graph.add_node(
        "sql_generator",
        sql_generator_node
    )

    graph.add_node(
        "sql_validator",
        sql_validator_node
    )

    graph.add_node(
        "sql_execution",
        sql_execution_node
    )

    graph.add_node(
        "sql_correction",
        sql_correction_node
    )

    graph.add_node(
        "data_analysis",
        data_analysis_node
    )

    graph.add_node(
        "anomaly_detection",
        anomaly_detection_node
    )

    graph.add_node(
        "chart",
        chart_node
    )

    graph.add_node(
        "final_insight",
        final_insight_node
    )

    graph.add_node(
        "analysis_router",
        lambda state: state
    )

    # -----------------------------------------
    # Main Pipeline
    # -----------------------------------------

    graph.add_edge(
        START,
        "question_rewriter"
    )

    graph.add_edge(
        "question_rewriter",
        "schema"
    )

    graph.add_edge(
        "schema",
        "planner"
    )

    graph.add_edge(
        "planner",
        "sql_generator"
    )

    graph.add_edge(
        "sql_generator",
        "sql_validator"
    )

    # -----------------------------------------
    # SQL Validation Routing
    # -----------------------------------------

    def check_validation(state):

        if state.get(
            "success",
            False
        ):
            return "valid"

        attempts = state.get(
            "sql_attempts",
            0
        )

        if attempts >= 3:
            return "failed"

        return "invalid"

    graph.add_conditional_edges(
        "sql_validator",
        check_validation,
        {
            "valid": "sql_execution",
            "invalid": "sql_correction",
            "failed": END
        }
    )

    # -----------------------------------------
    # SQL Execution Routing
    # -----------------------------------------

    def check_sql_result(state):

        if state.get(
            "success",
            False
        ):
            return "success"

        attempts = state.get(
            "sql_attempts",
            0
        )

        if attempts >= 3:
            return "failed"

        return "retry"

    graph.add_conditional_edges(
        "sql_execution",
        check_sql_result,
        {
            "success": "analysis_router",
            "retry": "sql_correction",
            "failed": END
        }
    )

    # -----------------------------------------
    # SQL Correction
    # -----------------------------------------

    graph.add_edge(
        "sql_correction",
        "sql_validator"
    )

    # -----------------------------------------
    # Analysis Router
    # -----------------------------------------

    def analysis_router(state):

        plan = state.get(
            "plan",
            {}
        )

        if plan.get(
            "statistics",
            False
        ):
            return "statistics"

        if plan.get(
            "anomaly_detection",
            False
        ):
            return "anomaly"

        if plan.get(
            "chart",
            False
        ):
            return "chart"

        return "final"

    graph.add_conditional_edges(
        "analysis_router",
        analysis_router,
        {
            "statistics": "data_analysis",
            "anomaly": "anomaly_detection",
            "chart": "chart",
            "final": "final_insight"
        }
    )

    # -----------------------------------------
    # After Statistics
    # -----------------------------------------

    def after_statistics(state):

        plan = state.get(
            "plan",
            {}
        )

        if plan.get(
            "anomaly_detection",
            False
        ):
            return "anomaly"

        if plan.get(
            "chart",
            False
        ):
            return "chart"

        return "final"

    graph.add_conditional_edges(
        "data_analysis",
        after_statistics,
        {
            "anomaly": "anomaly_detection",
            "chart": "chart",
            "final": "final_insight"
        }
    )

    # -----------------------------------------
    # After Anomaly Detection
    # -----------------------------------------

    def after_anomaly(state):

        plan = state.get(
            "plan",
            {}
        )

        if plan.get(
            "chart",
            False
        ):
            return "chart"

        return "final"

    graph.add_conditional_edges(
        "anomaly_detection",
        after_anomaly,
        {
            "chart": "chart",
            "final": "final_insight"
        }
    )

    # -----------------------------------------
    # Chart → Final Answer
    # -----------------------------------------

    graph.add_edge(
        "chart",
        "final_insight"
    )

    graph.add_edge(
        "final_insight",
        END
    )

    return graph.compile()