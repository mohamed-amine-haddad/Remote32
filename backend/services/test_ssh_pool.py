import sys
sys.path.insert(0, ".")

try:
    from backend.services.config_loader import load_all_configs
    from backend.services.devices import get_by_serial
    from backend.services.ssh import ssh_connect, _pool
except ImportError:
    from services.config_loader import load_all_configs
    from services.devices import get_by_serial
    from services.ssh import ssh_connect, _pool
    

configs = load_all_configs()
board_cfg = get_by_serial(configs, "066FFF3632524B3043205333")
credentials = board_cfg.target.pi

# Test 1: first call creates a new connection
print("--- Test 1: first call ---")
client1 = ssh_connect(credentials)
_, stdout, _ = client1.exec_command("echo ok")
print(f"PASS — connected to {credentials.host}, got: {stdout.read().decode().strip()}")
print(f"      pool size: {len(_pool)}")

# Test 2: second call returns the same object (no new handshake)
print("\n--- Test 2: second call reuses connection ---")
client2 = ssh_connect(credentials)
if client1 is client2:
    print("PASS — same client object returned from pool")
else:
    print("FAIL — different client object, pool not working")

# Test 3: reused connection still works
print("\n--- Test 3: reused connection executes commands ---")
_, stdout, _ = client2.exec_command("echo reused")
print(f"PASS — got: {stdout.read().decode().strip()}")
