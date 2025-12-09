import urllib.parse
from datetime import datetime, timedelta

def generate_google_calendar_link(title: str, start_dt: datetime, end_dt: datetime, details: str) -> str:
    """
    Generate a Google Calendar event link.
    Format: https://calendar.google.com/calendar/render?action=TEMPLATE&text=...
    Dates format: YYYYMMDDTHHMMSSZ
    """
    def format_date(dt):
        return dt.strftime('%Y%m%dT%H%M%S')

    base_url = "https://calendar.google.com/calendar/render"
    params = {
        "action": "TEMPLATE",
        "text": f"Medicine: {title}",
        "dates": f"{format_date(start_dt)}/{format_date(end_dt)}",
        "details": details,
        "sf": "true",
        "output": "xml"
    }
    
    return f"{base_url}?{urllib.parse.urlencode(params)}"
