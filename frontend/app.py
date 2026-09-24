import os

import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide"
)


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "database_name" not in st.session_state:
    st.session_state.database_name = None

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def upload_sql_file(uploaded_file):
    """
    Upload SQL file to FastAPI and create a session.
    """

    try:

        response = requests.post(
            f"{API_BASE_URL}/upload-sql",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/sql"
                )
            },
            timeout=120
        )

        if response.status_code != 200:

            try:
                error_data = response.json()
                error_message = error_data.get(
                    "detail",
                    "SQL upload failed."
                )
            except Exception:
                error_message = response.text

            return None, error_message

        return response.json(), None

    except requests.exceptions.ConnectionError:

        return (
            None,
            "Unable to connect to the FastAPI server."
        )

    except requests.exceptions.Timeout:

        return (
            None,
            "The SQL upload request timed out."
        )

    except Exception as e:

        return (
            None,
            f"Unexpected error: {str(e)}"
        )


def analyze_question(question):
    """
    Send a question to FastAPI using the
    current uploaded database session.
    """

    payload = {
        "session_id": st.session_state.session_id,
        "question": question,
        "conversation": st.session_state.conversation
    }

    try:

        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=180
        )

        if response.status_code != 200:

            try:
                error_data = response.json()
                error_message = error_data.get(
                    "detail",
                    "Analysis failed."
                )
            except Exception:
                error_message = response.text

            return None, error_message

        return response.json(), None

    except requests.exceptions.ConnectionError:

        return (
            None,
            "Unable to connect to the FastAPI server."
        )

    except requests.exceptions.Timeout:

        return (
            None,
            "The analysis request timed out."
        )

    except Exception as e:

        return (
            None,
            f"Unexpected error: {str(e)}"
        )


def close_current_session():
    """
    Close the current backend session and
    delete its temporary database.
    """

    if not st.session_state.session_id:
        return

    try:

        requests.delete(
            f"{API_BASE_URL}/session/"
            f"{st.session_state.session_id}",
            timeout=30
        )

    except Exception:
        pass

    st.session_state.session_id = None
    st.session_state.database_name = None
    st.session_state.conversation = []
    st.session_state.uploaded_file_name = None


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("AI Data Analyst")

st.write(
    "Upload a SQL database and ask questions "
    "using natural language."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Data Source")

    uploaded_file = st.file_uploader(
        "Upload SQL file",
        type=["sql"],
        help=(
            "Upload a SQL dump containing "
            "CREATE TABLE and INSERT statements."
        )
    )

    if uploaded_file is not None:

        if st.button(
            "Upload Database",
            use_container_width=True
        ):

            with st.spinner(
                "Importing database..."
            ):

                result, error = upload_sql_file(
                    uploaded_file
                )

            if error:

                st.error(error)

            else:

                # Close previous session if one exists
                if st.session_state.session_id:

                    close_current_session()

                st.session_state.session_id = (
                    result["session_id"]
                )

                st.session_state.database_name = (
                    result["database_name"]
                )

                st.session_state.uploaded_file_name = (
                    uploaded_file.name
                )

                st.session_state.conversation = []

                st.success(
                    "Database uploaded successfully."
                )

    st.divider()

    st.subheader("Current Session")

    if st.session_state.session_id:

        st.write(
            f"File: "
            f"{st.session_state.uploaded_file_name}"
        )

        st.write(
            "Status: Connected"
        )

        if st.button(
            "Clear Session",
            use_container_width=True
        ):

            close_current_session()

            st.rerun()

    else:

        st.write(
            "No database uploaded."
        )


# --------------------------------------------------
# Main Application
# --------------------------------------------------

if not st.session_state.session_id:

    st.info(
        "Upload a SQL database from the sidebar "
        "to begin."
    )

else:

    st.subheader("Ask a Question")

    question = st.text_input(
        "Natural language question",
        placeholder=(
            "Example: What are the top 10 customers "
            "by total order amount?"
        ),
        key="question_input"
    )

    analyze_button = st.button(
        "Analyze",
        type="primary"
    )

    if analyze_button:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "Analyzing the database..."
            ):

                result, error = analyze_question(
                    question
                )

            if error:

                st.error(error)

            elif result:

                analysis = result.get(
                    "analysis"
                )

                results = result.get(
                    "results",
                    []
                )

                sql = result.get(
                    "sql"
                )

                chart_path = result.get(
                    "chart"
                )

                backend_error = result.get(
                    "error"
                )

                # --------------------------------------
                # Conversation memory
                # --------------------------------------

                st.session_state.conversation.append({
                    "role": "user",
                    "content": question
                })

                if analysis:

                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": analysis
                    })

                # --------------------------------------
                # Analysis
                # --------------------------------------

                st.subheader("Analysis")

                if analysis:

                    st.write(analysis)

                else:

                    st.write(
                        "No analysis was generated."
                    )

                # --------------------------------------
                # Results
                # --------------------------------------

                if results:

                    st.subheader("Query Results")

                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True
                    )

                # --------------------------------------
                # Chart
                # --------------------------------------

                if chart_path:

                    st.subheader(
                        "Visualization"
                    )

                    if os.path.exists(
                        chart_path
                    ):

                        try:

                            with open(
                                chart_path,
                                "r",
                                encoding="utf-8"
                            ) as chart_file:

                                chart_html = (
                                    chart_file.read()
                                )

                            st.components.v1.html(
                                chart_html,
                                height=600,
                                scrolling=True
                            )

                        except Exception as e:

                            st.warning(
                                "The chart was generated "
                                "but could not be displayed."
                            )

                    else:

                        st.warning(
                            "The chart file could not "
                            "be found."
                        )

                # --------------------------------------
                # SQL
                # --------------------------------------

                if sql:

                    with st.expander(
                        "Generated SQL"
                    ):

                        st.code(
                            sql,
                            language="sql"
                        )

                # --------------------------------------
                # Backend error
                # --------------------------------------

                if backend_error:

                    st.error(
                        backend_error
                    )


# --------------------------------------------------
# Conversation History
# --------------------------------------------------

if (
    st.session_state.session_id
    and st.session_state.conversation
):

    st.divider()

    st.subheader(
        "Conversation History"
    )

    for message in (
        st.session_state.conversation
    ):

        if message["role"] == "user":

            st.markdown(
                f"**You:** {message['content']}"
            )

        elif message["role"] == "assistant":

            st.markdown(
                f"**Analyst:** {message['content']}"
            )