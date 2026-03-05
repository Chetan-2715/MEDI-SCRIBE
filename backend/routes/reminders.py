from fastapi import APIRouter, Depends, HTTPException, Body
from db import query, execute
from .auth import get_current_user
from utils.calendar_generator import generate_google_calendar_link
from utils.dosage_calculator import get_dosage_timings
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/reminders")
async def create_reminder(
    medicine_name: str = Body(...),
    dosage_pattern: str = Body(...),
    instructions: str = Body("After food"),
    start_date: str = Body(...),
    duration_days: int = Body(5),
    user_id: str = Depends(get_current_user)
):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=duration_days)

        # Generate calendar links
        timings = get_dosage_timings(dosage_pattern, instructions)
        calendar_links = []

        for t in timings:
            event_start = datetime.combine(start_dt.date(), t)
            event_end = event_start + timedelta(minutes=30)

            link = generate_google_calendar_link(
                title=f"{medicine_name} ({dosage_pattern})",
                start_dt=event_start,
                end_dt=event_end,
                details=f"Instructions: {instructions}"
            )
            calendar_links.append(link)

        # Save reminder to DB
        reminder_time = timings[0].strftime("%H:%M:%S") if timings else "09:00:00"
        execute(
            """INSERT INTO reminders (user_id, reminder_time, is_active, days_of_week)
               VALUES (%s, %s, %s, %s)""",
            (user_id, reminder_time, True, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        )

        return {
            "message": "Reminder created",
            "calendar_links": calendar_links
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
