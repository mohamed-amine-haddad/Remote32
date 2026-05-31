import time
import sys
sys.path.insert(0, ".")

from sqlmodel import Session as DBSession

try:
    from backend.services.config_loader import load_all_configs
    from backend.services.application_sessions import start, get_by_id, flash, send_command, uart_send, end
    from backend.database import engine
except ImportError:
    from services.config_loader import load_all_configs
    from services.application_sessions import start, get_by_id, flash, send_command, uart_send, end
    from database import engine

JSON_PATH = "configs/applications/test_button.json"
USER_ID = 2

configs = load_all_configs()

# Step 1: start session — launches OpenOCD for both boards
print("--- Step 1: start ---")
session_data = None
with DBSession(engine) as db:
    try:
        session_data = start(configs, db, JSON_PATH, USER_ID)
        print(f"PASS — session id={session_data['id']} | connect to {session_data['gdb_host']}:{session_data['gdb_port']}")
        print(f"       control devices: {len(session_data['control_devices'])}")
    except RuntimeError as e:
        print(f"FAIL — {e}")
        exit(1)

session_id = session_data["id"]

# Step 2: get_by_id
print("\n--- Step 2: get_by_id ---")
with DBSession(engine) as db:
    try:
        data = get_by_id(db, session_id, USER_ID, configs)
        print(f"PASS — status={data['status']} | ends_at={data['ends_at']} | time_left={data['time_left']}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

# Step 3: flash firmware to control board
print("\n--- Step 3: flash first binfile ---")
with DBSession(engine) as db:
    try:
        msg = flash(db, session_id, "blink_ctrl_led.bin", configs)
        print(f"PASS — {msg}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

print("\n--- Step 4: wait ---")
time.sleep(10)

# Step 3: flash firmware to control board
print("\n--- Step 5: flash second binfile---")
with DBSession(engine) as db:
    try:
        msg = flash(db, session_id, "blink_ctrl_led2.bin", configs)
        print(f"PASS — {msg}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

"""
# Step 4: send_command — requires firmware on control board + wiring
print("\n--- Step 4: send_command ---")
with DBSession(engine) as db:
    try:
        msg = send_command(db, 1, "PRESS_USER")
        print(f"PASS — {msg}")
    except RuntimeError as e:
        print(f"FAIL — {e}")


# Step 5: uart_send — requires firmware on control board + wiring
print("\n--- Step 5: uart_send ---")
with DBSession(engine) as db:
    try:
        msg = uart_send(db, session_id, "hello from backend")
        print(f"PASS — {msg}")
    except RuntimeError as e:
        print(f"FAIL — {e}")

# Step 6: end session — kills OpenOCD for both boards
print("\n--- Step 6: end ---")
with DBSession(engine) as db:
    try:
        msg = end(db, configs, session_id, USER_ID)
        print(f"PASS — {msg}")
    except RuntimeError as e:
        print(f"FAIL — {e}")
"""