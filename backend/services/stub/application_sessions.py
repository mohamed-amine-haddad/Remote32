# STUB — replace body of each function with real session logic when
# backend/services/application_sessions.py is ready. Change the import in
# routers/application_sessions.py from backend.services.stub.application_sessions
# to backend.services.application_sessions.

from datetime import datetime
import backend.services.stub.applications as _apps

def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")

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
_next_id: list = [1]       # session ID counter
_uart_logs: dict = {}      # session_id → list of message dicts
_uart_next_id: list = [1]  # global UART message ID counter


def _make_session(json_path: str) -> dict:
    try:
        app = _apps._APPLICATIONS.get(int(json_path))
    except (ValueError, TypeError):
        app = None
    has_control = bool(app and app["descriptor"]["control_devices"])
    session_id = _next_id[0]
    _next_id[0] += 1

    boot_time = _now()
    boot_msgs = [
        {"id": _uart_next_id[0],     "direction": "rx", "text": "[BOOT] STM32F4 initializing...",              "timestamp": boot_time},
        {"id": _uart_next_id[0] + 1, "direction": "rx", "text": "[BOOT] HAL configured — UART2 @ 115200 baud", "timestamp": boot_time},
        {"id": _uart_next_id[0] + 2, "direction": "rx", "text": "[BOOT] System ready. Awaiting commands.",     "timestamp": boot_time},
    ]
    _uart_next_id[0] += len(boot_msgs)
    _uart_logs[session_id] = boot_msgs

    return {
        "id": session_id,
        "app_name": app["name"] if app else json_path.split("/")[-1].replace(".json", ""),
        "status": "active",
        "started_at": "14:32",
        "ends_at": "15:32",
        "time_left": "27:14",
        "gdb_host": "retroboy",
        "gdb_port": 3333,
        "control_devices": _STUB_CONTROL_DEVICES if has_control else [],
    }


def get_by_id(session, session_id: int, user_id: int) -> dict:
    data = _sessions.get(session_id)
    if not data:
        raise RuntimeError(f"Session {session_id} not found")
    return data


def start(session, json_path: str, user_id: int) -> dict:
    data = _make_session(json_path)
    _sessions[data["id"]] = data
    return data


def end(session, session_id: int, user_id: int) -> str:
    if session_id not in _sessions:
        raise RuntimeError(f"Session {session_id} not found")
    _sessions[session_id]["status"] = "ended"
    return "Session ended"


def flash(session, session_id: int, elf_filename: str) -> str:
    return f"Flashed {elf_filename}"


def send_command(session, session_id: int, uart_command: str) -> str:
    return f"Command sent: {uart_command}"


def get_uart_messages(session, session_id: int, since_id: int = 0) -> dict:
    if session_id not in _sessions:
        raise RuntimeError(f"Session {session_id} not found")
    logs = _uart_logs.get(session_id, [])
    return {"messages": [m for m in logs if m["id"] > since_id]}


def uart_send(session, session_id: int, text: str) -> str:
    if session_id not in _sessions:
        raise RuntimeError(f"Session {session_id} not found")
    now = _now()
    tx_id = _uart_next_id[0]
    rx_id = _uart_next_id[0] + 1
    _uart_next_id[0] += 2
    log = _uart_logs.setdefault(session_id, [])
    log.append({"id": tx_id, "direction": "tx", "text": text,          "timestamp": now})
    log.append({"id": rx_id, "direction": "rx", "text": f"ACK: {text}", "timestamp": now})
    return f"Sent: {text}"
