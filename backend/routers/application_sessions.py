from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import Any

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.application_sessions as application_sessions_service

router = APIRouter(prefix="/sessions/application", tags=["application-sessions"])


# ---------- Schemas ----------

class ApplicationSessionOut(BaseModel):
    id: int
    app_name: str
    status: str
    started_at: str
    ends_at: str
    time_left: str
    gdb_host: str
    gdb_port: int
    control_devices: list[Any]


class StartAppSessionRequest(BaseModel):
    json_path: str


class FlashRequest(BaseModel):
    elf_filename: str


class CommandRequest(BaseModel):
    uart_command: str


class UartSendRequest(BaseModel):
    text: str


class UartMessage(BaseModel):
    id: int
    direction: str
    text: str
    timestamp: str


class UartMessagesOut(BaseModel):
    messages: list[UartMessage]


class MessageOut(BaseModel):
    message: str


class CameraOut(BaseModel):
    stream_url: str


# ---------- Endpoints ----------

@router.get("/{id}", response_model=ApplicationSessionOut)
def get_application_session(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        configs = request.app.state.configs
        return application_sessions_service.get_by_id(db, id, current_user.id, configs)
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("", response_model=ApplicationSessionOut, status_code=status.HTTP_201_CREATED)
def start_application_session(
    body: StartAppSessionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        configs = request.app.state.configs
        return application_sessions_service.start(configs, db, body.json_path, current_user.id)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/end", response_model=MessageOut)
def end_application_session(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        configs = request.app.state.configs
        message = application_sessions_service.end(db, configs, id, current_user.id)
        return {"message": message}
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{id}/uart/messages", response_model=UartMessagesOut)
def get_uart_messages(
    id: int,
    since_id: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return application_sessions_service.get_uart_messages(db, id, since_id)
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.get("/{id}/camera", response_model=CameraOut)
def get_camera_stream(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        configs = request.app.state.configs
        url = application_sessions_service.camera_stream(db, id, current_user.id, configs)
        return {"stream_url": url}
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{id}/uart/send", response_model=MessageOut)
def uart_send(
    id: int,
    body: UartSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        message = application_sessions_service.uart_send(db, id, body.text)
        return {"message": message}
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
