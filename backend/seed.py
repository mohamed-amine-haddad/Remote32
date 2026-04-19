from sqlmodel import Session
from models import Board, DeviceSession, ApplicationSession, RaspberryPi
from database import engine
from datetime import datetime

with Session(engine) as session:
    pi = RaspberryPi(host="retroboy", user="retroboy69", password="Admin060606")
    session.add(pi)
    session.flush()

    boards = [
        Board(name="Nucleo-F401RE", serial_number="066FFF3632524B3043205333", gdb_port=3333, telnet_port=4444, tcl_port=6666, pi_id=pi.id),
        Board(name="Nucleo-F103RB", serial_number="066DFF535550755187063847", gdb_port=3334, telnet_port=4445, tcl_port=6667, pi_id=pi.id),
    ]
    for board in boards:
        session.add(board)
    session.flush()
    for board in boards:
        board.config_file = f"configs/devices/{board.name.lower().replace('-', '_')}_{board.id}.cfg"

    device_sessions = [
        DeviceSession(
            board_id=boards[0].id,
            start_time=datetime(2026, 4, 10, 9, 0, 0),
            end_time=datetime(2026, 4, 10, 10, 30, 0),
            status="ended",
        ),
        DeviceSession(
            board_id=boards[1].id,
            start_time=datetime(2026, 4, 14, 14, 0, 0),
            end_time=datetime(2026, 4, 14, 15, 0, 0),
            status="active",
        ),
    ]

    application_sessions = [
        ApplicationSession(
            target_board_id=boards[0].id,
            control_board_id=boards[1].id,
            start_time=datetime(2026, 4, 11, 8, 30, 0),
            end_time=datetime(2026, 4, 11, 11, 0, 0),
            status="ended",
        ),
        ApplicationSession(
            target_board_id=boards[1].id,
            control_board_id=boards[0].id,
            start_time=datetime(2026, 4, 15, 13, 0, 0),
            end_time=datetime(2026, 4, 15, 14, 30, 0),
            status="reserved",
        ),
    ]

    for ds in device_sessions:
        session.add(ds)
    for as_ in application_sessions:
        session.add(as_)
    session.commit()
