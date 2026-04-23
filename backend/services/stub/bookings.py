# STUB — replace body of each function with real DB queries when
# backend/services/bookings.py is ready. Change the import in routers/bookings.py
# from backend.services.stub.bookings to backend.services.bookings.

_RESERVATIONS = [
    {"date": "2026-04-10", "start": "09:00", "end": "10:00", "status": "reserved"},
    {"date": "2026-04-10", "start": "14:00", "end": "14:30", "status": "occupied"},
    {"date": "2026-04-11", "start": "10:00", "end": "11:00", "status": "reserved"},
    {"date": "2026-04-13", "start": "08:00", "end": "09:00", "status": "occupied"},
]


def get_by_resource(session, resource_type: str, resource_id: int) -> list[dict]:
    return _RESERVATIONS


def create(session, user_id: int, resource_type: str, resource_id: int,
           date: str, start_time: str, duration_minutes: int) -> dict:
    h, m = map(int, start_time.split(":"))
    end_total = h * 60 + m + duration_minutes
    end_time = f"{end_total // 60:02d}:{end_total % 60:02d}"
    return {"date": date, "start": start_time, "end": end_time, "status": "reserved"}
