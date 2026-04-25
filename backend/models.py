from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

# Runtime state of a physical STM32 board — static config lives in JSON files
class Board(SQLModel, table=True):
    serial_number : str = Field(primary_key=True)   # physical identity, matches JSON serial_number
    type          : str                              # "target" | "control"
    status        : str = Field(default="idle")      # "idle" | "running"
    openocd_pid   : Optional[int] = Field(default=None)

# Unified session — covers both device (no control board) and application (with control board)
class Session(SQLModel, table=True):
    __tablename__ = "session"
    id               : Optional[int] = Field(default=None, primary_key=True)
    user_id          : Optional[int] = Field(default=None, foreign_key="user.id")
    json_path        : str                                                          # path to config file — also acts as session type discriminator
    target_board_sn  : str           = Field(foreign_key="board.serial_number")
    control_board_sn : Optional[str] = Field(default=None, foreign_key="board.serial_number")  # None = device session
    start_time       : datetime
    end_time         : datetime
    status           : str                                                          # "reserved" | "active" | "ended" | "cancelled"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: str = Field(default="user")  # "user" or "admin"