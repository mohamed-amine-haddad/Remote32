# CLAUDE.md

Guidance for Claude Code when working in this repository.

---

## Project

**Remote32** — web-based remote lab platform. Students upload, flash, and debug
code on real STM32 microcontrollers connected to a Raspberry Pi, from their own
computer. Developed as a Projet de Fin d'Année (PFA).

**Status:** frontend UI prototype done; auth works end-to-end; routers scaffolded (501 placeholders); stub services done + UI pages linked to backend; real services being implemented in parallel. Devices merged into Applications — a device is now an Application with no control boards.

---

## Repository structure
remote32/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── routers/          # auth.py, devices.py, applications.py, bookings.py, application_sessions.py
│   ├── services/         # sessions/, openocd.py, devices.py, raspberrys.py, users.py, auth.py
│   │   └── stub/         # stub implementations used until real services are ready
│   ├── configs/
│   │   ├── devices/      # OpenOCD .cfg files for each physical board
│   │   └── applications/ # application descriptor JSON files
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── hooks/
│       ├── api/
├── nginx/
│   └── remote32.conf
└── .env.example

---

## How to run

**Backend:**
```bash
# From repo root — always activate venv first
venv\Scripts\activate
uvicorn backend.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## Tech stack

**Backend:** FastAPI · SQLModel · SQLite · Alembic · python-jose (JWT) · pyserial · Uvicorn

**Frontend:** React (Vite) · Tailwind CSS v4 · react-router-dom · clsx · react-calendar

**Infrastructure:** nginx (reverse proxy) · OpenOCD (GDB server + STM32 flashing) · Raspberry Pi OS

---

## Tool versions (Windows 11 dev machine)

python 3.11.9 pip 26.0.1
node v20.20.2 npm 10.8.2
git 2.45.1
openocd 0.12.0+dev-00645-g49ef1d010 (STMicroelectronics fork)
tailwindcss 4.2.2 vite 8.0.7

---

## Hardware context

- **Pi hostname:** `retroboy` · **user:** `retroboy69`
- **OpenOCD** runs on the Pi, exposes GDB server on port `3333`, telnet on `4444`
- **STM32CubeIDE** on the developer's PC connects to `retroboy:3333`
- **Serial:** control STM32s communicate via UART over `/dev/ttyUSB0` (or `/dev/ttyACM0`)
- **Camera:** connected to Pi, streamed via nginx MJPEG proxy

---

## Key domain concepts

**Application** — a named lab setup with one **main board** (the target STM32, accessed
via GDB) plus one or more **control boards**. Control boards are flashed automatically
at session start; the user switches `.elf` firmware from a dropdown and sends UART
commands via button panels.

**Device** — an application with **no control boards**: just a target STM32 exposed as
a remote GDB server. Internally a device is stored and handled identically to an
application; the distinction is UI-only (separate browse pages, no control panel in the
session view). This avoids duplicate code for booking, session management, and the
detail/session pages.

**Board** — one physical STM32 connected to the Pi. Tracked in the database because it
carries runtime state (status, openocd_pid) and port assignments (gdb_port, telnet_port,
tcl_port). The `.cfg` files in `configs/devices/` are the OpenOCD configurations for
each board.

**Session** — time-bounded access to an application. One `Session` row in the DB
references an `Application` (by `application_id`). Can be booked in advance (calendar
+ duration) or started immediately (fixed admin-set duration). Conflict prevention is
enforced at the database level and at the session level (async lock).

---

## Auth

JWT issued on login/register, sent as **httpOnly cookie** (not localStorage).
"Remember me" extends cookie `max_age` to 30 days. Two roles: `user` and `admin`.

---

## Conventions

- **Indentation:** 4 spaces everywhere — Python and JavaScript
- **Branch:** `ui/prototype` for frontend work · `main` is stable
- **Commit style:** `feat:` `fix:` `chore:` prefixes
- **Tailwind:** define design tokens in `frontend/src/index.css` under `@theme`.
  No `tailwind.config.js`. Extract class strings into named `const` variables —
  never write long `className` strings inline in JSX
- **No `@apply`** — do not use Tailwind's `@apply` directive
- **Styling:** Neobrutalism — `border-2 border-black`, `shadow-nb` (4px offset, no blur), `rounded-none`, accent color `#FFD200`, navy `#03234B`

---

## What NOT to do

- Do not install or suggest `tailwind.config.js` — the project uses Tailwind v4 CSS-first configuration via `@theme` in `index.css`
- Do not use `@tailwind base/components/utilities` — those are Tailwind v3 syntax
- Do not commit the `venv/` folder, `.env` file, `*.db` files, or `frontend/dist/`
- Do not use `localStorage` or `sessionStorage` for auth — JWT lives in httpOnly cookies
- Do not add architecture-specific code — backend must run identically on Windows 11 (dev) and Raspberry Pi OS (production)
- Do not push to origin.