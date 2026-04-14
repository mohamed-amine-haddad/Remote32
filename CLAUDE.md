# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Remote32** is a remote device management and debugging system targeting STM32 microcontrollers. It allows developers to manage, flash, and debug STM32 boards remotely over the network — from any PC — without physical access to the hardware. The project is developed on VS Code on Windows 11 laptop. It will be deployed on Raspberry Pi. The Developed as a Projet de Fin d'Année (PFA).

The system consists of three layers:
- **Embedded layer**: STM32 boards connected to a Raspberry Pi running OpenOCD, acting as the debug probe gateway
- **Backend layer**: FastAPI server handling device management, serial communication, and bridging the embedded layer to the web
- **Frontend layer**: React web UI for monitoring and managing connected devices

The project is currently in its early stage.

---

## Core concepts
- **Device**: A Device is a single STM32 microcontroller accessible through the platform. It is exposed as a GDB server via OpenOCD. The platform provides the user with the IP address and port number to enter in STM32CubeIDE (Debug Configurations → GDB Hardware Debugging → Remote Target). From there the user can compile, flash, and debug code normally. The live camera feed is accessible in the web UI simultaneously.
- **Application**: An Application is a group of two or more STM32 devices: one main device and one or more control devices. The system is designed to be extensible to multiple control devices, though in practice there is usually only one.
Main device — works exactly like a Device (remote GDB server, same IDE workflow, same camera access).
Control devices — each control device has a set of pre-loaded .elf binary files. Their behaviour:
•	At session start : the Pi automatically flashes the default .elf onto each control STM32 using OpenOCD.
•	During the session: the user can switch the active .elf from a dropdown list in the UI. Switching causes the Pi to reflash the control STM32 via OpenOCD. The button panel regenerates to match the new .elf.
•	Button commands: each .elf has a corresponding button panel defined in the JSON config. Each button is tied to a UART command string. When pressed, the React frontend sends a request to the FastAPI backend, which forwards the command over serial (pyserial) to the control STM32 via /dev/ttyUSB0 (or equivalent). The running firmware listens via UART and executes the corresponding action. Every .elf intended as control firmware must implement UART command handling, and the JSON config must accurately describe the commands it accepts.

## User roles
- **Regular user**:
•	Register and log in.
•	Browse the list of Devices and Applications (publicly visible without login).
•	View the detail page of a Device or Application.
•	Start an immediate session or book a future time slot (requires authentication).
•	View and manage their own reservations.
- **Admin**:
•	All regular user capabilities plus an admin dashboard.
•	Add, edit, or remove Devices and Applications (including .elf files and JSON config).
•	Set session duration policy: minimum, maximum, and fixed duration for unbooked sessions.
•	Cancel any existing reservation.

## Session and booking system
- **Booking a session**:
•	A calendar shows all free time slots.
•	The user selects a start time and a duration between an admin-configured minimum (e.g. 15 min) and maximum (e.g. 1 hour).
•	The reservation is saved immediately and the slot is blocked, preventing any conflicting booking or immediate session on the same resource.
- **Starting an immediate (unbooked) session**:
•	If a resource is currently free, the user can start immediately.
•	Duration is a fixed value set by the admin (e.g. 30 min). No calendar choice.
•	The time slot is blocked immediately to prevent conflicts.
- **Ending a session**:
•	Ends automatically when the allocated time expires.
•	The user can end early at any time via an "End session" button.
- **Conflict prevention**:
•	At the database level: overlapping reservations on the same resource are rejected with a constraint.
•	At the session level: an async lock prevents two concurrent immediate sessions on the same device.
•	Both enforced server-side regardless of UI state.

## Key user flows
- **Landing page (unauthenticated)**: Options to log in, register, browse Devices, browse Applications. A profile page requires login.
- **Browsing**: List page with device/application cards showing name, description, and current status (free / occupied / reserved). Clicking opens the detail page.
- **Booking**: User opens the booking calendar, picks a free slot, sets duration within the allowed range, confirms. Slot is immediately blocked.
- **Device session**: Platform shows the GDB server IP and port. User connects STM32CubeIDE and works normally. Camera stream is visible in the web UI.
- **Application session**: Same as device session for the main device. Additionally, a dynamically generated button panel appears for each control device. The user can press buttons (sends UART commands) or switch the active .elf (triggers reflash). Camera stream available.
- **Profile**: Show name and e-mail. Shows total time spent in a session. Reservation management with all the user reservations and the option to cancel a reservation.


## Embedded Systems Layer (Hardware Side)

> **Context for Claude Code:** This layer lives outside the repository but is tightly coupled to the backend. Understanding it is essential for working on device routers, services, and any GDB/OpenOCD integration code.

### Hardware Setup

- **Target MCU**: STM32 Nucleo series
- **Debug probe**: ST-Link v2 connected to the Raspberry Pi via USB
- **Host gateway**: Raspberry Pi (hostname: `retroboy`, user: `retroboy69`)
- **Developer machine**: Windows PC running STM32CubeIDE v1.18
- **Server**: Raspberry Pi 2 Model B v1.1, 1 GB RAM
- **Camera**: Connected to the Pi.
- **Portability**: Deployment must work equally on newer Pi models (3B, 4, 5) with no architecture-specific code

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

The frontend is intended to provide:
- A device dashboard showing connected STM32 boards and their status
- Controls to trigger remote actions (flash, reset, start/stop debug session)
- Log streaming for OpenOCD and serial output

- **Art Direction** :
Responsive, Neobrutalist UI — bold borders, offset shadows, strong typography via Tailwind.
Check Remote32/frontend/pages and Remote32/frontend/components to see what has been done. (currently just a prototype) 

- **VITE**: in Remote32/frontend I ran npm create vite@latest . -- --template react 
npm install react-router-dom
npm install -D tailwindcss @tailwindcss/vite
tailwindcss@4.2.2
vite@8.0.7
---

## Architecture
- **Reverse proxy**: nginx — serves React static build, proxies /api to FastAPI, proxies camera stream
- **Public access**: No-IP / DynDNS (free hostname + router port forwarding) — preferred. ngrok (free tunnel) as fallback. Decision to be finalised before deployment

## Expected scale
•	3–10 concurrent users at peak (small class).
•	Correctness and conflict-avoidance are the priority over throughput.
•	Total application RAM usage must stay well under 512 MB to leave headroom on the 1 GB Pi.

## Non-functional requirements
•	Responsive, Neobrutalist UI — bold borders, offset shadows, strong typography via Tailwind.
•	English UI.
•	Lightweight backend — FastAPI + SQLite keeps Pi RAM usage well under 512 MB if possible.
•	No built-in code editor or code storage. Users write and compile in STM32CubeIDE on their own machines.
•	Developed and tested on Windows 11, deployed to Raspberry Pi OS (Debian-based). No architecture-specific code.

## Windows 11 Tools --version
python --version
Python 3.11.9
pip --version
pip 26.0.1 
node --version
v20.20.2
npm --version
10.8.2
git --version
git version 2.45.1.windows.1
openocd --version
Open On-Chip Debugger 0.12.0+dev-00645-g49ef1d010 (2026-04-14-20:18) [https://github.com/STMicroelectronics/OpenOCD]

## Repository Structure
Always check the whole structure. Check the project tree to know the files and folder structure.
Check the version of the tools and node mudules.

## Conventions
tabulation : 4 spaces
make sure naming conventions are followed.
