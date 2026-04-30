import os
from dotenv import load_dotenv

try:
    from config_loader import TargetConfig, load_all_configs
    from devices import get_by_serial
    from ssh import ssh_connect
except:
    from backend.services.config_loader import TargetConfig, load_all_configs
    from backend.services.devices import get_by_serial
    from backend.services.ssh import ssh_connect
load_dotenv()

def open_camera(board_cfg: TargetConfig) -> str:
    client = ssh_connect(board_cfg)
    mjpg_streamer_path = os.getenv("MJPG_STREAMER_PATH")
    _, stdout, _ = client.exec_command("nohup mjpg_streamer -o \"output_http.so -w /usr/local/share/mjpg-streamer/www\" -i \"input_uvc.so\" > /tmp/mjppg_streamer.log 2>1& &")
    stdout.read()
    client.close()
    return "link"

if __name__ == "__main__":
    try:
        configs = load_all_configs()
        target_config = get_by_serial(configs, "066FFF3632524B3043205333").target
        #print(f"PASS — found '{device.name}'")
    except RuntimeError as e:
        print(f"FAIL — {e}")
        exit(1)

    link = open_camera(target_config)