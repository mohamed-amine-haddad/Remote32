from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

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
    pi_id : int = Field(foreign_key = "raspberrypi.id")
    openocd_pid : Optional[int] = Field(default = None)


class DeviceSession(SQLModel, table=True):
    __tablename__ = "device_session"
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    start_time: datetime
    end_time: datetime
    status: str  # reserved | active | ended | cancelled


class ApplicationSession(SQLModel, table=True):
    __tablename__ = "application_session"
    id: Optional[int] = Field(default=None, primary_key=True)
    target_board_id: int = Field(foreign_key="board.id")
    control_board_id: int = Field(foreign_key="board.id")
    start_time: datetime
    end_time: datetime
    status: str  # reserved | active | ended | cancelled

class RaspberryPi(SQLModel, table=True):
    id : Optional[int] = Field(default = None, primary_key = True)
    host : str = Field(unique = True)
    user : str
    password : str
