# Pydantic models mirroring the JSON config schema + functions to load and validate config files.
# Single entry point between raw JSON files on disk and the rest of the backend.

import json
from pathlib import Path
from pydantic import BaseModel, Field
from sqlmodel import Session

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
    firmwares : list[FirmwareConfig]

class SessionConfig(BaseModel):
    name : str
    target : TargetConfig
    controls : list[ControlConfig] = [] # DEfault value = []
    @property 
    def is_application(self) -> bool:
        return len(self.controls) > 0

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

"""
called at startup, two checks:
- every serial_number across all configs has a matching row in the board table
- no two different boards (different serial numbers) share the same GDB, telnet, or tcl port
"""
def validate_configs(configs: dict[str, SessionConfig], db_session: Session) -> None:
    pass

if __name__ == "__main__":
    all_configs = load_all_configs()
    for path, config in all_configs.items():
      print(path)
      print(json.dumps(config.model_dump(), indent=4))
      print()



