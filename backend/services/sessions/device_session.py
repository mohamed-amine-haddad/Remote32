import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from models import DeviceSession


def get_all(session: Session) -> list[DeviceSession]:
    return session.exec(select(DeviceSession)).all()


def get_by_id(session: Session, device_session_id: int) -> DeviceSession | None:
    return session.get(DeviceSession, device_session_id)


def get_by_board_id(session: Session, board_id: int) -> list[DeviceSession]:
    return session.exec(select(DeviceSession).where(DeviceSession.board_id == board_id)).all()


def get_by_status(session: Session, status: str) -> list[DeviceSession]:
    return session.exec(select(DeviceSession).where(DeviceSession.status == status)).all()


def create(session: Session, device_session: DeviceSession) -> DeviceSession:
    session.add(device_session)
    session.commit()
    session.refresh(device_session)
    return device_session


def update(session: Session, device_session_id: int, data: dict) -> DeviceSession | None:
    device_session = session.get(DeviceSession, device_session_id)
    if not device_session:
        return None
    for key, value in data.items():
        setattr(device_session, key, value)
    session.commit()
    session.refresh(device_session)
    return device_session


def delete(session: Session, device_session_id: int) -> bool:
    device_session = session.get(DeviceSession, device_session_id)
    if not device_session:
        return False
    session.delete(device_session)
    session.commit()
    return True


if __name__ == "__main__":
    from database import engine
    from sqlmodel import Session
    from datetime import datetime

    with Session(engine) as session:
        
        # --- CREATE ---
        new_session = DeviceSession(
            board_id=1,
            start_time=datetime(2026, 4, 21, 10, 0, 0),
            end_time=datetime(2026, 4, 21, 11, 0, 0),
            status="reserved"
        )
        created = create(session, new_session)
        print("Created:", created)
        
        # --- GET ALL ---
        all_sessions = get_all(session)
        print(f"All sessions ({len(all_sessions)}):")
        for s in all_sessions:
            print(f"  [{s.id}] board={s.board_id} | {s.start_time} -> {s.end_time} | {s.status}")

        # --- GET BY ID ---
        fetched = get_by_id(session, 1)
        print("Fetched by ID:", fetched)

        # --- GET BY BOARD ID ---
        board_sessions = get_by_board_id(session, 1)
        print("Sessions for board 1:", board_sessions)

        # --- GET BY STATUS ---
        reserved = get_by_status(session, "active")
        print("Active sessions:", reserved)

        # --- UPDATE ---
        updated = update(session, 3, {"status": "active"})
        print("Updated status:", updated.status)

        # --- DELETE ---
        deleted = delete(session, 3)
        print("Deleted:", deleted)
