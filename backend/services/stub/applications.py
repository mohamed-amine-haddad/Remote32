# STUB — replace body of each function with real DB/config queries when
# backend/services/applications.py is ready. Change the import in routers/applications.py
# from backend.services.stub.applications to backend.services.applications.

_APPLICATIONS = {
    1: {
        "id": 1,
        "name": "Motor Control Lab",
        "status": "free",
        "description": "Full closed-loop DC motor control application. Main STM32 runs a PID controller over PWM. Control board sends speed setpoint commands and direction signals over UART. Includes encoder feedback and current sensing.",
        "descriptor": {
            "name": "Motor Control Lab",
            "description": "Closed-loop DC motor control with PID. Control board manages speed and direction setpoints.",
            "main_device": {
                "device_id": "STM32-01",
                "role": "PID controller — reads encoder, drives PWM output",
                "openocd_config_path": "board/stm32f4discovery.cfg",
                "camera": {"enabled": True, "stream_path": "/stream/app1"},
            },
            "control_devices": [
                {
                    "device_id": "STM32-03",
                    "default_elf": "motor_control_v1.elf",
                    "available_elfs": [
                        "motor_control_v1.elf",
                        "motor_control_v2_turbo.elf",
                        "motor_open_loop.elf",
                    ],
                    "buttons": [
                        {"label": "Start motor", "uart_command": "CMD_START"},
                        {"label": "Stop motor",  "uart_command": "CMD_STOP"},
                        {"label": "Speed +10%",  "uart_command": "CMD_SPD_UP"},
                        {"label": "Speed -10%",  "uart_command": "CMD_SPD_DN"},
                        {"label": "Reverse",     "uart_command": "CMD_REV"},
                    ],
                }
            ],
        },
    },
    2: {
        "id": 2,
        "name": "Sensor Array",
        "status": "reserved",
        "description": "Multi-sensor data acquisition platform. Main device aggregates readings from temperature, pressure, and proximity sensors over I2C. Control board triggers sampling sequences and configures sensor modes via UART commands.",
        "descriptor": {
            "name": "Sensor Array",
            "description": "Multi-sensor data acquisition over I2C. Control board triggers sampling and configures sensor modes.",
            "main_device": {
                "device_id": "STM32-02",
                "role": "I2C master — aggregates sensor readings",
                "openocd_config_path": "board/stm32g0nucleo.cfg",
                "camera": {"enabled": False, "stream_path": None},
            },
            "control_devices": [
                {
                    "device_id": "STM32-04",
                    "default_elf": "sensor_trigger_v1.elf",
                    "available_elfs": [
                        "sensor_trigger_v1.elf",
                        "sensor_continuous.elf",
                    ],
                    "buttons": [
                        {"label": "Sample once",    "uart_command": "CMD_SAMPLE"},
                        {"label": "Continuous on",  "uart_command": "CMD_CONT_ON"},
                        {"label": "Continuous off", "uart_command": "CMD_CONT_OFF"},
                    ],
                }
            ],
        },
    },
    3: {
        "id": 3,
        "name": "Communication Bus Demo",
        "status": "occupied",
        "description": "Demonstrates CAN bus communication between two STM32 nodes. The main device acts as a master node, while the control board simulates a slave ECU responding to standardized message frames.",
        "descriptor": {
            "name": "Communication Bus Demo",
            "description": "CAN bus communication between two STM32 nodes.",
            "main_device": {
                "device_id": "STM32-01",
                "role": "CAN master node",
                "openocd_config_path": "board/stm32f4discovery.cfg",
                "camera": {"enabled": False, "stream_path": None},
            },
            "control_devices": [
                {
                    "device_id": "STM32-02",
                    "default_elf": "can_slave_v1.elf",
                    "available_elfs": ["can_slave_v1.elf"],
                    "buttons": [
                        {"label": "Send frame", "uart_command": "CMD_SEND"},
                        {"label": "Reset bus",  "uart_command": "CMD_RESET"},
                    ],
                }
            ],
        },
    },
}

_SESSION_CONFIG = {
    "min_duration_minutes": 15,
    "max_duration_minutes": 60,
    "slot_step_minutes": 15,
}


def get_all(session) -> list[dict]:
    return [
        {"id": a["id"], "name": a["name"], "status": a["status"], "description": a["description"]}
        for a in _APPLICATIONS.values()
    ]


def get_by_id(session, app_id: int) -> dict:
    app = _APPLICATIONS.get(app_id)
    if not app:
        raise LookupError(f"Application {app_id} not found")
    return {"id": app["id"], "status": app["status"], "descriptor": app["descriptor"]}


def get_config(session, app_id: int) -> dict:
    if app_id not in _APPLICATIONS:
        raise LookupError(f"Application {app_id} not found")
    return _SESSION_CONFIG
