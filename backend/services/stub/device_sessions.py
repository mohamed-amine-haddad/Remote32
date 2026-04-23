# STUB — replace body of each function with real session logic when
# backend/services/device_sessions.py is ready. Change the import in
# routers/device_sessions.py from backend.services.stub.device_sessions
# to backend.services.device_sessions.

_STUB_SESSION = {
    "id": 1,
    "device_name": "STM32-01",
    "status": "active",
    "started_at": "14:32",
    "ends_at": "15:00",
    "time_left": "27:14",
    "gdb_host": "retroboy",
    "gdb_port": "3333",
}


def get_by_id(session, session_id: int, user_id: int) -> dict:
    if session_id != 1:
        raise LookupError(f"Session {session_id} not found")
    return _STUB_SESSION


def start(session, board_id: int, user_id: int) -> dict:
    return _STUB_SESSION


def end(session, session_id: int, user_id: int) -> str:
    if session_id != 1:
        raise LookupError(f"Session {session_id} not found")
    return "Session ended"
