import shlex
import sys
sys.path.insert(0, ".")

try:
    from backend.services.config_loader import ControlConfig
    from backend.services.ssh import ssh_connect
except ImportError:
    from services.config_loader import ControlConfig
    from services.ssh import ssh_connect


def send_command(board_cfg: ControlConfig, command: str) -> None:
    client = ssh_connect(board_cfg.pi)
    port = board_cfg.serial_port
    quoted = shlex.quote(command)
    client.exec_command(f"stty -F {port} {board_cfg.baud_rate} && echo {quoted} > {port}")
