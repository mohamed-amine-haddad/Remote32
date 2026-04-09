# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Remote32** is a remote device management and debugging system targeting STM32 microcontrollers. It allows developers to manage, flash, and debug STM32 boards remotely over the network — from any PC — without physical access to the hardware.

The system consists of three layers:
- **Embedded layer**: STM32 boards connected to a Raspberry Pi running OpenOCD, acting as the debug probe gateway
- **Backend layer**: FastAPI server handling device management, serial communication, and bridging the embedded layer to the web
- **Frontend layer**: React web UI for monitoring and managing connected devices

The project is currently in early scaffold stage.

---

## Embedded Systems Layer (Hardware Side)

> **Context for Claude Code:** This layer lives outside the repository but is tightly coupled to the backend. Understanding it is essential for working on device routers, services, and any GDB/OpenOCD integration code.

### Hardware Setup

- **Target MCU**: STM32 Nucleo series
- **Debug probe**: ST-Link v2 connected to the Raspberry Pi via USB
- **Host gateway**: Raspberry Pi (hostname: `retroboy`, user: `retroboy69`)
- **Developer machine**: Windows PC running STM32CubeIDE v1.18

### Software Stack on the Raspberry Pi

- **OpenOCD**: Exposes a GDB server on port `3333` and a telnet interface on port `4444`
- **GDB client**: `arm-none-eabi-gdb` (also bundled inside STM32CubeIDE's plugins folder on the PC side)
- **OpenOCD config**: `~/openocd.cfg` on the Raspberry Pi

### OpenOCD Configuration Notes

The `openocd.cfg` uses:
- `source [find interface/stlink-v2.cfg]` (via a shim, since newer OpenOCD versions use `stlink.cfg`)
- `source [find target/stm32xxx.cfg]` — **not** `stm32f1x.cfg`


### Remote Debugging Workflow

1. Start OpenOCD on the Pi: `openocd -f ~/openocd.cfg`
2. OpenOCD binds GDB server on `retroboy:3333`
3. Developer connects via STM32CubeIDE (mode: **Connect to remote GDB server**, target: `retroboy:3333`) or manually via `arm-none-eabi-gdb.exe` with `target remote retroboy:3333`
4. Flash and debug the STM32 remotely over the network

### Backend Integration Points

The backend communicates with the Raspberry Pi to:
- Trigger or restart OpenOCD sessions
- Relay GDB server availability status to the frontend
- (Future) stream OpenOCD telnet output for live device status

---

## Backend

**Stack:** FastAPI, SQLModel (ORM over SQLAlchemy), Alembic (migrations), PySerial (serial device communication), python-jose (JWT auth), Pydantic v2, Uvicorn.

**Entry point:** `backend/main.py`

**Run the backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Intended structure:**
- `routers/` — FastAPI routers, split by domain (`applications/`, `devices/`)
- `services/` — Business logic layer
- `configs/applications/` and `configs/devices/` — Static or runtime config files per domain

### Device Domain Notes

The `devices` domain maps directly to physical STM32 boards connected through the Raspberry Pi gateway. Each device record should track:
- Connection status (is OpenOCD running and GDB port reachable?)
- Target chip family (e.g., `stm32f4`)
- Gateway host (e.g., `retroboy`) and GDB port (default `3333`)
- ST-Link probe identifier if multiple probes are connected

PySerial is used for any UART/serial communication with the STM32 (e.g., debug output over USART). Serial port paths on the Pi follow the pattern `/dev/ttyUSB0` or `/dev/ttyACM0`.

---

## Frontend

**Structure scaffold:** `src/` contains `api/`, `components/`, `hooks/`, `pages/`, `i18n/` — no framework config file exists yet (no `package.json`).

The frontend is intended to provide:
- A device dashboard showing connected STM32 boards and their status
- Controls to trigger remote actions (flash, reset, start/stop debug session)
- Log streaming for OpenOCD and serial output

---

## Architecture