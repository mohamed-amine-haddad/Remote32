from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlmodel import Session
from datetime import datetime, timedelta

from backend.database import get_session
from backend.services.session.session import get_active_by_board, get_reserved_by_board

_STATUS_WINDOW = timedelta(minutes=10)

router = APIRouter(prefix="/devices", tags=["devices"])


class DeviceSummaryOut(BaseModel):
    id: int
    name: str
    status: str
    description: str


def _board_status(serial_number: str, db: Session) -> str:
    if get_active_by_board(db, serial_number):
        return "occupied"
    now = datetime.now()
    if get_reserved_by_board(db, serial_number, starts_before=now + _STATUS_WINDOW, ends_after=now):
        return "reserved"
    return "free"


@router.get("", response_model=list[DeviceSummaryOut])
def list_devices(request: Request, db: Session = Depends(get_session)):
    configs = request.app.state.configs
    configs_ids = request.app.state.configs_ids
    path_to_id = {v: k for k, v in configs_ids.items()}
    return [
        {
            "id":          path_to_id[path],
            "name":        cfg.name,
            "status":      _board_status(cfg.target.serial_number, db),
            "description": cfg.description,
        }
        for path, cfg in configs.items()
        if not cfg.is_application
    ]
