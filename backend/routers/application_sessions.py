from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import Any

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User

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
    # TODO: call application_session_service.get_by_id(db, id)
    #       Check session.user_id == current_user.id.
    #       Return 404 if not found OR not owned.
    #       Build full response: app_name from config, gdb_host/port from RaspberryPi,
    #       time_left from end_time, control_devices with elf lists and button panels.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("", response_model=ApplicationSessionOut, status_code=status.HTTP_201_CREATED)
def start_application_session(
    body: StartAppSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call application_session_service.start(db, application_id=body.application_id, user_id=current_user.id)
    # TODO: service raises LookupError → 404 (application not found)
    # TODO: service raises ConflictError → 409 (one or more required boards already occupied)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/{id}/end", response_model=MessageOut)
def end_application_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call application_session_service.end(db, session_id=id)
    #       Check ownership (return 404 if not found or not owned).
    # TODO: service raises LookupError → 404
    # TODO: service raises ValueError → 409 (session already ended or cancelled)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/{id}/flash", response_model=MessageOut)
def flash_firmware(
    id: int,
    body: FlashRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call application_session_service.flash(db, session_id=id, elf_filename=body.elf_filename)
    #       Check ownership and that session.status == "active".
    # TODO: service raises LookupError → 404
    # TODO: service raises ValueError → 409 (session not active)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("/{id}/command", response_model=MessageOut)
def send_command(
    id: int,
    body: CommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    # TODO: call application_session_service.send_command(db, session_id=id, uart_command=body.uart_command)
    #       Check ownership and that session.status == "active".
    # TODO: service raises LookupError → 404
    # TODO: service raises ValueError → 409 (session not active)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
