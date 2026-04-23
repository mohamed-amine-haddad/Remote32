from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
import backend.services.stub.devices as devices_service

router = APIRouter(prefix="/devices", tags=["devices"])


# ---------- Schemas ----------

class DeviceSummaryOut(BaseModel):
    id: int
    name: str
    status: str
    description: str


class DeviceDetailOut(BaseModel):
    id: int
    status: str
    descriptor: dict


class SessionConfigOut(BaseModel):
    min_duration_minutes: int
    max_duration_minutes: int
    slot_step_minutes: int


# ---------- Endpoints ----------

@router.get("", response_model=list[DeviceSummaryOut])
def list_devices(db: Session = Depends(get_session)):
    return devices_service.get_all(db)


@router.get("/{id}", response_model=DeviceDetailOut)
def get_device(id: int, db: Session = Depends(get_session)):
    try:
        return devices_service.get_by_id(db, id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")


@router.get("/{id}/config", response_model=SessionConfigOut)
def get_device_config(id: int, db: Session = Depends(get_session)):
    try:
        return devices_service.get_config(db, id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
