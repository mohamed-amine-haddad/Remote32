import sys
sys.path.insert(0, ".")

try:
    from backend.services.config_loader import load_config
    from backend.services.openocd import launch_openocd, flash_firmware, kill_openocd, is_running_by_pid
except ImportError:
    from services.config_loader import load_config
    from services.openocd import launch_openocd, flash_firmware, kill_openocd, is_running_by_pid

board_cfg = load_config("configs/devices/nucleo_f401re_1.json").target
print(f"Board : {board_cfg.serial_number}")
print(f"Pi    : {board_cfg.pi.host}")
print(f"Telnet: {board_cfg.telnet_port}\n")

# Step 1: launch OpenOCD
print("--- Step 1: launch OpenOCD ---")
pid = None
try:
    pid = launch_openocd(board_cfg)
    print(f"PASS — OpenOCD running with PID {pid}")
except RuntimeError as e:
    print(f"FAIL — {e}")
    exit(1)

# Step 2: flash
print("\n--- Step 2: flash_firmware ---")
try:
    flash_firmware(board_cfg, "blink_led.bin")
    print("PASS — firmware flashed and verified")
except RuntimeError as e:
    print(f"FAIL — {e}")

# Step 3: cleanup
print("\n--- Step 3: kill OpenOCD ---")
try:
    kill_openocd(board_cfg)
    print("PASS — OpenOCD killed")
except RuntimeError as e:
    print(f"FAIL — {e}")
