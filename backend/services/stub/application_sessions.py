# STUB — replace body of each function with real session logic when
# backend/services/application_sessions.py is ready. Change the import in
# routers/application_sessions.py from backend.services.stub.application_sessions
# to backend.services.application_sessions.

_STUB_SESSION = {
    "id": 1,
    "app_name": "Multi-Axis Motion Lab",
    "status": "active",
    "started_at": "14:32",
    "ends_at": "15:32",
    "time_left": "27:14",
    "gdb_host": "retroboy",
    "gdb_port": "3333",
    "control_devices": [
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
                {
                    "filename": "y_axis_calibration.elf",
                    "buttons": [
                        {"label": "Cal start", "uart_command": "CMD_Y_CAL_START"},
                        {"label": "Cal stop",  "uart_command": "CMD_Y_CAL_STOP"},
                        {"label": "Save",      "uart_command": "CMD_Y_CAL_SAVE"},
                    ],
                },
            ],
        },
        {
            "device_id": "STM32-05",
            "label": "Sensor Array",
            "default_elf": "sensor_continuous.elf",
            "available_elfs": [
                {
                    "filename": "sensor_continuous.elf",
                    "buttons": [
                        {"label": "Start sampling", "uart_command": "CMD_S_START"},
                        {"label": "Stop sampling",  "uart_command": "CMD_S_STOP"},
                        {"label": "Reset counters", "uart_command": "CMD_S_RESET"},
                    ],
                },
                {
                    "filename": "sensor_trigger.elf",
                    "buttons": [
                        {"label": "Trigger once",  "uart_command": "CMD_S_TRIG"},
                        {"label": "Trigger burst", "uart_command": "CMD_S_BURST"},
                        {"label": "Set threshold", "uart_command": "CMD_S_THRESH"},
                        {"label": "Read raw",      "uart_command": "CMD_S_RAW"},
                    ],
                },
            ],
        },
    ],
}


def get_by_id(session, session_id: int, user_id: int) -> dict:
    if session_id != 1:
        raise LookupError(f"Session {session_id} not found")
    return _STUB_SESSION


def start(session, application_id: int, user_id: int) -> dict:
    return _STUB_SESSION


def end(session, session_id: int, user_id: int) -> str:
    if session_id != 1:
        raise LookupError(f"Session {session_id} not found")
    return "Session ended"


def flash(session, session_id: int, elf_filename: str) -> str:
    return f"Flashed {elf_filename}"


def send_command(session, session_id: int, uart_command: str) -> str:
    return f"Command sent: {uart_command}"
