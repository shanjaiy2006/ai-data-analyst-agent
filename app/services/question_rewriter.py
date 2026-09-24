from app.services.groq_service import ask_groq


def rewrite_question(
    question,
    conversation
):
    """
    Convert a follow-up question into a
    self-contained question.
    """

    if not conversation:

        return question

    conversation_text = ""

    for message in conversation:

        conversation_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are an expert data analyst.

Rewrite the user's current question into a
self-contained database question.

CONVERSATION HISTORY:
{conversation_text}

CURRENT QUESTION:
{question}

RULES:

1. If the current question is already complete,
   return it unchanged.

2. If it is a follow-up question, use the
   conversation history to understand it.

3. Preserve the user's intended meaning.

4. Do not answer the question.

5. Return only the rewritten question.

REWRITTEN QUESTION:
"""

    rewritten = ask_groq(prompt)

    return rewritten.strip()