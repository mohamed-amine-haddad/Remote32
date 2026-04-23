from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session

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
    # TODO: call applications_service.get_all(db)
    #       Applications are defined in backend/configs/applications/ JSON files.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{id}", response_model=ApplicationDetailOut)
def get_application(id: int, db: Session = Depends(get_session)):
    # TODO: call applications_service.get_by_id(id)
    #       Reads the application config JSON and resolves the boards' current status from DB.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{id}/config", response_model=SessionConfigOut)
def get_application_config(id: int, db: Session = Depends(get_session)):
    # TODO: call config_service.get_application_config(id)
    #       Reads min/max duration and slot step from the application descriptor JSON.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
