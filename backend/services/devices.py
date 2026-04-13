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
