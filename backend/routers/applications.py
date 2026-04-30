from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.services.session.session import get_active_by_board, get_reserved_by_board

router = APIRouter(prefix="/applications", tags=["applications"])


# ---------- Schemas ----------

class ApplicationSummaryOut(BaseModel):
    id: int
    name: str
    status: str
    description: str


class ApplicationDetailOut(BaseModel):
    json_path: str
    status: str
    descriptor: dict


class SessionConfigOut(BaseModel):
    json_path: str
    min_duration_minutes: int
    max_duration_minutes: int
    slot_step_minutes: int


# ---------- Helpers ----------

def _board_status(serial_number: str, db: Session) -> str:
    if get_active_by_board(db, serial_number):
        return "occupied"
    if get_reserved_by_board(db, serial_number):
        return "reserved"
    return "free"


def _app_status(cfg, db: Session) -> str:
    """Occupied/reserved if target OR control board is in use; free otherwise."""
    if get_active_by_board(db, cfg.target.serial_number):
        return "occupied"
    if cfg.is_application and get_active_by_board(db, cfg.control.serial_number):
        return "occupied"
    if get_reserved_by_board(db, cfg.target.serial_number):
        return "reserved"
    if cfg.is_application and get_reserved_by_board(db, cfg.control.serial_number):
        return "reserved"
    return "free"


def _resolve(raw: str, configs_ids: dict) -> str:
    """Accept an integer ID string or a literal json_path."""
    try:
        json_path = configs_ids.get(int(raw))
        if json_path is None:
            raise RuntimeError(f"ID {raw} not found")
        return json_path
    except ValueError:
        return raw


def _build_descriptor(cfg) -> dict:
    return {
        "name":        cfg.name,
        "description": cfg.description,
        "main_device": {
            "device_id":          cfg.target.serial_number,
            "role":               "Target board",
            "openocd_config_path": cfg.target.openocd_cfg,
            "camera":             {"enabled": cfg.camera is not None, "stream_path": None},
        },
        "control_devices": [
            {
                "device_id": cfg.control.serial_number,
                "label":     cfg.name,
                "available_elfs": [
                    {
                        "filename": fw.bin_file,
                        "name":     fw.name,
                        "buttons": [
                            {"label": b.label, "uart_command": b.command}
                            for b in fw.buttons
                        ],
                    }
                    for fw in cfg.control.firmwares
                ],
            }
        ] if cfg.is_application else [],
    }


# ---------- Endpoints ----------

@router.get("", response_model=list[ApplicationSummaryOut])
def list_applications(request: Request, db: Session = Depends(get_session)):
    configs = request.app.state.configs
    configs_ids = request.app.state.configs_ids
    path_to_id = {v: k for k, v in configs_ids.items()}
    return [
        {
            "id":          path_to_id[path],
            "name":        cfg.name,
            "status":      _app_status(cfg, db),
            "description": cfg.description,
        }
        for path, cfg in configs.items()
        if cfg.is_application
    ]


# /config must be registered before the /{json_path:path} catch-all
@router.get("/{json_path:path}/config", response_model=SessionConfigOut)
def get_application_config(json_path: str, request: Request, db: Session = Depends(get_session)):
    configs = request.app.state.configs
    configs_ids = request.app.state.configs_ids
    try:
        resolved = _resolve(json_path, configs_ids)
        if configs.get(resolved) is None:
            raise RuntimeError()
        return {
            "json_path":             resolved,
            "min_duration_minutes":  15,
            "max_duration_minutes":  60,
            "slot_step_minutes":     15,
        }
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")


@router.get("/{json_path:path}", response_model=ApplicationDetailOut)
def get_application(json_path: str, request: Request, db: Session = Depends(get_session)):
    configs = request.app.state.configs
    configs_ids = request.app.state.configs_ids
    try:
        resolved = _resolve(json_path, configs_ids)
        cfg = configs.get(resolved)
        if cfg is None:
            raise RuntimeError()
        return {
            "json_path":  resolved,
            "status":     _app_status(cfg, db),
            "descriptor": _build_descriptor(cfg),
        }
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
