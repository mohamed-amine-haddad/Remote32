import sys
sys.path.insert(0, ".")

import paramiko 
from models import Board, RaspberryPi
from sqlmodel import Session
from database import engine
from services.raspberrys import get_by_id as get_pi_by_id
from services.devices import get_by_id as get_board_by_id

session = paramiko.SSHClient()
session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
    stdin, stdout, stderr = client.exec_command(f"kill -0 {openocd_pid}") # checks process existence without affecting it
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    return exit_code == 0



if __name__ == "__main__":
      """
      from database import engine
      from sqlmodel import Session
        """
      with Session(engine) as session:
          board = session.get(Board, 1)
      print(is_running((board)))



