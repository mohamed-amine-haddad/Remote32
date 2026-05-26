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
    client.exec_command(f"echo '{command}' > {board_cfg.serial_port}")

