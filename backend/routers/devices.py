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


# ---------- Endpoints ----------

@router.get("", response_model=list[DeviceSummaryOut])
def list_devices(db: Session = Depends(get_session)):
    return devices_service.get_all(db)
