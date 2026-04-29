# SSH-based OpenOCD lifecycle management on the Raspberry Pi.
# All functions accept a TargetConfig — Pi credentials and board info come from the config, not the DB.

import sys
sys.path.insert(0, ".")

import os
import time
import paramiko
from dotenv import load_dotenv
from sqlmodel import Session, select

load_dotenv()

try:
    from backend.services.config_loader import TargetConfig
    from backend.services.ssh import ssh_connect
    from backend.database import engine
    from backend.models import Board
except ImportError:
    from services.config_loader import TargetConfig
    from services.ssh import ssh_connect
    from database import engine
    from models import Board

"""
def ssh_connect(board_cfg: TargetConfig) -> paramiko.SSHClient:
    # Opens and returns an SSH connection to the Pi using credentials from the config
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=board_cfg.pi.host,
        username=board_cfg.pi.user,
        password=board_cfg.pi.password
    )
    return client
"""

def is_running_by_pid(openocd_pid: int, board_cfg: TargetConfig) -> bool:
    # Verifies that the process with the given PID is actually openocd on the Pi
    client = ssh_connect(board_cfg)
    _, stdout, _ = client.exec_command(f"cat /proc/{openocd_pid}/comm")
    process_name = stdout.read().decode().strip()
    client.close()
    return process_name == "openocd"


def is_running(board_cfg: TargetConfig) -> bool:
    # Looks up the board's current PID from the DB, then verifies the process is alive on the Pi
    with Session(engine) as session:
        board = session.exec(select(Board).where(Board.serial_number == board_cfg.serial_number)).first()
    if board is None or board.openocd_pid is None:
        return False
    return is_running_by_pid(board.openocd_pid, board_cfg)


def is_port_in_use(board_cfg: TargetConfig) -> bool:
    # Checks if the board's GDB port is already listening on the Pi
    client = ssh_connect(board_cfg)
    _, stdout, _ = client.exec_command(f"ss -tlnp | grep :{board_cfg.gdb_port}")
    result = stdout.read().decode().strip()
    client.close()
    return len(result) > 0


def launch_openocd(board_cfg: TargetConfig) -> int:
    """
    Launches OpenOCD on the Pi for the given board config.
    Returns the PID of the started process.
    Raises RuntimeError if OpenOCD fails to start.
    """
    client = ssh_connect(board_cfg)
    config_path = os.getenv("CONFIG_PATH") + board_cfg.openocd_cfg
    log_file = f"/tmp/openocd_{board_cfg.serial_number}.log"
    _, stdout, _ = client.exec_command(
        f"nohup openocd -f {config_path} > {log_file} 2>&1 & echo $!"
    )
    openocd_pid = int(stdout.readline().strip())
    client.close()

    time.sleep(1)
    if not is_running_by_pid(openocd_pid, board_cfg):
        raise RuntimeError(f"OpenOCD failed to start for board '{board_cfg.serial_number}'")

    return openocd_pid


def kill_openocd(board_cfg: TargetConfig) -> None:
    """
    Kills the OpenOCD process running on the Pi for this board.
    Raises RuntimeError if no active process exists.
    """
    if not is_running(board_cfg):
        raise RuntimeError(f"Board '{board_cfg.serial_number}' has no active OpenOCD process")

    with Session(engine) as session:
        board = session.exec(select(Board).where(Board.serial_number == board_cfg.serial_number)).first()

    client = ssh_connect(board_cfg)
    client.exec_command(f"kill {board.openocd_pid}")
    client.close()


if __name__ == "__main__":
    try:
        from backend.services.config_loader import load_config
    except ImportError:
        from services.config_loader import load_config
    """
    board_cfg = load_config("configs/devices/nucleo_f401re_1.json").target
    print(f"Board: {board_cfg.serial_number} | Pi: {board_cfg.pi.host} | GDB port: {board_cfg.gdb_port}\n")

    # Test 1: SSH connection
    print("--- Test 1: SSH connection ---")
    try:
        client = ssh_connect(board_cfg)
        client.close()
        print("PASS — SSH connection successful")
    except Exception as e:
        print(f"FAIL — {e}")

    # Test 2: is_running before launch
    print("\n--- Test 2: is_running before launch ---")
    print(f"PASS — is_running = {is_running(board_cfg)} (expected False)")

    # Test 3: is_port_in_use before launch
    print("\n--- Test 3: is_port_in_use before launch ---")
    print(f"PASS — is_port_in_use = {is_port_in_use(board_cfg)}")

    # Test 4: launch_openocd
    print("\n--- Test 4: launch_openocd ---")
    pid = None
    try:
        pid = launch_openocd(board_cfg)
        print(f"PASS — launched with PID {pid}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

    # Test 5: is_running_by_pid after launch
    print("\n--- Test 5: is_running after launch ---")
    if pid:
        print(f"PASS — is_running_by_pid = {is_running_by_pid(pid, board_cfg)}")
    else:
        print("SKIP — launch failed")

    # Test 6: kill_openocd
    print("\n--- Test 6: kill_openocd ---")
    if pid:
        # Store PID in DB so kill_openocd can find it
        with Session(engine) as session:
            board = session.exec(select(Board).where(Board.serial_number == board_cfg.serial_number)).first()
            board.openocd_pid = pid
            board.status = "running"
            session.add(board)
            session.commit()
        try:
            kill_openocd(board_cfg)
            print("PASS — killed successfully")
        except RuntimeError as e:
            print(f"FAIL — {e}")
    else:
        print("SKIP — launch failed")

    # Test 7: kill when not running
    print("\n--- Test 7: kill when not running ---")
    try:
        kill_openocd(board_cfg)
        print("FAIL — should have raised RuntimeError")
    except RuntimeError as e:
        print(f"PASS — correctly rejected: {e}")
    """

    board_cfg = load_config("configs/devices/nucleo_f401re_1.json").target
    print(f"Board: {board_cfg.serial_number} | Pi: {board_cfg.pi.host} | GDB port: {board_cfg.gdb_port}\n")
    """
    # Test 1: SSH connection
    print("--- Test 1: SSH connection ---")
    try:
        client = ssh_connect(board_cfg)
        client.close()
        print("PASS — SSH connection successful")
    except Exception as e:
        print(f"FAIL — {e}")

    # Test 2: is_running before launch
    print("\n--- Test 2: is_running before launch ---")
    print(f"PASS — is_running = {is_running(board_cfg)}")

    # Test 3: is_port_in_use before launch
    print("\n--- Test 3: is_port_in_use before launch ---")
    print(f"PASS — is_port_in_use = {is_port_in_use(board_cfg)}")

    
    # Test 4: launch_openocd
    print("\n--- Test 4: launch_openocd ---")
    pid = None
    try:
        pid = launch_openocd(board_cfg)
        print(f"PASS — launched with PID {pid}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

        
    # Test 5: is_running_by_pid after launch
    print("\n--- Test 5: is_running after launch ---")
    if pid:
        print(f"PASS — is_running_by_pid = {is_running_by_pid(pid, board_cfg)}")
    else:
        print("SKIP — launch failed")
    """
    print(is_running(board_cfg))
    try:
        client = ssh_connect(board_cfg)
        _, stdout, _ = client.exec_command("echo ok")
        print(f"PASS — SSH connected to {board_cfg.pi.host}, got: {stdout.read().decode().strip()}")
        client.close()
    except Exception as e:
        print(f"FAIL — SSH connection: {e}")