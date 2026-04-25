# STUB — replace body of each function with real DB/config queries when
# backend/services/applications.py is ready. Change the import in routers/applications.py
# from backend.services.stub.applications to backend.services.applications.

_APPLICATIONS = {
    # ── Full lab applications (have control boards) ───────────────────────────
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

    # ── Direct-access applications (no control boards — formerly "devices") ───
    4: {
        "id": 4,
        "name": "STM32-01 Direct Access",
        "status": "free",
        "description": "STM32F4 Discovery board. General-purpose device suitable for GPIO, timers, UART, SPI and I2C experiments. Connected via SWD.",
        "descriptor": {
            "name": "STM32-01 Direct Access",
            "description": "General-purpose STM32F4 Discovery. Suitable for most beginner and intermediate labs.",
            "main_device": {
                "device_id": "STM32-01",
                "role": "Direct GDB access",
                "openocd_config_path": "board/stm32f4discovery.cfg",
                "camera": {"enabled": True, "stream_path": "/stream/device1"},
            },
            "control_devices": [],
        },
    },
    5: {
        "id": 5,
        "name": "STM32-02 Direct Access",
        "status": "occupied",
        "description": "STM32G0 Nucleo board. Ideal for low-power experiments and ADC/DAC signal processing labs. Full debug access via SWD.",
        "descriptor": {
            "name": "STM32-02 Direct Access",
            "description": "STM32G0 Nucleo. Ideal for low-power and ADC/DAC experiments.",
            "main_device": {
                "device_id": "STM32-02",
                "role": "Direct GDB access",
                "openocd_config_path": "board/stm32g0nucleo.cfg",
                "camera": {"enabled": True, "stream_path": "/stream/device2"},
            },
            "control_devices": [],
        },
    },
    6: {
        "id": 6,
        "name": "STM32-03 Direct Access",
        "status": "reserved",
        "description": "STM32H7 evaluation board. High-performance board with FPU support. Used for DSP and real-time control labs requiring floating-point operations.",
        "descriptor": {
            "name": "STM32-03 Direct Access",
            "description": "High-performance STM32H7. For DSP and real-time control with FPU.",
            "main_device": {
                "device_id": "STM32-03",
                "role": "Direct GDB access",
                "openocd_config_path": "board/stm32h7.cfg",
                "camera": {"enabled": False, "stream_path": None},
            },
            "control_devices": [],
        },
    },
    7: {
        "id": 7,
        "name": "STM32-04 Direct Access",
        "status": "free",
        "description": "STM32L4 Nucleo board configured for ultra-low-power mode experiments. Suitable for battery-powered system prototyping.",
        "descriptor": {
            "name": "STM32-04 Direct Access",
            "description": "Ultra-low-power STM32L4. Suitable for battery-powered system prototyping.",
            "main_device": {
                "device_id": "STM32-04",
                "role": "Direct GDB access",
                "openocd_config_path": "board/stm32l4nucleo.cfg",
                "camera": {"enabled": False, "stream_path": None},
            },
            "control_devices": [],
        },
    },
}

_SESSION_CONFIG = {
    "min_duration_minutes": 15,
    "max_duration_minutes": 60,
    "slot_step_minutes": 15,
}

# IDs of entries that are full applications (have control boards).
# Entries with no control boards are exposed via /api/devices instead.
_APPLICATION_IDS = {1, 2, 3}


def get_all(session) -> list[dict]:
    return [
        {"id": a["id"], "name": a["name"], "status": a["status"], "description": a["description"]}
        for a in _APPLICATIONS.values()
        if a["id"] in _APPLICATION_IDS
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
