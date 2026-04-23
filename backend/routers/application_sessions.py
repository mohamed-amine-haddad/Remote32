from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import Any

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.stub.application_sessions as application_sessions_service

router = APIRouter(prefix="/sessions/application", tags=["application-sessions"])


# ---------- Schemas ----------

class ApplicationSessionOut(BaseModel):
    id: int
    app_name: str
    status: str         # reserved | active | ended | cancelled
    started_at: str     # "HH:MM"
    ends_at: str        # "HH:MM"
    time_left: str      # "MM:SS" countdown — computed server-side
    gdb_host: str
    gdb_port: str
    control_devices: list[Any]  # list of control device objects with available_elfs and buttons


class StartAppSessionRequest(BaseModel):
    application_id: int


class FlashRequest(BaseModel):
    elf_filename: str


class CommandRequest(BaseModel):
    uart_command: str


class MessageOut(BaseModel):
    message: str


# ---------- Endpoints ----------

@router.get("/{id}", response_model=ApplicationSessionOut)
def get_application_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return application_sessions_service.get_by_id(db, id, current_user.id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("", response_model=ApplicationSessionOut, status_code=status.HTTP_201_CREATED)
def start_application_session(
    body: StartAppSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return application_sessions_service.start(db, body.application_id, current_user.id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/end", response_model=MessageOut)
def end_application_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        message = application_sessions_service.end(db, id, current_user.id)
        return {"message": message}
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/flash", response_model=MessageOut)
def flash_firmware(
    id: int,
    body: FlashRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        message = application_sessions_service.flash(db, id, body.elf_filename)
        return {"message": message}
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/command", response_model=MessageOut)
def send_command(
    id: int,
    body: CommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        message = application_sessions_service.send_command(db, id, body.uart_command)
        return {"message": message}
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
