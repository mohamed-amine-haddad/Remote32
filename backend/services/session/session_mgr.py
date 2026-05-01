# Unified session lifecycle manager.
# Orchestrates OpenOCD, board status, and session records for both device and application sessions.

import sys
sys.path.insert(0, ".")

from datetime import datetime, timedelta
from sqlmodel import Session as DBSession

try:
    from backend.services.config_loader import SessionConfig
    from backend.services.session.session import get_by_id, get_active_by_board, get_active_by_user, get_reserved_by_user, get_time_until_next_reservation, has_overlapping_session, create, update, delete
    from backend.services.devices import update_board
    from backend.services.openocd import is_running, is_port_in_use, launch_openocd, kill_openocd
    from backend.models import Session as SessionRecord
    from backend.database import engine
except ImportError:
    from services.config_loader import SessionConfig
    from services.session.session import get_by_id, get_active_by_board, get_active_by_user, get_reserved_by_user, get_time_until_next_reservation, has_overlapping_session, create, update, delete
    from services.devices import update_board
    from services.openocd import is_running, is_port_in_use, launch_openocd, kill_openocd
    from models import Session as SessionRecord
    from database import engine


def book_session(configs: dict[str, SessionConfig], json_path: str, user_id: int, start_time: datetime, duration_minutes: int, db: DBSession) -> SessionRecord:
    """
    Validates availability and creates a session record with status 'reserved'.
    Does DB checks only — no SSH or hardware interaction.
    Raises RuntimeError if any check fails.

    configs          : all configs loaded at startup (json_path -> SessionConfig)
    json_path        : key identifying which device/application to book
    user_id          : ID of the user making the reservation
    start_time       : when the session should start
    duration_minutes : requested duration (may be capped by next reservation)
    db               : database session
    """
    config = configs.get(json_path)
    if config is None:
        raise RuntimeError(f"Config '{json_path}' not found")

    target_board_cfg = config.target

    # Check if the user already has an active session
    if get_active_by_user(db, user_id):
        raise RuntimeError("You can't book a session when you currently have an active one")
    
    """
    # Check if the user already has a reserved session
    if get_reserved_by_user(db, user_id):
        raise RuntimeError("You can only book one session at a time")
    """

    # Find the closest upcoming reservation for both target and control boards
    time_until_next = get_time_until_next_reservation(db, target_board_cfg.serial_number, start_time)
    if config.is_application:
        control_time = get_time_until_next_reservation(db, config.control.serial_number, start_time)
        if control_time is not None:
            if time_until_next is None or control_time < time_until_next:
                time_until_next = control_time

    # Cap duration to the time before the next reservation (only if > 10 minutes remaining)
    if time_until_next is not None:
        if time_until_next <= timedelta(minutes=10):
            raise RuntimeError(f"Not enough time before next reservation ({int(time_until_next.total_seconds() // 60)} minutes remaining)")
        duration_minutes = min(duration_minutes, int(time_until_next.total_seconds() // 60))

    # Lab hours enforcement (08:00–20:00) — also validated client-side for UX
    start_mins = start_time.hour * 60 + start_time.minute
    end_mins   = start_mins + duration_minutes
    if start_mins < 8 * 60:
        raise RuntimeError("Sessions cannot start before 08:00")
    if end_mins > 20 * 60:
        raise RuntimeError("Session would end after lab closing time (20:00)")

    # Check if the (possibly capped) time slot overlaps with an existing session on the board
    end_time = start_time + timedelta(minutes=duration_minutes)
    if has_overlapping_session(db, target_board_cfg.serial_number, start_time, end_time):
        raise RuntimeError(f"Board '{target_board_cfg.serial_number}' is already booked for that time slot")
    if config.is_application and has_overlapping_session(db, config.control.serial_number, start_time, end_time):
        raise RuntimeError(f"Control board '{config.control.serial_number}' is already booked for that time slot")

    # All checks passed — create the reserved session record
    return create(db, SessionRecord(
        user_id=user_id,
        json_path=json_path,
        target_board_sn=target_board_cfg.serial_number,
        control_board_sn=config.control.serial_number if config.is_application else None,
        start_time=start_time,
        end_time=start_time + timedelta(minutes=duration_minutes),
        status="reserved"
    ))


def activate_reserved_session(session_id: int, configs: dict[str, SessionConfig], db: DBSession) -> int:
    """
    Activates a reserved session: launches OpenOCD and updates statuses.
    Raises RuntimeError if the session is not found, not reserved, or hardware checks fail.
    Returns the GDB port to connect to.

    session_id : ID of the reserved session to activate
    configs    : all configs loaded at startup (json_path -> SessionConfig)
    db         : database session
    """
    record = get_by_id(db, session_id)
    if record.status != "reserved":
        raise RuntimeError(f"Session {session_id} is not in 'reserved' state (current: '{record.status}')")
    if datetime.now() < record.start_time:
        raise RuntimeError(f"Session {session_id} cannot be activated before its start time ({record.start_time})")

    config  = configs[record.json_path]
    target_board_cfg = config.target

    # Real-time hardware checks — target board
    if is_running(target_board_cfg):
        raise RuntimeError(f"Board '{target_board_cfg.serial_number}' is already running")
    if is_port_in_use(target_board_cfg):
        raise RuntimeError(f"GDB port {target_board_cfg.gdb_port} is already in use")

    # Real-time hardware checks — control board (application only)
    if config.is_application:
        if is_running(config.control):
            raise RuntimeError(f"Control board '{config.control.serial_number}' is already running")
        if is_port_in_use(config.control):
            raise RuntimeError(f"GDB port {config.control.gdb_port} is already in use")

    # Launch OpenOCD for target board and update its status
    target_openocd_pid = launch_openocd(target_board_cfg)
    update_board(target_board_cfg.serial_number, {"status": "running", "openocd_pid": target_openocd_pid}, db)

    # Launch OpenOCD for control board and update its status (application only)
    if config.is_application:
        control_openocd_pid = launch_openocd(config.control)
        update_board(config.control.serial_number, {"status": "running", "openocd_pid": control_openocd_pid}, db)

    # Update session status to active
    update(db, session_id, {"status": "active"})    

    return target_board_cfg.gdb_port


def start_session(configs: dict[str, SessionConfig], json_path: str, user_id: int, duration_minutes: int, db: DBSession) -> int:
    """
    Starts a session immediately.
    Books the slot for now, then activates it. Cleans up on activation failure.
    Returns the GDB port to connect to.

    configs          : all configs loaded at startup (json_path -> SessionConfig)
    json_path        : key identifying which device/application to start
    user_id          : ID of the user starting the session
    duration_minutes : requested duration (may be capped by next reservation)
    db               : database session
    """
    record = book_session(configs, json_path, user_id, datetime.now(), duration_minutes, db)
    try:
        return activate_reserved_session(record.id, configs, db)
    except RuntimeError:
        delete(db, record.id)
        raise


def end_session(session_id: int, configs: dict[str, SessionConfig], db: DBSession) -> None:
    """
    Ends an active session: kills OpenOCD and resets board statuses.
    Raises RuntimeError if the session is not found or not active.

    session_id : ID of the active session to end
    configs    : all configs loaded at startup (json_path -> SessionConfig)
    db         : database session
    """
    record = get_by_id(db, session_id)
    if record.status != "active":
        raise RuntimeError(f"Session {session_id} is not active (current: '{record.status}')")

    config = configs[record.json_path]

    # Kill OpenOCD for target board and reset its status
    kill_openocd(config.target)
    update_board(config.target.serial_number, {"status": "idle", "openocd_pid": None}, db)

    # Kill OpenOCD for control board and reset its status (application only)
    if config.is_application:
        kill_openocd(config.control)
        update_board(config.control.serial_number, {"status": "idle", "openocd_pid": None}, db)

    update(db, session_id, {"status": "ended"})


if __name__ == "__main__":
    try:
        from backend.services.config_loader import load_all_configs
        from backend.services.session.session import get_active_by_board
        from backend.database import engine
    except ImportError:
        from services.config_loader import load_all_configs
        from services.session.session import get_active_by_board
        from database import engine

    configs = load_all_configs()
    JSON_PATH = "configs/devices/nucleo_f401re_1.json"
    USER_ID = 2
    """
    # Test 1: start_session
    print("--- Test 1: start_session ---")
    with DBSession(engine) as db:
        try:
            gdb_port = start_session(configs, JSON_PATH, USER_ID, 60, db)
            print(f"PASS — session started, connect to GDB port {gdb_port}")
        except RuntimeError as e:
            print(f"FAIL — {e}")
    
    # Test 2: start_session — board already in use
    print("\n--- Test 2: start_session (board already in use) ---")
    with DBSession(engine) as db:
        try:
            start_session(configs, JSON_PATH, USER_ID, 60, db)
            print("FAIL — should have raised RuntimeError")
        except RuntimeError as e:
            print(f"PASS — correctly rejected: {e}")

    # Test 3: end_session
    print("\n--- Test 3: end_session ---")
    with DBSession(engine) as db:
        active = get_active_by_board(db, configs[JSON_PATH].target.serial_number)
    if active:
        with DBSession(engine) as db:
            try:
                end_session(active.id, configs, db)
                print(f"PASS — session {active.id} ended")
            except RuntimeError as e:
                print(f"FAIL — {e}")
    else:
        print("SKIP — no active session found")

    # Test 4: end_session — already ended
    print("\n--- Test 4: end_session (already ended) ---")
    if active:
        with DBSession(engine) as db:
            try:
                end_session(active.id, configs, db)
                print("FAIL — should have raised RuntimeError")
            except RuntimeError as e:
                print(f"PASS — correctly rejected: {e}")
    else:
        print("SKIP — no session to test with")
    """

    with DBSession(engine) as db:
        end_session(2, configs, db)