from sqlmodel import Session, select
from backend.models import Board
from backend.database import engine, create_db_and_tables

create_db_and_tables()

BOARDS = [
    {"serial_number": "066FFF3632524B3043205333", "type": "target"},
    {"serial_number": "066DFF535550755187063847", "type": "control"},
]

with Session(engine) as session:
    for b in BOARDS:
        exists = session.exec(select(Board).where(Board.serial_number == b["serial_number"])).first()
        if not exists:
            session.add(Board(**b))
    session.commit()
    print("Done.")
