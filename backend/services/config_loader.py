# Pydantic models mirroring the JSON config schema + functions to load and validate config files.
# Single entry point between raw JSON files on disk and the rest of the backend.

import sys
sys.path.insert(0, ".")

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import Session, select

DEVICES_DIR = Path(__file__).parent.parent / "configs" / "devices"
APPLICATIONS_DIR = Path(__file__).parent.parent / "configs" / "applications"

class PiConfig(BaseModel):
    host : str
    user : str
    password : str

class TargetConfig(BaseModel):
    serial_number : str
    pi : PiConfig
    openocd_cfg : str
    gdb_port : int
    telnet_port : int
    tcl_port : int
    gdb_external_host : str
    gdb_external_port : int

class CameraConfig(BaseModel):
    host     : str
    user     : str
    password : str
    port     : int

class ButtonConfig(BaseModel):
    label : str
    command : str

class FirmwareConfig(BaseModel):
    name : str
    bin_file : str = Field(alias="bin")  # "bin" in JSON maps to bin_file in Python (bin is a built-in)
    buttons : list[ButtonConfig]

class ControlConfig(BaseModel):
    serial_number : str
    pi : PiConfig
    openocd_cfg : str
    gdb_port : int
    telnet_port : int
    tcl_port : int
    serial_port : str
    firmwares : list[FirmwareConfig]

class SessionConfig(BaseModel):
    name        : str
    description : str = ""
    target      : TargetConfig
    control     : Optional[ControlConfig] = None
    camera      : Optional[CameraConfig] = None
    @property
    def is_application(self) -> bool:
        return self.control is not None

# reads one JSON file from disk, parses and validates it into a SessionConfig
def load_config(json_path: str) -> SessionConfig:
    full_json_path = Path(__file__).parent.parent / json_path
    with open(full_json_path) as f:
        return SessionConfig(**json.load(f))

def load_all_configs() -> dict[str, SessionConfig]:
    """
    Scans configs/devices/ and configs/applications/ and loads every .json file.

    Returns a dict where :
    -key = relative path to the file (e.g. "configs/devices/nucleo_f401re_1.json")
    -value = the parsed SessionConfig object for that file
    """
    configs = {}

    for directory in [DEVICES_DIR, APPLICATIONS_DIR]:
        # find all json files in directory
        for json_file in directory.glob("*.json"): 
            # Build the relative path used as key (e.g. "configs/devices/nucleo_f401re_1.json")
            relative_path = json_file.relative_to(Path(__file__).parent.parent).as_posix()
            configs[relative_path] = load_config(relative_path)

    return configs

def validate_configs(configs: dict[str, SessionConfig], db_session: Session) -> None:
    """
    Called at startup. Raises RuntimeError if any check fails, preventing the server from starting.

    Check 1 — every serial_number in every config has a matching row in the board table.
    Check 2 — no two different boards share the same GDB, telnet, or tcl port.
    """
    try:
        from backend.models import Board  # when running via uvicorn from repo root
    except ImportError:
        from models import Board          # when running directly from backend/

    # Collect all unique boards across all configs: serial_number -> (gdb_port, telnet_port, tcl_port, source_file)
    # If the same board appears in multiple configs, its ports must be identical — otherwise raise immediately
    boards: dict[str, tuple[int, int, int, str]] = {}
    for json_path, config in configs.items():
        for board_cfg in [config.target] + ([config.control] if config.control else []):
            sn = board_cfg.serial_number
            ports = (board_cfg.gdb_port, board_cfg.telnet_port, board_cfg.tcl_port)
            if sn in boards and boards[sn][:3] != ports:
                raise RuntimeError(
                    f"Board '{sn}' has inconsistent ports across config files "
                    f"(first seen in '{boards[sn][3]}', conflicts with '{json_path}')"
                )
            boards[sn] = (*ports, json_path)

    # Check 1: every serial_number must have a matching board row in the database
    for serial_number, (gdb_port, telnet_port, tcl_port, source_file) in boards.items():
        board = db_session.exec(select(Board).where(Board.serial_number == serial_number)).first()
        if board is None:
            raise RuntimeError(f"Board '{serial_number}' referenced in '{source_file}' not found in the database")

    # Check 2: no two different boards can share the same port
    seen_ports: dict[int, str] = {}  # port -> serial_number that owns it
    for serial_number, (gdb_port, telnet_port, tcl_port, _) in boards.items():
        for port in [gdb_port, telnet_port, tcl_port]:
            if port in seen_ports and seen_ports[port] != serial_number:
                raise RuntimeError(f"Port {port} conflict between :\n'{serial_number}' (file : '{boards[serial_number][3]}') and\n'{seen_ports[port]}' (file : '{boards[seen_ports[port]][3]}) ")                    
            seen_ports[port] = serial_number

if __name__ == "__main__":
    """
    nucleo_f401 = load_config("configs/devices/nucleo_f401re_1.json")
    print("NUCLEO F401 :")
    print(json.dumps(nucleo_f401.model_dump(), indent = 4))
    
    print("---")

    test_button = load_config("configs/applications/test_button.json")
    print("TEST BUTTON:")
    print(json.dumps(test_button.model_dump(), indent=4))
    

    all_configs = load_all_configs()
    for path, config in all_configs.items():
      print(path)
      print(json.dumps(config.model_dump(), indent=4))
      print()
    """
    all_configs = load_all_configs()
    for path, config in all_configs.items():
      print(path)
      print(json.dumps(config.model_dump(), indent=4))
    

