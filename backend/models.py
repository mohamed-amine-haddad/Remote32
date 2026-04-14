from sqlmodel import Field, SQLModel
from typing import Optional

# Stm32 board Model
class Board(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key = True)
    name : str
    serial_number : str = Field(unique = True)
    config_file: Optional[str] = Field(default=None, unique = True)
    gdb_port : int = Field(unique = True)
    telnet_port : int = Field(unique = True)
    tcl_port : int = Field(unique = True)
    status : str = Field(default = "idle")
    pi_host : str = Field(default = "localhost")
    openocd_pid : Optional[int] = Field(default = None)


