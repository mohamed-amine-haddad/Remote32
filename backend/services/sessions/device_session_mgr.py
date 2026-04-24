import sys
sys.path.insert(0, ".")

import os
import paramiko
from dotenv import load_dotenv
from fastapi import HTTPException
from models import Board, RaspberryPi, DeviceSession
from sqlmodel import Session
from database import engine
from datetime import datetime, timedelta

load_dotenv()
from services.devices import get_by_id as get_board_by_id
from services.devices import update as update_board
from services.sessions.device_session import get_active_by_board_id, get_active_by_user_id, get_time_until_next_reservation, create as create_device_session
from services.sessions.application_session import get_active_by_target_board_id, get_time_until_next_reservation as get_app_time_until_next_reservation
from services.openocd import is_running, is_port_in_use, launch_openocd, kill_openocd


# Start a device session now if the time slot is available
# One safety case : user has a reseved session that starts soon and tries to start another one
def start_device_session(board_id : int, user_id : int, duration_minutes : int) -> int :
    with Session(engine) as session:
        board = get_board_by_id(session, board_id)
        active_device_session = get_active_by_board_id(session, board_id)
        active_app_session = get_active_by_target_board_id(session, board_id)
        active_user_session = get_active_by_user_id(session, user_id)
        device_time_until_next = get_time_until_next_reservation(session, board_id)
        app_time_until_next = get_app_time_until_next_reservation(session, board_id)

    # Check board existence
    if board is None:
        raise HTTPException(status_code=404, detail="Board does not exist")

    # Check if the specified board is running
    if is_running(board) or active_device_session or active_app_session:
        raise HTTPException(status_code=409, detail="Board already has an active session")

    # Check if the board's gdb port is already in use
    if is_port_in_use(board):
        raise HTTPException(status_code=409, detail="GDB port already in use")

    # Check if User has other active sessions
    if active_user_session:
        raise HTTPException(status_code=409, detail="You can only have one active session at a time")

    # Pick the closest upcoming reservation across both session types
    time_until_next = device_time_until_next
    if app_time_until_next is not None:
        if time_until_next is None or app_time_until_next < time_until_next:
            time_until_next = app_time_until_next

    # If an upcoming reservation exists, cap the session duration to the remaining time (only if > 10 minutes)
    if time_until_next is not None:
        if time_until_next <= timedelta(minutes=10):
            raise HTTPException(status_code=409, detail=f"Not enough time before next reservation ({int(time_until_next.total_seconds() // 60)} minutes remaining)")
        duration_minutes = int(time_until_next.total_seconds() // 60)

    # Safety checks Successful
    openocd_pid = launch_openocd(board)

    with Session(engine) as session:
        create_device_session(session, DeviceSession(
          user_id=user_id,
          board_id=board_id,
          start_time=datetime.now(),
          end_time=datetime.now() + timedelta(minutes=duration_minutes),
          status="active"
        ))
        update_board(session, board_id, {"status" : "running", "openocd_pid" : openocd_pid})

    return board.gdb_port



if __name__ == "__main__":
    with Session(engine) as session:
        board1 = get_board_by_id(session, 1)
        board2 = get_board_by_id(session, 2)

    """
    print("1) is_running before launch:", is_running(board1))
    
    gdb_port_1 = start_device_session(board1.id, 1, 90)
    print("launched with GDB Port:", gdb_port_1)

    with Session(engine) as session:
        board1 = get_board_by_id(session, 1)

    print("1) is_running after launch:", is_running(board1))
    """
    print("---")
    
    print("2) is_running before launch:", is_running(board2))
    
    gdb_port_2 = start_device_session(board2.id, 2, 90)
    print("launched with PID:", gdb_port_2)

    with Session(engine) as session:
        board2 = get_board_by_id(session, 2)

    print("2) is_running after launch:", is_running(board2))
    