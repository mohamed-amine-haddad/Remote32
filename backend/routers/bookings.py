from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.stub.bookings as bookings_service

router = APIRouter(prefix="/bookings", tags=["bookings"])

VALID_RESOURCE_TYPES = {"application"}


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
    try:
        return bookings_service.get_by_resource(db, resource_type, resource_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    try:
        return bookings_service.create(
            db, current_user.id, body.resource_type, body.resource_id,
            body.date, body.start_time, body.duration_minutes,
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    # TODO: except ConflictError → 409 when real service implements overlap detection
