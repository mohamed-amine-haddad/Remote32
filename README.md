# Remote32

A web-based remote lab platform that lets students flash, debug, and interact with real STM32 microcontrollers over the network — from any computer, using STM32CubeIDE as if the board were on their desk.

Developed as a *Projet de Fin d'Année* (PFA).

---

## What it does

- **Remote debugging** — exposes each STM32 as a GDB server via OpenOCD. Students connect STM32CubeIDE to an IP:port and debug normally, no physical access needed.
- **Remote control** — for multi-board "Applications", a live button panel sends UART commands to control devices. Firmware can be switched mid-session from a dropdown.
- **Booking system** — students can start an immediate session or reserve a future time slot. Conflict prevention is enforced at the database level.
- **Live camera** — a camera feed of the physical lab bench streams alongside the debug session.

---

## Architecture

```
Browser (STM32CubeIDE + React UI)
        │
        ▼
    nginx (reverse proxy)
    ├── /           → React static build
    ├── /api        → FastAPI backend
    └── /stream     → Camera MJPEG stream
        │
        ▼
    FastAPI (Python)
    ├── Auth (JWT / httpOnly cookies)
    ├── Device & Application management
    ├── Session & Booking system
    └── OpenOCD + pyserial control
        │
        ▼
    Raspberry Pi
    ├── OpenOCD → GDB server (port 3333)
    └── pyserial → UART to control STM32s
        │
        ▼
    STM32 boards (SWD/JTAG via ST-Link)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React · Vite · Tailwind CSS v4 · react-router-dom |
| Backend | FastAPI · SQLModel · SQLite · Alembic · python-jose · pyserial · Uvicorn |
| Infrastructure | nginx · OpenOCD · Raspberry Pi OS |

---

## Prerequisites

Install these on your development machine before anything else.

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | Must match Pi deployment version |
| Node.js | 20 LTS | npm is included |
| Git | Any recent | Run `git config --global core.autocrlf input` on Windows |
| OpenOCD | 0.12.0+ | Use the [STMicroelectronics fork](https://github.com/STMicroelectronics/OpenOCD) |
| STM32CubeIDE | 1.18+ | Used to connect to the remote GDB server |

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Remote32.git
cd Remote32
```

### 2. Backend setup

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Raspberry Pi
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

Copy the environment file and fill in the values:

```bash
cp .env.example .env
```

Run the backend:

```bash
uvicorn backend.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`.
Interactive API docs are available at `http://127.0.0.1:8000/docs`.

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The UI is now running at `http://localhost:5173`.

---

## Environment variables

Copy `.env.example` to `.env` and configure:

```env
# Security — change this to a long random string in production
SECRET_KEY=your-secret-key-here

# JWT cookie lifetime in seconds (default: 30 days)
ACCESS_TOKEN_EXPIRE_SECONDS=2592000

# Session policy defaults (admin can override via dashboard)
SESSION_MIN_MINUTES=15
SESSION_MAX_MINUTES=60
SESSION_FIXED_MINUTES=30
```

---

## Hardware setup (Raspberry Pi)

The Pi acts as the gateway between the network and the physical STM32 boards.

**Pi hostname:** `retroboy` · **user:** `retroboy69`

### Install dependencies on the Pi

```bash
sudo apt update
sudo apt install python3.11 python3-pip nginx openocd
pip install uvicorn fastapi sqlmodel python-jose pyserial python-dotenv alembic
```

### OpenOCD configuration

The file `~/openocd.cfg` on the Pi should contain:

```
source [find interface/stlink.cfg]
source [find target/stm32f4x.cfg]
```

Adjust the target config to match your STM32 chip family.

Start OpenOCD manually to verify the connection:

```bash
openocd -f ~/openocd.cfg
```

OpenOCD binds the GDB server on port `3333` and a telnet interface on port `4444`.

### Connect STM32CubeIDE

In STM32CubeIDE: **Debug Configurations → GDB Hardware Debugging → Remote Target**

Set the host to `retroboy` and port to `3333`. Flash and debug normally.

---

## Project structure

