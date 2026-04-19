import sys
sys.path.insert(0, ".")

import paramiko 
from models import Board, RaspberryPi
from sqlmodel import Session
from database import engine
from services.raspberrys import get_by_id

session = paramiko.SSHClient()
session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Opens and returns an SSH connection to the Pi that the board is connected to
def _ssh(board : Board):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    with Session(engine) as session:
          pi = get_by_id(session, board.pi_id)

    client.connect(hostname = pi.host, username = pi.user, password = pi.password)
    return client

if __name__ == "__main__":
      """
      from database import engine
      from sqlmodel import Session
        """
      with Session(engine) as session:
          board = session.get(Board, 1)
      client = _ssh(board)
      client.close()



