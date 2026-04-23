from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.stub.device_sessions as device_sessions_service

router = APIRouter(prefix="/sessions/device", tags=["device-sessions"])


# ---------- Schemas ----------

class DeviceSessionOut(BaseModel):
    id: int
    device_name: str
    status: str      # reserved | active | ended | cancelled
    started_at: str  # "HH:MM"
    ends_at: str     # "HH:MM"
    time_left: str   # "MM:SS" countdown — computed server-side
    gdb_host: str
    gdb_port: str


class StartDeviceSessionRequest(BaseModel):
    board_id: int


class MessageOut(BaseModel):
    message: str


# ---------- Endpoints ----------

@router.get("/{id}", response_model=DeviceSessionOut)
def get_device_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return device_sessions_service.get_by_id(db, id, current_user.id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("", response_model=DeviceSessionOut, status_code=status.HTTP_201_CREATED)
def start_device_session(
    body: StartDeviceSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return device_sessions_service.start(db, body.board_id, current_user.id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/end", response_model=MessageOut)
def end_device_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        message = device_sessions_service.end(db, id, current_user.id)
        return {"message": message}
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
