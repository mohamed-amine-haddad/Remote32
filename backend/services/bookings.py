from datetime import datetime
from sqlmodel import Session, select

try:
    from backend.services.config_loader import SessionConfig
    from backend.services.session.session_mgr import book_session
    from backend.models import Session as SessionRecord
except ImportError:
    from services.config_loader import SessionConfig
    from services.session.session_mgr import book_session
    from models import Session as SessionRecord


def _record_to_booking(record: SessionRecord) -> dict:
    return {
        "date":   record.start_time.strftime("%Y-%m-%d"),
        "start":  record.start_time.strftime("%H:%M"),
        "end":    record.end_time.strftime("%H:%M"),
        "status": "occupied" if record.status == "active" else "reserved",
    }


def get_by_resource(configs: dict, db: Session, json_path: str) -> list[dict]:
    config = configs.get(json_path)
    if config is None:
        raise RuntimeError(f"Config '{json_path}' not found")

    sns = [config.target.serial_number]
    if config.is_application:
        sns.append(config.control.serial_number)

    records = db.exec(
        select(SessionRecord)
        .where(
            (SessionRecord.target_board_sn.in_(sns)) |
            (SessionRecord.control_board_sn.in_(sns))
        )
        .where(SessionRecord.status.in_(["reserved", "active"]))
    ).all()
    return [_record_to_booking(r) for r in records]


def create(
    configs: dict[str, SessionConfig],
    db: Session,
    user_id: int,
    json_path: str,
    start_time: datetime,
    duration_minutes: int,
) -> dict:
    record = book_session(configs, json_path, user_id, start_time, duration_minutes, db)
    return _record_to_booking(record)
