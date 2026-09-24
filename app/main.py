import os
import tempfile

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File
)

from pydantic import BaseModel

from app.agent.graph import build_graph

from app.database.sql_importer import (
    import_sql_file,
    cleanup_database
)

from app.services.session_manager import (
    create_session,
    get_session,
    delete_session
)


app = FastAPI(
    title="AI Data Analyst Agent",
    description=(
        "Application-independent "
        "AI Data Analyst"
    ),
    version="1.0.0"
)


class AnalyzeRequest(BaseModel):

    session_id: str

    question: str

    conversation: list[
        dict[str, str]
    ] = []


@app.get("/")
def root():

    return {
        "message": (
            "AI Data Analyst Agent API is running"
        )
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/upload-sql")
async def upload_sql(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(
        ".sql"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only .sql files are supported."
        )

    temp_path = None

    try:

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".sql"
        ) as temp_file:

            temp_file.write(content)

            temp_path = temp_file.name

        result = import_sql_file(
            temp_path
        )

        database_name = result[
            "database_name"
        ]

        session_id = create_session(
            database_name
        )

        return {

            "message":
                "SQL database uploaded successfully.",

            "session_id":
                session_id,

            "database_name":
                database_name,

            "statements_executed":
                result["statements_executed"]
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if temp_path and os.path.exists(
            temp_path
        ):

            os.remove(temp_path)


@app.post("/analyze")
def analyze(
    request: AnalyzeRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    session = get_session(
        request.session_id
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail=(
                "Session not found or expired. "
                "Please upload your SQL file again."
            )
        )

    database_name = session[
        "database_name"
    ]

    try:

        agent = build_graph()

        result = agent.invoke({

            "question":
                request.question,

            "conversation":
                request.conversation,

            "database_name":
                database_name
        })

        return {

            "question":
                request.question,

            "session_id":
                request.session_id,

            "sql":
                result.get("sql"),

            "results":
                result.get(
                    "results",
                    []
                ),

            "analysis":
                result.get(
                    "analysis"
                ),

            "chart":
                result.get(
                    "chart"
                ),

            "error":
                result.get(
                    "error"
                )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.delete("/session/{session_id}")
def close_session(
    session_id: str
):

    session = delete_session(
        session_id
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    database_name = session[
        "database_name"
    ]

    try:

        cleanup_database(
            database_name
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Session removed but "
                "database cleanup failed: "
                f"{str(e)}"
            )
        )

    return {
        "message": "Session closed successfully."
    }