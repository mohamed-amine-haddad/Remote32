# STUB — replace body of each function with real session logic when
# backend/services/application_sessions.py is ready. Change the import in
# routers/application_sessions.py from backend.services.stub.application_sessions
# to backend.services.application_sessions.

import backend.services.stub.applications as _apps

# Reusable stub control-device data (used when the application has control boards).
# In the real service this comes from the application JSON + session context.
_STUB_CONTROL_DEVICES = [
    {
        "device_id": "STM32-03",
        "label": "X-Axis Motor",
        "default_elf": "x_axis_pid.elf",
        "available_elfs": [
            {
                "filename": "x_axis_pid.elf",
                "buttons": [
                    {"label": "Start",      "uart_command": "CMD_X_START"},
                    {"label": "Stop",       "uart_command": "CMD_X_STOP"},
                    {"label": "Speed +10%", "uart_command": "CMD_X_SPD_UP"},
                    {"label": "Speed -10%", "uart_command": "CMD_X_SPD_DN"},
                    {"label": "Reverse",    "uart_command": "CMD_X_REV"},
                ],
            },
            {
                "filename": "x_axis_open_loop.elf",
                "buttons": [
                    {"label": "Run CW",    "uart_command": "CMD_X_CW"},
                    {"label": "Run CCW",   "uart_command": "CMD_X_CCW"},
                    {"label": "Full stop", "uart_command": "CMD_X_ESTOP"},
                ],
            },
        ],
    },
    {
        "device_id": "STM32-04",
        "label": "Y-Axis Motor",
        "default_elf": "y_axis_pid.elf",
        "available_elfs": [
            {
                "filename": "y_axis_pid.elf",
                "buttons": [
                    {"label": "Start",      "uart_command": "CMD_Y_START"},
                    {"label": "Stop",       "uart_command": "CMD_Y_STOP"},
                    {"label": "Speed +10%", "uart_command": "CMD_Y_SPD_UP"},
                    {"label": "Speed -10%", "uart_command": "CMD_Y_SPD_DN"},
                ],
            },
            {
                "filename": "y_axis_step_mode.elf",
                "buttons": [
                    {"label": "Step +1",  "uart_command": "CMD_Y_STEP_P"},
                    {"label": "Step -1",  "uart_command": "CMD_Y_STEP_N"},
                    {"label": "Step +10", "uart_command": "CMD_Y_STEP_PP"},
                    {"label": "Step -10", "uart_command": "CMD_Y_STEP_NN"},
                    {"label": "Home",     "uart_command": "CMD_Y_HOME"},
                ],
            },
        ],
    },
]

# In-memory session store — persists for the lifetime of the server process.
# Resets on server restart, which is fine for a stub.
_sessions: dict = {}
_next_id: list = [1]   # list so it stays mutable at module level


def _make_session(application_id: int) -> dict:
    app = _apps._APPLICATIONS.get(application_id)
    has_control = bool(app and app["descriptor"]["control_devices"])
    session_id = _next_id[0]
    _next_id[0] += 1
    return {
        "id": session_id,
        "app_name": app["name"] if app else f"Application {application_id}",
        "status": "active",
        "started_at": "14:32",
        "ends_at": "15:32",
        "time_left": "27:14",
        "gdb_host": "retroboy",
        "gdb_port": "3333",
        "control_devices": _STUB_CONTROL_DEVICES if has_control else [],
    }


def get_by_id(session, session_id: int, user_id: int) -> dict:
    data = _sessions.get(session_id)
    if not data:
        raise LookupError(f"Session {session_id} not found")
    return data


def start(session, application_id: int, user_id: int) -> dict:
    data = _make_session(application_id)
    _sessions[data["id"]] = data
    return data


def end(session, session_id: int, user_id: int) -> str:
    if session_id not in _sessions:
        raise LookupError(f"Session {session_id} not found")
    _sessions[session_id]["status"] = "ended"
    return "Session ended"


def flash(session, session_id: int, elf_filename: str) -> str:
    return f"Flashed {elf_filename}"


def send_command(session, session_id: int, uart_command: str) -> str:
    return f"Command sent: {uart_command}"
