import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from models import RaspberryPi


def get_all(session: Session) -> list[RaspberryPi]:
    return session.exec(select(RaspberryPi)).all()


def get_by_id(session: Session, pi_id: int) -> RaspberryPi | None:
    return session.get(RaspberryPi, pi_id)


def create(session: Session, pi: RaspberryPi) -> RaspberryPi:
    session.add(pi)
    session.commit()
    session.refresh(pi)
    return pi


def update(session: Session, pi_id: int, data: dict) -> RaspberryPi | None:
    pi = session.get(RaspberryPi, pi_id)
    if not pi:
        return None
    for key, value in data.items():
        setattr(pi, key, value)
    session.commit()
    session.refresh(pi)
    return pi


def delete(session: Session, pi_id: int) -> bool:
    pi = session.get(RaspberryPi, pi_id)
    if not pi:
        return False
    session.delete(pi)
    session.commit()
    return True


if __name__ == "__main__":
    from database import engine

    with Session(engine) as session:
        """
        pi = RaspberryPi(host="testhost", user="testuser", password="testpass")
        created = create(session, pi)
        print("Created:", created)

        all_pis = get_all(session)
        print("All pis:", all_pis)

        fetched = get_by_id(session, 1)
        print("Fetched by ID:", fetched)

        updated = update(session, created.id, {"user": "newuser"})
        print("Updated user:", updated.user)

        deleted = delete(session, 2)
        print("Deleted:", deleted)
        """
        updated = update(session, 1, {"host": "192.168.1.15"})
        print("Updated user:", updated.user)