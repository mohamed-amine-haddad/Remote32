from sqlmodel import Session
from models import Board
from database import engine, create_db

create_db()

boards = [
  Board(name="Nucleo-F401RE", serial_number="066FFF3632524B3043205333", gdb_port=3333, telnet_port=4444, tcl_port=6666),
  Board(name="Nucleo-F103RB", serial_number="066DFF535550755187063847", gdb_port=3334, telnet_port=4445, tcl_port=6667),
]

with Session(engine) as session:
    for board in boards:
        session.add(board)
        session.flush()  # assigns the auto-incremented id before commit
        board.config_file = f"configs/devices/{board.name.lower().replace('-', '_')}_{board.id}.cfg"
    session.commit()
