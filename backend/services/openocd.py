import sys
sys.path.insert(0, ".")

import os
import paramiko
from dotenv import load_dotenv
from fastapi import HTTPException
from models import Board, RaspberryPi
from sqlmodel import Session
from database import engine

load_dotenv()
from services.raspberrys import get_by_id as get_pi_by_id
from services.devices import get_by_id as get_board_by_id
from services.devices import update as update_board

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

def start_debug_session(board_id : int) -> int :
    with Session(engine) as session:
        board = get_board_by_id(session, board_id)

    if is_running(board) :
        raise HTTPException(status_code=409, detail="Board already has an active session")
        
    client = _ssh(board)
    config_file_path = os.getenv("CONFIG_PATH") + board.config_file

    stdin, stdout, stderr = client.exec_command(f"nohup openocd -f {config_file_path} > /tmp/openocd_{board_id}.log 2>&1 & echo $!")

    openocd_pid = stdout.readline().strip()

    with Session(engine) as session:
        update_board(session, board_id, {"status" : "running", "openocd_pid" : openocd_pid})

    return board.gdb_port


if __name__ == "__main__":
      with Session(engine) as session:
          board = session.get(Board, 1)
    
      print(start_debug_session((1)))



