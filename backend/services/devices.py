import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select
from models import Board


def get_all(session: Session) -> list[Board]:
    return session.exec(select(Board)).all()


def get_by_id(session: Session, board_id: int) -> Board | None:
    return session.get(Board, board_id)


def create(session: Session, board: Board) -> Board:
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def update(session: Session, board_id: int, data: dict) -> Board | None:
    board = session.get(Board, board_id)
    if not board:
        return None
    for key, value in data.items():
        setattr(board, key, value)
    session.commit()
    session.refresh(board)
    return board


def delete(session: Session, board_id: int) -> bool:
    board = session.get(Board, board_id)
    if not board:
        return False
    session.delete(board)
    session.commit()
    return True

if __name__ == "__main__":
    from database import engine
    from sqlmodel import Session

    with Session(engine) as session:
        """
        
        board = Board(
            name = "testBoard",
            serial_number = "testSerialNumber",
            gdb_port = 3335,
            telnet_port = 1234,
            tcl_port = 3456,
        )
        created = create(session, board)
        print("Created:", created)

        # --- GET ALL ---
        all_boards = get_all(session)
        print("All boards:", all_boards)
        
        # --- GET BY ID ---
        fetched = get_by_id(session, 2)
        print("Fetched by ID:", fetched)
        """
        
        # --- UPDATE ---
        updated = update(session, 1, {"openocd_pid": 7058})
        print("Updated status:", updated.status)

        """
        # --- DELETE ---
        deleted = delete(session, 3)
        print("Deleted:", deleted)
        """
        
