from datetime import datetime, time, timedelta

def calculate_duration(quantity: int, pattern: str) -> int:
    """
    Calculate duration in days based on quantity and dosage pattern (e.g., '1-0-1').
    """
    if not pattern or not quantity:
        return 0
    
    try:
        # Check for standard patterns
        daily_count = 0
        pattern = pattern.strip().upper()
        
        if pattern == 'OD':
            daily_count = 1
        elif pattern == 'BD' or pattern == 'BID':
            daily_count = 2
        elif pattern == 'TDS' or pattern == 'TID':
            daily_count = 3
        elif pattern == 'QID':
            daily_count = 4
        elif '-' in pattern:
            parts = pattern.split('-')
            daily_count = sum(int(p) for p in parts if p.isdigit())
        else:
            return 0 # Unknown pattern
            
        if daily_count == 0:
            return 0
            
        return max(1, quantity // daily_count)
    except:
        return 0

def get_dosage_timings(pattern: str, instructions: str = "After food"):
    """
    Return a list of specific times (datetime.time) for the reminders based on pattern and instructions.
    """
    timings = []
    pattern = pattern.strip().upper()
    instructions = instructions.lower()
    
    is_before_food = "before food" in instructions
    
    # Define slots
    # Before food: 9:00 AM, 1:00 PM, 7:00 PM
    # After food: 10:00 AM (midpoint of 9:30-10:30), 3:00 PM (midpoint of 2:30-3:30), 9:00 PM (midpoint of 8:30-9:30)
    
    morning_time = time(9, 0) if is_before_food else time(10, 0)
    afternoon_time = time(13, 0) if is_before_food else time(15, 0)
    evening_time = time(19, 0) if is_before_food else time(21, 0)
    
    morning = False
    afternoon = False
    evening = False
    
    if pattern == 'OD':
        morning = True
    elif pattern == 'BD' or pattern == 'BID':
        morning = True
        evening = True
    elif pattern == 'TDS' or pattern == 'TID':
        morning = True
        afternoon = True
        evening = True
    elif '-' in pattern:
        parts = pattern.split('-')
        # Assuming 3 parts: morn-noon-eve (e.g. 1-0-1)
        # If 4 parts? usually 3.
        if len(parts) >= 1 and int(parts[0]) > 0: morning = True
        if len(parts) >= 2 and int(parts[1]) > 0: afternoon = True
        if len(parts) >= 3 and int(parts[2]) > 0: evening = True
    
    if morning: timings.append(morning_time)
    if afternoon: timings.append(afternoon_time)
    if evening: timings.append(evening_time)
    
    return timings
