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
from services.raspberrys import get_by_id as get_pi_by_id
from services.devices import get_by_id as get_board_by_id
from services.devices import update as update_board
from services.sessions.device_session import get_by_board_id, create as create_device_session

# Opens and returns an SSH connection to the Pi that the board is connected to
def _ssh(board : Board):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    with Session(engine) as session:
        pi = get_pi_by_id(session, board.pi_id)

    client.connect(hostname = pi.host, username = pi.user, password = pi.password)
    return client

def is_running(board : Board):
    openocd_pid = board.openocd_pid
    if (openocd_pid == None):
        return False
    
    client = _ssh(board) 
    stdin, stdout, stderr = client.exec_command(f"cat /proc/{openocd_pid}/comm") # checks process existence without affecting it
    process_name = stdout.read().decode().strip()

    client.close()
    return process_name == "openocd"

# Start a debug session immediately if the time slot is available
def start_debug_session(board_id : int, user_id : int, duration_minutes : int) -> int :
    with Session(engine) as session:
        board = get_board_by_id(session, board_id)
        active = get_by_board_id(session, board_id)
    
    # Check board existence
    if board == None:
        raise HTTPException(status_code = 404, detail = "Board does not exist")
    
    # Check if the specified board is running
    if is_running(board) or active == True:
        raise HTTPException(status_code=409, detail="Board already has an active session")

    # Check if the board's gdb port is already in use
    client = _ssh(board)
    stdin, stdout, stderr = client.exec_command(f"ss -tlnp | grep :{board.gdb_port}")
    port_in_use = stdout.read().decode().strip()
    if port_in_use:
      raise HTTPException(status_code=409, detail="GDB port already in use")
        
    # Safety checks Successful
    config_file_path = os.getenv("CONFIG_PATH") + board.config_file
    stdin, stdout, stderr = client.exec_command(f"nohup openocd -f {config_file_path} > /tmp/openocd_{board_id}.log 2>&1 & echo $!")
    openocd_pid = stdout.readline().strip()

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
          board = session.get(Board, 1)
    
      print(start_debug_session(1,1, 90))



