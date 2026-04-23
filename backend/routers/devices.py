from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session

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
    # TODO: devices_service.get_all needs to be updated to use absolute imports
    #       (from backend.models import Board) before this call works.
    #       Also needs to load description from the device config JSON file.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{id}", response_model=DeviceDetailOut)
def get_device(id: int, db: Session = Depends(get_session)):
    # TODO: devices_service.get_by_id exists but needs absolute imports fix.
    #       Also needs to load the hardware descriptor from the config JSON file.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{id}/config", response_model=SessionConfigOut)
def get_device_config(id: int, db: Session = Depends(get_session)):
    # TODO: call config_service.get_device_config(id)
    #       Reads min/max duration and slot step from the device descriptor JSON.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
