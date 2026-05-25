# Config-based device queries. Devices are configs/devices/ JSON files (no control boards).
# Configs are loaded once at startup and passed in — no disk I/O here.
# Board runtime state (status, openocd_pid) is read from the DB.

import sys
sys.path.insert(0, ".")

from sqlmodel import Session, select

try:
    from backend.services.config_loader import SessionConfig
    from backend.models import Board
except ImportError:
    from services.config_loader import SessionConfig
    from models import Board


def get_all(configs: dict[str, SessionConfig]) -> list[SessionConfig]:
    return [c for c in configs.values() if not c.is_application]


def get_by_serial(configs: dict[str, SessionConfig], serial_number: str) -> SessionConfig:
    """Raises RuntimeError if no device config has that target serial number."""
    for config in configs.values():
        if config.target.serial_number == serial_number and not config.is_application:
            return config
    raise RuntimeError(f"Device '{serial_number}' not found in configs")


def get_board(serial_number: str, db: Session) -> Board:
    """Raises RuntimeError if the board row is missing from the DB."""
    board = db.exec(select(Board).where(Board.serial_number == serial_number)).first()
    if board is None:
        raise RuntimeError(f"Board '{serial_number}' not found in database")
    return board


def create_board(serial_number: str, type: str, db: Session) -> Board:
    """Raises RuntimeError if a board with that serial number already exists."""
    if db.get(Board, serial_number) is not None:
        raise RuntimeError(f"Board '{serial_number}' already exists in database")
    board = Board(serial_number=serial_number, type=type)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update_board(serial_number: str, data: dict, db: Session) -> Board:
    """Raises RuntimeError if the board is not found."""
    board = db.get(Board, serial_number)
    if board is None:
        raise RuntimeError(f"Board '{serial_number}' not found in database")
    for key, value in data.items():
        setattr(board, key, value)
    db.commit()
    db.refresh(board)
    return board


def delete_board(serial_number: str, db: Session) -> None:
    """Raises RuntimeError if the board is not found."""
    board = db.get(Board, serial_number)
    if board is None:
        raise RuntimeError(f"Board '{serial_number}' not found in database")
    db.delete(board)
    db.commit()
    print("Deleted Successfully")


if __name__ == "__main__":
    try:
        from backend.services.config_loader import load_all_configs
        from backend.database import engine
    except ImportError:
        from services.config_loader import load_all_configs
        from database import engine
    """
    configs = load_all_configs()
    VALID_SN   = "066FFF3632524B3043205333"
    INVALID_SN = "INVALID_SERIAL_NUMBER"

    # Test 1: get_all
    print("--- Test 1: get_all ---")
    devices = get_all(configs)
    print(f"PASS — {len(devices)} device(s) found:")
    for d in devices:
        print(f"  {d.name} | {d.target.serial_number}")

    # Test 2: get_by_serial — valid
    print("\n--- Test 2: get_by_serial (valid) ---")
    try:
        device = get_by_serial(configs, VALID_SN)
        print(f"PASS — found '{device.name}'")
    except RuntimeError as e:
        print(f"FAIL — {e}")

    # Test 3: get_by_serial — invalid
    print("\n--- Test 3: get_by_serial (invalid) ---")
    try:
        get_by_serial(configs, INVALID_SN)
        print("FAIL — should have raised RuntimeError")
    except RuntimeError as e:
        print(f"PASS — correctly rejected: {e}")

    # Test 4: get_board — valid
    print("\n--- Test 4: get_board (valid) ---")
    with Session(engine) as db:
        try:
            board = get_board(VALID_SN, db)
            print(f"PASS — board: serial={board.serial_number} | type={board.type} | status={board.status}")
        except RuntimeError as e:
            print(f"FAIL — {e}")

    # Test 5: get_board — invalid
    print("\n--- Test 5: get_board (invalid) ---")
    with Session(engine) as db:
        try:
            get_board(INVALID_SN, db)
            print("FAIL — should have raised RuntimeError")
        except RuntimeError as e:
            print(f"PASS — correctly rejected: {e}")
    """

    with Session(engine) as db_session:
        update_board("066FFF3632524B3043205333", {"status" : "idle", "openocd_pid" : None}, db_session)
        update_board("066DFF535550755187063847", {"status" : "idle", "openocd_pid" : None}, db_session)