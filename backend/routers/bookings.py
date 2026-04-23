from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User

router = APIRouter(prefix="/bookings", tags=["bookings"])

VALID_RESOURCE_TYPES = {"device", "application"}


# ---------- Schemas ----------

class BookingOut(BaseModel):
    date: str   # "YYYY-MM-DD"
    start: str  # "HH:MM"
    end: str    # "HH:MM"
    status: str # "reserved" | "occupied"


class CreateBookingRequest(BaseModel):
    resource_type: str       # "device" | "application"
    resource_id: int
    date: str                # "YYYY-MM-DD"
    start_time: str          # "HH:MM"
    duration_minutes: int


# ---------- Endpoints ----------

@router.get("", response_model=list[BookingOut])
def list_bookings(
    resource_type: str = Query(...),
    resource_id: int = Query(...),
    db: Session = Depends(get_session),
):
    if resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"resource_type must be one of: {', '.join(VALID_RESOURCE_TYPES)}",
        )
    # TODO: call bookings_service.get_by_resource(db, resource_type, resource_id)
    #       Returns all reserved/occupied slots for the given resource.
    #       Raise 404 if the resource_id does not correspond to a known device/application.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    body: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if body.resource_type not in VALID_RESOURCE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"resource_type must be one of: {', '.join(VALID_RESOURCE_TYPES)}",
        )
    # TODO: call bookings_service.create(db, current_user.id, body.resource_type,
    #           body.resource_id, body.date, body.start_time, body.duration_minutes)
    # TODO: service raises LookupError → 404 (resource not found)
    # TODO: service raises ValueError → 400 (invalid date/time)
    # TODO: service raises ConflictError → 409 (time overlap with existing reservation)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
