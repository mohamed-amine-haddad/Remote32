from sqlmodel import Session
from models import Board, User
from database import engine

with Session(engine) as session:
    boards = [
        Board(serial_number="066FFF3632524B3043205333", type="target"),
        Board(serial_number="066DFF535550755187063847", type="control"),
    ]
    for board in boards:
        session.add(board)
    session.commit()
    print("Seeded boards successfully")
