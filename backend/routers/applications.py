from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
import backend.services.stub.applications as applications_service

router = APIRouter(prefix="/applications", tags=["applications"])


# ---------- Schemas ----------

class ApplicationSummaryOut(BaseModel):
    id: int
    name: str
    status: str
    description: str


class ApplicationDetailOut(BaseModel):
    id: int
    status: str
    descriptor: dict


class SessionConfigOut(BaseModel):
    min_duration_minutes: int
    max_duration_minutes: int
    slot_step_minutes: int


# ---------- Endpoints ----------

@router.get("", response_model=list[ApplicationSummaryOut])
def list_applications(db: Session = Depends(get_session)):
    return applications_service.get_all(db)


@router.get("/{id}", response_model=ApplicationDetailOut)
def get_application(id: int, db: Session = Depends(get_session)):
    try:
        return applications_service.get_by_id(db, id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")


@router.get("/{id}/config", response_model=SessionConfigOut)
def get_application_config(id: int, db: Session = Depends(get_session)):
    try:
        return applications_service.get_config(db, id)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
