import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from models import ApplicationSession


def get_all(session: Session) -> list[ApplicationSession]:
    return session.exec(select(ApplicationSession)).all()


def get_by_id(session: Session, session_id: int) -> ApplicationSession | None:
    return session.get(ApplicationSession, session_id)


def get_by_target_board_id(session: Session, board_id: int) -> list[ApplicationSession]:
    return session.exec(select(ApplicationSession).where(ApplicationSession.target_board_id == board_id)).all()


def get_by_control_board_id(session: Session, board_id: int) -> list[ApplicationSession]:
    return session.exec(select(ApplicationSession).where(ApplicationSession.control_board_id == board_id)).all()


def get_by_user_id(session: Session, user_id: int) -> list[ApplicationSession]:
    return session.exec(select(ApplicationSession).where(ApplicationSession.user_id == user_id)).all()


def get_by_status(session: Session, status: str) -> list[ApplicationSession]:
    return session.exec(select(ApplicationSession).where(ApplicationSession.status == status)).all()


def create(session: Session, app_session: ApplicationSession) -> ApplicationSession:
    session.add(app_session)
    session.commit()
    session.refresh(app_session)
    return app_session


def update(session: Session, session_id: int, data: dict) -> ApplicationSession | None:
    app_session = session.get(ApplicationSession, session_id)
    if not app_session:
        return None
    for key, value in data.items():
        setattr(app_session, key, value)
    session.commit()
    session.refresh(app_session)
    return app_session


def delete(session: Session, session_id: int) -> bool:
    app_session = session.get(ApplicationSession, session_id)
    if not app_session:
        return False
    session.delete(app_session)
    session.commit()
    return True


if __name__ == "__main__":
    from database import engine
    from sqlmodel import Session
    from datetime import datetime

    with Session(engine) as session:

        # --- CREATE ---
        new_session = ApplicationSession(
            user_id=1,
            target_board_id=1,
            control_board_id=2,
            start_time=datetime(2026, 4, 21, 10, 0, 0),
            end_time=datetime(2026, 4, 21, 11, 0, 0),
            status="reserved"
        )
        created = create(session, new_session)
        print("Created:", created)

        # --- GET ALL ---
        all_sessions = get_all(session)
        print("All sessions:", all_sessions)

        # --- GET BY ID ---
        fetched = get_by_id(session, created.id)
        print("Fetched by ID:", fetched)

        # --- GET BY TARGET BOARD ID ---
        target_sessions = get_by_target_board_id(session, 1)
        print("Sessions for target board 1:", target_sessions)

        # --- GET BY CONTROL BOARD ID ---
        control_sessions = get_by_control_board_id(session, 2)
        print("Sessions for control board 2:", control_sessions)

        # --- GET BY STATUS ---
        reserved = get_by_status(session, "reserved")
        print("Reserved sessions:", reserved)

        # --- UPDATE ---
        updated = update(session, created.id, {"status": "active"})
        print("Updated status:", updated.status)

        # --- DELETE ---
        deleted = delete(session, created.id)
        print("Deleted:", deleted)
