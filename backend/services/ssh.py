import time
import paramiko
from sqlmodel import Session, select

try:
    from config_loader import TargetConfig
    from devices import get_by_serial
    from config_loader import load_all_configs
except:
    from backend.services.config_loader import TargetConfig
    from backend.services.devices import get_by_serial
    from backend.services.config_loader import load_all_configs

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

if __name__ == "__main__":
    try:
        configs = load_all_configs()
        device = get_by_serial(configs, "066FFF3632524B3043205333").target
        #print(f"PASS — found '{device.name}'")
    except RuntimeError as e:
        print(f"FAIL — {e}")
        exit(1)

    try:
        client = ssh_connect(device)
        _, stdout, _ = client.exec_command("echo ok")
        print(f"PASS — SSH connected to {device.pi.host}, got: {stdout.read().decode().strip()}")
        client.close()
    except Exception as e:
        print(f"FAIL — SSH connection: {e}")