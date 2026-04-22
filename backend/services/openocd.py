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
from services.devices import get_by_id as get_board_by_id, update as update_board
#from services.devices import update as update_board
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
    if (openocd_pid == None):
        return False
    
    client = _ssh(board) 
    stdin, stdout, stderr = client.exec_command(f"cat /proc/{openocd_pid}/comm") # checks process existence without affecting it
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

    # Update openocd_pid in database
    with Session(engine) as session:
        update_board(session, board.id, {"openocd_pid" : openocd_pid})
    
    return openocd_pid

def kill_openocd(board : Board): # Parameter board or openocd_pid ?
    pass
if __name__ == "__main__":
    with Session(engine) as session:
        board = get_board_by_id(session, 1)
    print(is_running(board))



