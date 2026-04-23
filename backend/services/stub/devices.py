# STUB — replace body of each function with real DB/config queries when
# backend/services/devices.py is ready. Change the import in routers/devices.py
# from backend.services.stub.devices to backend.services.devices.

_DEVICES = {
    1: {
        "id": 1,
        "name": "STM32-01",
        "status": "free",
        "description": "STM32F4 Discovery board. General-purpose device suitable for GPIO, timers, UART, SPI and I2C experiments. Connected via SWD.",
        "descriptor": {
            "name": "STM32-01",
            "type": "STM32F4 Discovery",
            "openocd_config_path": "board/stm32f4discovery.cfg",
            "serial_port": "/dev/ttyUSB0",
            "swd_interface": "stlink",
            "camera": {
                "enabled": True,
                "stream_path": "/stream/device1",
                "resolution": "1280x720",
            },
            "capabilities": ["GPIO", "UART", "SPI", "I2C", "PWM", "ADC"],
            "notes": "General-purpose board. Suitable for most beginner and intermediate labs.",
        },
    },
    2: {
        "id": 2,
        "name": "STM32-02",
        "status": "occupied",
        "description": "STM32G0 Nucleo board. Ideal for low-power experiments and ADC/DAC signal processing labs. Full debug access via SWD.",
        "descriptor": {
            "name": "STM32-02",
            "type": "STM32G0 Nucleo",
            "openocd_config_path": "board/stm32g0nucleo.cfg",
            "serial_port": "/dev/ttyUSB1",
            "swd_interface": "stlink",
            "camera": {
                "enabled": True,
                "stream_path": "/stream/device2",
                "resolution": "640x480",
            },
            "capabilities": ["GPIO", "UART", "ADC", "DAC", "Low-power modes"],
            "notes": None,
        },
    },
    3: {
        "id": 3,
        "name": "STM32-03",
        "status": "reserved",
        "description": "STM32H7 evaluation board. High-performance board with FPU support. Used for DSP and real-time control labs requiring floating-point operations.",
        "descriptor": {
            "name": "STM32-03",
            "type": "STM32H7 Eval",
            "openocd_config_path": "board/stm32h7.cfg",
            "serial_port": "/dev/ttyUSB2",
            "swd_interface": "stlink",
            "camera": {"enabled": False, "stream_path": None, "resolution": None},
            "capabilities": ["GPIO", "UART", "SPI", "I2C", "FPU", "DMA"],
            "notes": None,
        },
    },
    4: {
        "id": 4,
        "name": "STM32-04",
        "status": "free",
        "description": "STM32L4 Nucleo board configured for ultra-low-power mode experiments. Suitable for battery-powered system prototyping.",
        "descriptor": {
            "name": "STM32-04",
            "type": "STM32L4 Nucleo",
            "openocd_config_path": "board/stm32l4nucleo.cfg",
            "serial_port": "/dev/ttyUSB3",
            "swd_interface": "stlink",
            "camera": {"enabled": False, "stream_path": None, "resolution": None},
            "capabilities": ["GPIO", "UART", "ADC", "Low-power modes", "RTC"],
            "notes": "Ultra-low-power board. Suitable for battery-powered system prototyping.",
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
        {"id": d["id"], "name": d["name"], "status": d["status"], "description": d["description"]}
        for d in _DEVICES.values()
    ]


def get_by_id(session, device_id: int) -> dict:
    device = _DEVICES.get(device_id)
    if not device:
        raise LookupError(f"Device {device_id} not found")
    return {"id": device["id"], "status": device["status"], "descriptor": device["descriptor"]}


def get_config(session, device_id: int) -> dict:
    if device_id not in _DEVICES:
        raise LookupError(f"Device {device_id} not found")
    return _SESSION_CONFIG
