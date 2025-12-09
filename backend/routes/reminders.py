from fastapi import APIRouter, Depends, HTTPException, Body
from supabase_client import get_supabase_client
from .auth import get_current_user
from utils.calendar_generator import generate_google_calendar_link
from utils.dosage_calculator import get_dosage_timings
from datetime import datetime, timedelta

router = APIRouter()
supabase = get_supabase_client()

@router.post("/reminders")
async def create_reminder(
    medicine_name: str = Body(...),
    dosage_pattern: str = Body(...),
    instructions: str = Body("After food"),
    start_date: str = Body(...), # YYYY-MM-DD
    duration_days: int = Body(5),
    user_id: str = Depends(get_current_user)
):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=duration_days)
        
        # Save to DB
        # Note: In the schema I generated earlier, 'reminders' table has columns:
        # user_id, medicine_id (nullable), reminder_time, days_of_week
        # This route might be slightly different from the basic schema but we'll adapt.
        # We will just generate the link here as requested mostly.
        
        # Link generation
        timings = get_dosage_timings(dosage_pattern, instructions)
        calendar_links = []
        
        for t in timings:
            # Create a start datetime for the first occurrence
            event_start = datetime.combine(start_dt.date(), t)
            event_end = event_start + timedelta(minutes=30)
            
            link = generate_google_calendar_link(
                title=f"{medicine_name} ({dosage_pattern})",
                start_dt=event_start,
                end_dt=event_end,
                details=f"Instructions: {instructions}"
            )
            calendar_links.append(link)

        # For the sake of the DB, we store the config
        reminder_data = {
            "user_id": user_id,
            "medicine_id": None, # Optional if not linked directly to a med ID in this request
            "reminder_time": timings[0].strftime("%H:%M:%S") if timings else "09:00:00",
            "is_active": True,
            "days_of_week": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] 
        }
        supabase.table("reminders").insert(reminder_data).execute()

        return {
            "message": "Reminder created",
            "calendar_links": calendar_links
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
