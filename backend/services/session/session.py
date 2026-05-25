# Unified session CRUD — covers both device sessions (no control board) and application sessions.
# "Session" clashes with SQLModel's DB session, so the model is aliased as SessionRecord here.

import sys
sys.path.insert(0, ".")

from datetime import datetime, timedelta
from sqlmodel import Session as DBSession, select

try:
    from backend.models import Session as SessionRecord
except ImportError:
    from models import Session as SessionRecord


def get_all(db: DBSession) -> list[SessionRecord]:
    return db.exec(select(SessionRecord)).all()


def get_by_id(db: DBSession, session_id: int) -> SessionRecord:
    """Raises RuntimeError if not found."""
    record = db.get(SessionRecord, session_id)
    if record is None:
        raise RuntimeError(f"Session {session_id} not found")
    return record


def get_by_user(db: DBSession, user_id: int) -> list[SessionRecord]:
    return db.exec(select(SessionRecord).where(SessionRecord.user_id == user_id)).all()


def get_active_by_board(db: DBSession, serial_number: str) -> SessionRecord | None:
    return db.exec(
        select(SessionRecord)
        .where(
            (SessionRecord.target_board_sn == serial_number) |
            (SessionRecord.control_board_sn == serial_number)
        )
        .where(SessionRecord.status == "active")
    ).first()

def get_reserved_by_board(db: DBSession, serial_number: str) -> SessionRecord | None:
    return db.exec(
        select(SessionRecord)
        .where(
            (SessionRecord.target_board_sn == serial_number) |
            (SessionRecord.control_board_sn == serial_number)
        )
        .where(SessionRecord.status == "reserved")
    ).first()


def get_active_by_user(db: DBSession, user_id: int) -> SessionRecord | None:
    return db.exec(
        select(SessionRecord)
        .where(SessionRecord.user_id == user_id)
        .where(SessionRecord.status == "active")
    ).first()

def get_reserved_by_user(db: DBSession, user_id: int) -> SessionRecord | None:
    return db.exec(
        select(SessionRecord)
        .where(SessionRecord.user_id == user_id)
        .where(SessionRecord.status == "reserved")
    ).first()


def has_overlapping_session(db: DBSession, serial_number: str, start_time: datetime, end_time: datetime) -> bool:
    return db.exec(
        select(SessionRecord)
        .where(
            (SessionRecord.target_board_sn == serial_number) |
            (SessionRecord.control_board_sn == serial_number)
        )
        .where(SessionRecord.status.in_(["reserved", "active"]))
        .where(SessionRecord.start_time < end_time)
        .where(SessionRecord.end_time > start_time)
    ).first() is not None


def get_time_until_next_reservation(db: DBSession, serial_number: str, start_time: datetime) -> timedelta | None:
    next_reservation = db.exec(
        select(SessionRecord)
        .where(
            (SessionRecord.target_board_sn == serial_number) |
            (SessionRecord.control_board_sn == serial_number)
        )
        .where(SessionRecord.status == "reserved")
        .where(SessionRecord.start_time > start_time)
        .order_by(SessionRecord.start_time)
    ).first()
    if next_reservation is None:
        return None
    return next_reservation.start_time - start_time


def create(db: DBSession, record: SessionRecord) -> SessionRecord:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update(db: DBSession, session_id: int, data: dict) -> SessionRecord:
    """Raises RuntimeError if not found."""
    record = db.get(SessionRecord, session_id)
    if record is None:
        raise RuntimeError(f"Session {session_id} not found")
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete(db: DBSession, session_id: int) -> None:
    """Raises RuntimeError if not found."""
    record = db.get(SessionRecord, session_id)
    if record is None:
        raise RuntimeError(f"Session {session_id} not found")
    db.delete(record)
    db.commit()


def delete_all(db: DBSession) -> int:
    """Deletes all sessions. Returns the number of deleted rows."""
    records = db.exec(select(SessionRecord)).all()
    for record in records:
        db.delete(record)
    db.commit()
    return len(records)


if __name__ == "__main__":
    try:
        from backend.database import engine
    except ImportError:
        from database import engine

    TARGET_SN = "066FFF3632524B3043205333"
    CONTROL_SN = "066DFF535550755187063847"
    """
    # Test 1: create
    print("--- Test 1: create ---")
    with DBSession(engine) as db:
        record = create(db, SessionRecord(
            user_id=1,
            json_path="configs/devices/nucleo_f401re_1.json",
            target_board_sn=BOARD_SN,
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            status="reserved"
        ))
        session_id = record.id
        print(f"PASS — created session id={session_id}")
    
    # Test 2: get_by_id — valid
    print("\n--- Test 2: get_by_id (valid) ---")
    with DBSession(engine) as db:
        try:
            r = get_by_id(db, session_id)
            print(f"PASS — found session id={r.id} | status={r.status}")
        except RuntimeError as e:
            print(f"FAIL — {e}")

    # Test 3: get_by_id — invalid
    print("\n--- Test 3: get_by_id (invalid) ---")
    with DBSession(engine) as db:
        try:
            get_by_id(db, 99999)
            print("FAIL — should have raised RuntimeError")
        except RuntimeError as e:
            print(f"PASS — correctly rejected: {e}")

    # Test 4: get_all
    print("\n--- Test 4: get_all ---")
    with DBSession(engine) as db:
        all_sessions = get_all(db)
        print(f"PASS — {len(all_sessions)} session(s) in DB")

    # Test 5: get_by_user
    print("\n--- Test 5: get_by_user ---")
    with DBSession(engine) as db:
        sessions = get_by_user(db, 1)
        print(f"PASS — {len(sessions)} session(s) for user 1")

    # Test 6: get_active_by_board
    print("\n--- Test 6: get_active_by_board ---")
    with DBSession(engine) as db:
        active = get_active_by_board(db, BOARD_SN)
        print(f"PASS — active session: {active.id if active else None}")

    # Test 7: update
    print("\n--- Test 7: update ---")
    with DBSession(engine) as db:
        try:
            r = update(db, session_id, {"status": "ended"})
            print(f"PASS — updated status={r.status}")
        except RuntimeError as e:
            print(f"FAIL — {e}")
    
    # Test 8: get_time_until_next_reservation (no upcoming reservation)
    print("\n--- Test 8: get_time_until_next_reservation ---")
    with DBSession(engine) as db:
        delta = get_time_until_next_reservation(db, BOARD_SN)
        print(f"PASS — time until next reservation: {delta}")

    # Test 9: delete — valid
    print("\n--- Test 9: delete (valid) ---")
    with DBSession(engine) as db:
        try:
            delete(db, 3)
            print(f"PASS — deleted session id={3}")
        except RuntimeError as e:
            print(f"FAIL — {e}")
  
    # Test 10: delete — invalid
    print("\n--- Test 10: delete (invalid) ---")
    with DBSession(engine) as db:
        try:
            delete(db, session_id)
            print("FAIL — should have raised RuntimeError")
        except RuntimeError as e:
            print(f"PASS — correctly rejected: {e}")

    # Test 11: delete_all
    print("\n--- Test 11: delete_all ---")
    with DBSession(engine) as db:
        count = delete_all(db)
        print(f"PASS — deleted {count} session(s)")
    with DBSession(engine) as db:
        remaining = get_all(db)
        print(f"PASS — {len(remaining)} session(s) remaining (expected 0)")
    """
    
    # Test 9: delete — valid
    print("\n--- Test 9: delete (valid) ---")
    with DBSession(engine) as db:
        try:
            delete_all(db)
            print(f"PASS — deleted session id={3}")
        except RuntimeError as e:
            print(f"FAIL — {e}")