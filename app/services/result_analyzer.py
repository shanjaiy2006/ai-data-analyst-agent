from app.services.groq_service import ask_groq


def analyze_results(
    question,
    sql,
    results,
    data_analysis=None,
    anomalies=None
):
    """
    Generate a final analytical explanation using:

    - User question
    - SQL query
    - Database results
    - Statistical analysis
    - Anomaly detection

    Visualization is handled separately by the chart node.
    """

    # -----------------------------------------
    # No results
    # -----------------------------------------

    if not results:
        return "No data was found for this question."

    # -----------------------------------------
    # Convert database results to text
    # -----------------------------------------

    result_text = ""

    for row in results:
        result_text += str(row) + "\n"

    # -----------------------------------------
    # Statistical information
    # -----------------------------------------

    if data_analysis:
        statistics_text = str(data_analysis)
    else:
        statistics_text = (
            "Statistical analysis was not requested."
        )

    # -----------------------------------------
    # Anomaly information
    # -----------------------------------------

    if anomalies:
        anomaly_text = str(anomalies)
    else:
        anomaly_text = (
            "Anomaly detection was not requested."
        )

    # -----------------------------------------
    # Prompt Groq
    # -----------------------------------------

    prompt = f"""
You are an expert Data Analyst.

Answer the user's question using only the
database information provided below.

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

INSTRUCTIONS:

1. Answer the user's question directly.

2. Use only the information provided.

3. Never invent numbers, names, facts,
   or conclusions.

4. Mention important numerical values
   when useful.

5. Explain comparisons clearly.

6. If anomaly information is available,
   mention important anomalies.

7. If anomaly detection was not requested,
   do not discuss anomalies.

8. If statistical analysis was not requested,
   do not invent statistical information.

9. Keep the answer concise but useful.

10. Use professional and easy-to-understand
    language.

11. Do not mention that you are an AI.

12. Do not provide SQL in the final answer.

13. Return plain analytical text only.

14. Do NOT generate charts.

15. Do NOT generate images.

16. Do NOT use Markdown image syntax such as:
    ![title](...)

17. Do NOT generate Base64 image data.

18. Do NOT generate data:image URLs.

19. Do NOT generate HTML image tags.

20. Do NOT embed visualization data in the answer.

21. Visualization is handled separately by
    the application.

FINAL ANSWER:
"""

    # -----------------------------------------
    # Get final answer from Groq
    # -----------------------------------------

    answer = ask_groq(prompt)

    if not answer:
        return "Unable to generate an analysis."

    return answer.strip()