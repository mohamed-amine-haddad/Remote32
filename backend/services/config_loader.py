# Pydantic models mirroring the JSON config schema + functions to load and validate config files.
# Single entry point between raw JSON files on disk and the rest of the backend.

from pydantic import BaseModel
from database import engine
from sqlmodel import Session
from pathlib import Path
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
    bin_file : str
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

def load_config(json_path: str) -> SessionConfig:
    # reads one JSON file from disk, parses and validates it into a SessionConfig
    pass 

def load_all_configs() -> dict[str, SessionConfig]:
    # Scans configs/devices/ and configs/applications/, loads every .json file.
    # Returns a dict keyed by relative path (e.g : "configs/devices/nucleo_f401re_1.json").
    pass

def validate_configs(configs: dict[str, SessionConfig], db_session: Session) -> None:
    """
    called at startup, two checks:
    - every serial_number across all configs has a matching row in the board table
    - no two different boards (different serial numbers) share the same GDB, telnet, or tcl port
    """
    pass



