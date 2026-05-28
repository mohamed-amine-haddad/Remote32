#!/usr/bin/env python3
"""
Patch gdb_external_host and gdb_external_port in all config JSON files
to match the current ngrok TCP tunnel URLs.

Run on the Pi after ngrok starts, before the backend starts:
    python3 backend/update_ngrok.py

How it works:
  - Queries the ngrok local API at localhost:4040 to get all active TCP tunnels.
  - Builds a map of  local_port → (public_host, public_port).
  - Walks every JSON file under backend/configs/devices/ and backend/configs/applications/.
  - For each file, if target.gdb_port matches a tunnel, it updates
    target.gdb_external_host and target.gdb_external_port.
  - Writes the file back only if something actually changed (idempotent).
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

NGROK_API   = "http://127.0.0.1:4040/api/tunnels"
CONFIGS_DIR = Path(__file__).parent / "configs"


def fetch_tunnels() -> dict[int, tuple[str, int]]:
    try:
        with urllib.request.urlopen(NGROK_API, timeout=5) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as exc:
        print(f"ERROR: cannot reach ngrok API at {NGROK_API}: {exc}", file=sys.stderr)
        print("Make sure ngrok is running before calling this script.", file=sys.stderr)
        sys.exit(1)

    tunnels: dict[int, tuple[str, int]] = {}
    for t in data.get("tunnels", []):
        public_url = t.get("public_url", "")
        addr       = t.get("config", {}).get("addr", "")
        if not public_url.startswith("tcp://") or not addr:
            continue
        local_port  = int(addr.rsplit(":", 1)[-1])
        host_port   = public_url.removeprefix("tcp://")
        public_host, public_port_str = host_port.rsplit(":", 1)
        tunnels[local_port] = (public_host, int(public_port_str))

    return tunnels


def patch_file(path: Path, tunnels: dict[int, tuple[str, int]]) -> bool:
    with open(path) as f:
        data = json.load(f)

    target = data.get("target")
    if not target:
        return False

    local_port = target.get("gdb_port")
    if local_port not in tunnels:
        return False

    new_host, new_port = tunnels[local_port]
    if target.get("gdb_external_host") == new_host and target.get("gdb_external_port") == new_port:
        return False

    old_host = target.get("gdb_external_host", "?")
    old_port = target.get("gdb_external_port", "?")
    target["gdb_external_host"] = new_host
    target["gdb_external_port"] = new_port

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

    print(f"  {path.name:<40}  {old_host}:{old_port}  →  {new_host}:{new_port}")
    return True


def main() -> None:
    tunnels = fetch_tunnels()

    if not tunnels:
        print("WARNING: ngrok returned no TCP tunnels — nothing to update.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tunnels)} TCP tunnel(s):")
    for local, (host, port) in sorted(tunnels.items()):
        print(f"  localhost:{local}  →  {host}:{port}")
    print()

    config_files = sorted(
        list((CONFIGS_DIR / "devices").glob("*.json")) +
        list((CONFIGS_DIR / "applications").glob("*.json"))
    )

    if not config_files:
        print(f"No JSON configs found under {CONFIGS_DIR}", file=sys.stderr)
        sys.exit(1)

    updated = sum(patch_file(p, tunnels) for p in config_files)

    print()
    if updated:
        print(f"{updated} file(s) updated.")
    else:
        print("All configs already up to date.")


if __name__ == "__main__":
    main()
