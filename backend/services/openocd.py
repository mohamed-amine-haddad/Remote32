import sys
sys.path.insert(0, ".")

import os
import time
import paramiko
from dotenv import load_dotenv
from fastapi import HTTPException
from models import Board, RaspberryPi, DeviceSession
from sqlmodel import Session
from database import engine
from datetime import datetime, timedelta

load_dotenv()
from services.raspberrys import get_by_id as get_pi_by_id
from services.devices import get_by_id as get_board_by_id, update as update_board
from services.sessions.device_session import get_active_by_board_id, create as create_device_session

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
    if openocd_pid is None:
        return False
    return is_running_by_pid(openocd_pid, board)

def is_running_by_pid(openocd_pid: int, board: Board) -> bool:
    client = _ssh(board)
    stdin, stdout, stderr = client.exec_command(f"cat /proc/{openocd_pid}/comm")
    process_name = stdout.read().decode().strip()
    client.close()
    return process_name == "openocd"

def is_port_in_use(board : Board) -> bool:
    # Check if the board's gdb port is already in use
    client = _ssh(board)
    stdin, stdout, stderr = client.exec_command(f"ss -tlnp | grep :{board.gdb_port}")
    port_in_use = stdout.read().decode().strip()
    client.close()

    return len(port_in_use) > 0

def launch_openocd(board : Board) -> int:
    client = _ssh(board)
    config_file_path = os.getenv("CONFIG_PATH") + board.config_file
    stdin, stdout, stderr = client.exec_command(f"nohup openocd -f {config_file_path} > /tmp/openocd_{board.id}.log 2>&1 & echo $!")
    openocd_pid = stdout.readline().strip()
    client.close()

    time.sleep(1)
    if not is_running_by_pid(openocd_pid, board):
        raise HTTPException(status_code=500, detail="OpenOCD failed to start")

    """
    # Update openocd_pid in database
    with Session(engine) as session:
        update_board(session, board.id, {"status" : "running", "openocd_pid" : openocd_pid})
    """

    return openocd_pid

def kill_openocd(board : Board):
    if not is_running(board) == True:
        raise HTTPException(status_code = 409, detail = "Board does not have an active session")
    
    openocd_pid = board.openocd_pid
    client = _ssh(board)    
    client.exec_command(f"kill {openocd_pid}")
    client.close()
    
if __name__ == "__main__":
    with Session(engine) as session:
        board1 = get_board_by_id(session, 1)
        board2 = get_board_by_id(session, 2)

    print("1) is_running before launch:", is_running(board1))
    
    pid1 = launch_openocd(board1)
    print("launched with PID:", pid1)

    with Session(engine) as session:
        board = get_board_by_id(session, 1)

    print("1) is_running after launch:", is_running(board))
    print("---")
    print("2) is_running before launch:", is_running(board1))
    
    pid2 = launch_openocd(board2)
    print("launched with PID:", pid2)

    with Session(engine) as session:
        board2 = get_board_by_id(session, 2)

    print("1) is_running after launch:", is_running(board2))
      



