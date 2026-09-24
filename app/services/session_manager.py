import threading
import time
import uuid


SESSION_TIMEOUT_SECONDS = 60 * 60


_sessions = {}

_lock = threading.Lock()


def create_session(database_name):
    """
    Create a session for an uploaded database.
    """

    session_id = uuid.uuid4().hex

    with _lock:

        _sessions[session_id] = {
            "database_name": database_name,
            "created_at": time.time(),
            "last_accessed": time.time()
        }

    return session_id


def get_session(session_id):
    """
    Retrieve a session and update its last-accessed time.
    """

    if not session_id:
        return None

    with _lock:

        session = _sessions.get(
            session_id
        )

        if not session:
            return None

        current_time = time.time()

        if (
            current_time
            - session["last_accessed"]
            > SESSION_TIMEOUT_SECONDS
        ):

            del _sessions[session_id]

            return None

        session["last_accessed"] = current_time

        return session.copy()


def delete_session(session_id):
    """
    Remove a session from memory.
    """

    with _lock:

        return _sessions.pop(
            session_id,
            None
        )


def list_sessions():
    """
    Return basic information about active sessions.
    """

    with _lock:

        return {
            session_id: session.copy()
            for session_id, session
            in _sessions.items()
        }