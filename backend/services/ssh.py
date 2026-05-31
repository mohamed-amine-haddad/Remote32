import logging
import time
import paramiko
from typing import Protocol

logger = logging.getLogger(__name__)

class SSHCredentials(Protocol):
    host     : str
    user     : str
    password : str

try:
    from config_loader import load_all_configs
    from devices import get_by_serial
except ImportError:
    from backend.services.config_loader import load_all_configs
    from backend.services.devices import get_by_serial

_pool: dict[str, paramiko.SSHClient] = {}

def ssh_connect(credentials: SSHCredentials) -> paramiko.SSHClient:
    host = credentials.host
    client = _pool.get(host)
    transport = client.get_transport() if client else None
    if transport is None or not transport.is_active():
        reason = "no prior connection" if transport is None else "transport inactive"
        logger.info("[ssh] %s — connecting (reason: %s)", host, reason)
        t0 = time.perf_counter()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=credentials.host, username=credentials.user, password=credentials.password, timeout=15)
        except Exception as e:
            raise RuntimeError(f"SSH connection to '{credentials.host}' failed: {e}") from e
        logger.info("[ssh] %s — connected in %.2fs", host, time.perf_counter() - t0)
        _pool[host] = client
    else:
        logger.info("[ssh] %s — pool hit", host)
    return client

if __name__ == "__main__":
    try:
        configs = load_all_configs()
        target_config = get_by_serial(configs, "066FFF3632524B3043205333").target
    except RuntimeError as e:
        print(f"FAIL — {e}")
        exit(1)

    try:
        client = ssh_connect(target_config.pi)
        _, stdout, _ = client.exec_command("echo ok")
        print(f"PASS — SSH connected to {target_config.pi.host}, got: {stdout.read().decode().strip()}")
        client.close()
    except Exception as e:
        print(f"FAIL — SSH connection: {e}")