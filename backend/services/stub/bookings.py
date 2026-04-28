# STUB — replace body of each function with real DB queries when
# backend/services/bookings.py is ready. Change the import in routers/bookings.py
# from backend.services.stub.bookings to backend.services.bookings.

_RESERVATIONS = [
    {"date": "2026-04-10", "start": "09:00", "end": "10:00", "status": "reserved"},
    {"date": "2026-04-10", "start": "14:00", "end": "14:30", "status": "occupied"},
    {"date": "2026-04-11", "start": "10:00", "end": "11:00", "status": "reserved"},
    {"date": "2026-04-13", "start": "08:00", "end": "09:00", "status": "occupied"},
]


def get_by_resource(session, json_path: str) -> list[dict]:
    return _RESERVATIONS


def create(session, user_id: int, json_path: str, start_time, duration_minutes: int) -> dict:
    end_minutes = start_time.hour * 60 + start_time.minute + duration_minutes
    return {
        "date": start_time.strftime("%Y-%m-%d"),
        "start": f"{start_time.hour:02d}:{start_time.minute:02d}",
        "end": f"{end_minutes // 60:02d}:{end_minutes % 60:02d}",
        "status": "reserved",
    }
