from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session
from datetime import datetime

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.stub.bookings as bookings_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


# ---------- Schemas ----------

class BookingOut(BaseModel):
    date: str   # "YYYY-MM-DD"
    start: str  # "HH:MM"
    end: str    # "HH:MM"
    status: str # "reserved" | "occupied"


class CreateBookingRequest(BaseModel):
    json_path: str       # e.g. "configs/applications/test_button.json"
    start_time: datetime
    duration_minutes: int


# ---------- Endpoints ----------

@router.get("", response_model=list[BookingOut])
def list_bookings(
    json_path: str = Query(...),
    db: Session = Depends(get_session),
):
    try:
        return bookings_service.get_by_resource(db, json_path)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    body: CreateBookingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    try:
        return bookings_service.create(
            db, current_user.id, body.json_path,
            body.start_time, body.duration_minutes,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
