import time
from paramiko import SSHClient

try:
    from config_loader import SessionConfig, load_all_configs
    from devices import get_by_serial
    from ssh import ssh_connect
except:
    from backend.services.config_loader import SessionConfig, load_all_configs
    from backend.services.devices import get_by_serial
    from backend.services.ssh import ssh_connect

def _is_running(client: SSHClient) -> bool:
    _, stdout, _ = client.exec_command("pgrep mjpg_streamer")
    return stdout.read().decode().strip() != ""


def _find_device(client: SSHClient) -> str:
    _, stdout, _ = client.exec_command("v4l2-ctl --list-devices | grep -A1 'UVC' | grep '/dev/video'")
    device = stdout.read().decode().strip().split("\n")[0].strip()
    if not device:
        raise RuntimeError("No UVC camera device found on the Pi")
    return device


def open_camera(session_cfg: SessionConfig) -> str:
    if session_cfg.camera is None:
        raise RuntimeError(f"No camera configured for '{session_cfg.name}'")
    camera = session_cfg.camera
    client = ssh_connect(camera)
    if not _is_running(client):
        device = _find_device(client)
        client.exec_command(
            f"nohup mjpg_streamer -o \"output_http.so -w /usr/local/share/mjpg-streamer/www\" "
            f"-i \"input_uvc.so -d {device}\" > /tmp/mjpg_streamer.log 2>&1 &"
        )
        time.sleep(1)
        if not _is_running(client):
            _, stdout, _ = client.exec_command("cat /tmp/mjpg_streamer.log")
            log = stdout.read().decode().strip()
            raise RuntimeError(f"mjpg-streamer failed to start:\n{log}")
    return f"http://{camera.host}:{camera.port}/?action=stream"


if __name__ == "__main__":
    try:
        configs = load_all_configs()
        session = get_by_serial(configs, "066FFF3632524B3043205333")
        print(f"PASS — found '{session.name}'")
    except RuntimeError as e:
        print(f"FAIL — {e}")
        exit(1)

    try:
        link = open_camera(session)
        print(f"PASS — stream at {link}")
    except RuntimeError as e:
        print(f"FAIL — {e}")
