from datetime import datetime
from sqlmodel import Session as DBSession, select

try:
    from backend.services.config_loader import SessionConfig, load_config
    from backend.services.session.session_mgr import book_session, activate_reserved_session, end_session as _end_session
    from backend.services.session.session import get_by_id as get_session_by_id, delete
    from backend.services.openocd import flash_firmware
    from backend.services.serial_service import send_command as _send_serial_command
    from backend.services.uart import start_reader as _uart_start, stop_reader as _uart_stop, get_messages as _uart_messages, send_text as _uart_send_text
    from backend.models import Session as SessionRecord
except ImportError:
    from services.config_loader import SessionConfig, load_config
    from services.session.session_mgr import book_session, activate_reserved_session, end_session as _end_session
    from services.session.session import get_by_id as get_session_by_id, delete
    from services.openocd import flash_firmware
    from services.serial_service import send_command as _send_serial_command
    from services.uart import start_reader as _uart_start, stop_reader as _uart_stop, get_messages as _uart_messages, send_text as _uart_send_text
    from models import Session as SessionRecord

DEFAULT_DURATION_MINUTES = 60


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _fmt_time_left(end_time: datetime) -> str:
    secs = max(0, int((end_time - datetime.now()).total_seconds()))
    return f"{secs // 60:02d}:{secs % 60:02d}"


def _build_control_devices(config: SessionConfig) -> list[dict]:
    if not config.is_application:
        return []
    ctrl = config.control
    return [{
        "device_id":   ctrl.serial_number,
        "label":       config.name,
        "default_elf": ctrl.firmwares[0].bin_file if ctrl.firmwares else "",
        "available_elfs": [
            {
                "filename": fw.bin_file,
                "name":     fw.name,
                "buttons":  [{"label": b.label, "uart_command": b.command} for b in fw.buttons],
            }
            for fw in ctrl.firmwares
        ],
    }]


def _build_response(record: SessionRecord, configs: dict[str, SessionConfig]) -> dict:
    config = configs[record.json_path]
    return {
        "id":              record.id,
        "app_name":        config.name,
        "status":          record.status,
        "started_at":      _fmt_time(record.start_time),
        "ends_at":         _fmt_time(record.end_time),
        "time_left":       _fmt_time_left(record.end_time),
        "gdb_host":        config.target.gdb_external_host,
        "gdb_port":        config.target.gdb_external_port,
        "control_devices": _build_control_devices(config),
    }


def get_by_id(db: DBSession, session_id: int, user_id: int, configs: dict[str, SessionConfig]) -> dict:
    record = get_session_by_id(db, session_id)
    if record.user_id != user_id:
        raise RuntimeError(f"Session {session_id} not found")
    if record.json_path not in configs:
        raise RuntimeError(f"Config for session {session_id} not found")
    return _build_response(record, configs)


def start(configs: dict[str, SessionConfig], db: DBSession, json_path: str, user_id: int, duration_minutes: int = DEFAULT_DURATION_MINUTES) -> dict:
    record = book_session(configs, json_path, user_id, datetime.now(), duration_minutes, db)
    record_id = record.id
    try:
        activate_reserved_session(record_id, configs, db)
    except Exception:
        delete(db, record_id)
        raise
    fresh = get_session_by_id(db, record_id)
    config = configs[fresh.json_path]
    if config.target.serial_port:
        _uart_start(record_id, config.target, 'target')
    if config.is_application and config.control.serial_port:
        _uart_start(record_id, config.control, 'control')
    return _build_response(fresh, configs)


def get_my_reservation(db: DBSession, json_path: str, user_id: int) -> dict | None:
    now = datetime.now()
    record = db.exec(
        select(SessionRecord)
        .where(SessionRecord.user_id == user_id)
        .where(SessionRecord.json_path == json_path)
        .where(SessionRecord.status == "reserved")
        .where(SessionRecord.end_time > now)
        .order_by(SessionRecord.start_time)
    ).first()
    if record is None:
        return None
    return {
        "session_id":  record.id,
        "start_time":  record.start_time.isoformat(),
        "end_time":    record.end_time.isoformat(),
        "activatable": now >= record.start_time,
    }


def activate(db: DBSession, session_id: int, user_id: int, configs: dict[str, SessionConfig]) -> dict:
    record = get_session_by_id(db, session_id)
    if record.user_id != user_id:
        raise RuntimeError(f"Session {session_id} not found")
    if record.json_path not in configs:
        raise RuntimeError(f"Config for session {session_id} not found")
    activate_reserved_session(session_id, configs, db)
    fresh = get_session_by_id(db, session_id)
    config = configs[fresh.json_path]
    if config.target.serial_port:
        _uart_start(session_id, config.target, 'target')
    if config.is_application and config.control.serial_port:
        _uart_start(session_id, config.control, 'control')
    return _build_response(fresh, configs)


def end(db: DBSession, configs: dict[str, SessionConfig], session_id: int, user_id: int) -> str:
    record = get_session_by_id(db, session_id)
    if record.user_id != user_id:
        raise RuntimeError(f"Session {session_id} not found")
    _end_session(session_id, configs, db)
    _uart_stop(session_id)
    return "Session ended"


def flash(db: DBSession, session_id: int, elf_filename: str, configs: dict[str, SessionConfig]) -> str:
    record = get_session_by_id(db, session_id)
    if record.json_path not in configs:
        raise RuntimeError(f"Config for session {session_id} not found")
    config = configs[record.json_path]
    if not config.is_application:
        raise RuntimeError(f"Session {session_id} has no control board")
    flash_firmware(config.control, elf_filename)
    return f"Flashed {elf_filename}"


def send_command(db: DBSession, session_id: int, uart_command: str, configs: dict[str, SessionConfig]) -> str:
    record = get_session_by_id(db, session_id)
    if record.json_path not in configs:
        raise RuntimeError(f"Config for session {session_id} not found")
    config = configs[record.json_path]
    if not config.is_application:
        raise RuntimeError(f"Session {session_id} has no control board")
    _send_serial_command(config.control, uart_command)
    return f"Command sent: {uart_command}"


def get_uart_messages(db: DBSession, session_id: int, since_id: int = 0) -> dict:
    get_session_by_id(db, session_id)
    return _uart_messages(session_id, since_id)


def uart_send(db: DBSession, session_id: int, text: str, configs: dict[str, SessionConfig]) -> str:
    record = get_session_by_id(db, session_id)
    if record.json_path not in configs:
        raise RuntimeError(f"Config for session {session_id} not found")
    config = configs[record.json_path]
    if not config.target.serial_port:
        raise RuntimeError(f"Session {session_id} has no UART port configured on the target board")
    _uart_send_text(session_id, config.target, text)
    return f"Sent: {text}"


def camera_stream(db: DBSession, session_id: int, user_id: int, configs: dict[str, SessionConfig]) -> str:
    record = get_session_by_id(db, session_id)
    if record.user_id != user_id:
        raise RuntimeError(f"Session {session_id} not found")
    if record.status != "active":
        raise RuntimeError(f"Session {session_id} is not active")
    config = configs[record.json_path]
    if config.camera is None:
        raise RuntimeError(f"No camera configured for '{config.name}'")
    from backend.services.camera import open_camera
    return open_camera(config)
