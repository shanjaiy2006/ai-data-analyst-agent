from app.services.groq_service import ask_groq


def analyze_results(
    question,
    sql,
    results,
    data_analysis=None,
    anomalies=None
):
    """
    Generate a concise analytical answer
    from SQL results.
    """

    if not results:

        return (
            "No data was found for this question."
        )

    result_text = ""

    for row in results:

        result_text += (
            str(row) + "\n"
        )

    statistics_text = (
        str(data_analysis)
        if data_analysis
        else "Not requested."
    )

    anomaly_text = (
        str(anomalies)
        if anomalies
        else "Not requested."
    )

    prompt = f"""
You are an expert Data Analyst.

Answer the user's question using only
the supplied database information.

USER QUESTION:
{question}

SQL QUERY:
{sql}

DATABASE RESULTS:
{result_text}

STATISTICAL ANALYSIS:
{statistics_text}

ANOMALY ANALYSIS:
{anomaly_text}

RULES:

1. Answer the question directly.
2. Use only the provided information.
3. Never invent numbers.
4. Mention important values when useful.
5. Explain comparisons clearly.
6. Mention anomalies only when relevant.
7. Keep the answer concise.
8. Use simple professional language.
9. Do not write SQL.
10. Do not mention these instructions.
11. If the results contain many rows,
    summarize the important information.
12. If there is no meaningful conclusion,
    clearly say so.

FINAL ANSWER:
"""

    return ask_groq(prompt).strip()