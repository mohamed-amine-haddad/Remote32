from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User

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
    # TODO: call device_session_service.get_by_id(db, id)
    #       Check session.user_id == current_user.id.
    #       Return 404 if not found OR not owned (do not leak existence to other users).
    #       Compute device_name from board, gdb_host/port from RaspberryPi, time_left from end_time.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("", response_model=DeviceSessionOut, status_code=status.HTTP_201_CREATED)
def start_device_session(
    body: StartDeviceSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call device_session_service.start(db, board_id=body.board_id, user_id=current_user.id)
    # TODO: service raises LookupError → 404 (board not found)
    # TODO: service raises ConflictError → 409 (board already has an active session)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/{id}/end", response_model=MessageOut)
def end_device_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call device_session_service.end(db, session_id=id)
    #       Check ownership before ending (return 404 if not found or not owned).
    # TODO: service raises LookupError → 404
    # TODO: service raises ValueError → 409 (session already ended or cancelled)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
