import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from models import User


def get_all(session: Session) -> list[User]:
    return session.exec(select(User)).all()


def get_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_by_role(session: Session, role: str) -> list[User]:
    return session.exec(select(User).where(User.role == role)).all()


def create(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update(session: Session, user_id: int, data: dict) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


def delete(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True


if __name__ == "__main__":
    from database import engine
    from sqlmodel import Session

    with Session(engine) as session:

        # --- CREATE ---
        new_user = User(
            name="Test User",
            email="test@remote32.com",
            hashed_password="hashed_pw_placeholder",
            role="user"
        )
        created = create(session, new_user)
        print("Created:", created)

        # --- GET ALL ---
        all_users = get_all(session)
        print(f"All users ({len(all_users)}):")
        for u in all_users:
            print(f"  [{u.id}] {u.name} | {u.email} | {u.role}")

        # --- GET BY ID ---
        fetched = get_by_id(session, created.id)
        print("Fetched by ID:", fetched)

        # --- GET BY EMAIL ---
        by_email = get_by_email(session, "test@remote32.com")
        print("Fetched by email:", by_email)

        # --- GET BY ROLE ---
        admins = get_by_role(session, "admin")
        print(f"Admins ({len(admins)}):", admins)

        # --- UPDATE ---
        updated = update(session, created.id, {"role": "admin"})
        print("Updated role:", updated.role)
        
        # --- DELETE ---
        deleted = delete(session, created.id)
        print("Deleted:", deleted)