```
remote32/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── models.py                # SQLModel models (User, Device, Application, Booking, Session)
│   ├── routers/
│   │   ├── auth.py              # POST /auth/register, /auth/login, /auth/logout
│   │   ├── devices.py           # GET/POST/PATCH/DELETE /devices
│   │   ├── applications.py      # GET/POST/PATCH/DELETE /applications
│   │   ├── bookings.py          # Reservation calendar and CRUD
│   │   └── admin.py             # Admin dashboard endpoints
│   ├── services/
│   │   ├── session_manager.py   # Device locking and duration enforcement
│   │   ├── openocd_manager.py   # Start/stop OpenOCD, flash .elf files
│   │   ├── serial_manager.py    # UART command sending via pyserial
│   │   └── config_loader.py     # Parse hardware and application JSON descriptors
│   ├── configs/
│   │   ├── devices/             # Hardware descriptor JSON — one file per device
│   │   └── applications/        # Application descriptor JSON — one file per application
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/               # One file per route
│       ├── components/          # Reusable UI components
│       ├── hooks/               # Custom React hooks
│       ├── api/                 # Axios/fetch wrappers for FastAPI
│
├── nginx/
│   └── remote32.conf            # nginx site config
│
├── .env.example                 # Environment variable template
├── CLAUDE.md                    # Context file for Claude Code
└── README.md
```

---

## Configuration files

Two types of JSON descriptors are managed through the admin dashboard.

**Hardware descriptor** — describes one physical STM32 board:

```json
{
    "name": "STM32-01",
    "type": "STM32F4 Discovery",
    "openocd_config_path": "board/stm32f4discovery.cfg",
    "serial_port": "/dev/ttyUSB0",
    "swd_interface": "stlink",
    "camera": {
        "enabled": true,
        "stream_path": "/stream/device1"
    }
}
```

**Application descriptor** — groups a main device and one or more control devices:

```json
{
    "name": "Motor Control Lab",
    "main_device": {
        "device_id": "STM32-01",
        "openocd_config_path": "board/stm32f4discovery.cfg"
    },
    "control_devices": [
        {
            "device_id": "STM32-03",
            "default_elf": "motor_v1.elf",
            "available_elfs": ["motor_v1.elf", "motor_v2.elf"],
            "buttons": [
                { "label": "Start", "uart_command": "CMD_START" },
                { "label": "Stop",  "uart_command": "CMD_STOP"  }
            ]
        }
    ]
}
```

---

## User roles

**Regular user** — register, log in, browse devices and applications, start or book sessions, manage their own reservations.

**Admin** — everything above plus: add/edit/remove devices and applications, upload `.elf` firmware files, configure session duration policy (minimum, maximum, fixed), cancel any reservation.

---

## Development workflow

### Branches

| Branch | Purpose |
|---|---|
| `main` | Stable — only merged, tested code |
| `ui/prototype` | Frontend prototype — current active branch |

### Running both servers simultaneously

Open two terminals in VS Code.

**Terminal 1 — backend:**
```bash
venv\Scripts\activate
uvicorn backend.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

### Database migrations

```bash
# After changing models.py, generate a migration
alembic revision --autogenerate -m "describe the change"

# Apply all pending migrations
alembic upgrade head
```

---

## Deployment (Raspberry Pi)

```bash
# 1. Build the frontend
cd frontend
npm run build
# Outputs to frontend/dist/

# 2. Copy dist/ to nginx serving directory
sudo cp -r dist/ /var/www/remote32/

# 3. Install nginx config
sudo cp nginx/remote32.conf /etc/nginx/sites-available/remote32
sudo ln -s /etc/nginx/sites-available/remote32 /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 4. Run the backend with a process manager
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

For public access, configure either:
- **No-IP / DynDNS** — stable hostname, requires router port forwarding. Preferred for lab use.
- **ngrok** — no router access needed, URL changes on every restart. Use for early demos.

---

## Conventions

- **Indentation:** 4 spaces — Python and JavaScript
- **Commits:** `feat:` `fix:` `chore:` prefixes
- **Tailwind:** design tokens in `frontend/src/index.css` under `@theme`. No `tailwind.config.js`.
- **Class strings:** extracted into named `const` variables — never inline long `className` strings in JSX
- **Auth:** JWT in httpOnly cookies — never `localStorage`
- **Strings:** always use `t()` — never hardcode user-facing text in JSX

---

## Known constraints

- Total backend RAM must stay under 512 MB to fit on the Raspberry Pi 2 (1 GB total)
- No built-in code editor — students write and compile in STM32CubeIDE on their own machines
- No architecture-specific code — backend must run identically on Windows 11 (dev) and Raspberry Pi OS (production)
- Expected peak load: 3–10 concurrent users

---

## License

Academic project — all rights reserved.