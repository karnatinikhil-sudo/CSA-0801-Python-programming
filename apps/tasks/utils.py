import re
import datetime
from django.utils import timezone

def parse_natural_language_task(text):
    """
    Parses a natural-language input string into task fields:
    - title
    - priority (HIGH, MEDIUM, LOW)
    - due_date
    - due_time
    - recurrence (NONE, DAILY, WEEKLY, MONTHLY)
    - category
    """
    cleaned = text.strip()
    priority = 'MEDIUM'
    category = 'Work'
    recurrence = 'NONE'
    due_date = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
    due_time = None

    # Priority extraction
    if re.search(r'\b(urgent|high priority|critical|p1|asap)\b', cleaned, re.IGNORECASE):
        priority = 'HIGH'
        cleaned = re.sub(r'\b(urgent|high priority|critical|p1|asap)\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\b(low priority|minor|someday|p3)\b', cleaned, re.IGNORECASE):
        priority = 'LOW'
        cleaned = re.sub(r'\b(low priority|minor|someday|p3)\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\b(medium priority|normal|p2)\b', cleaned, re.IGNORECASE):
        priority = 'MEDIUM'
        cleaned = re.sub(r'\b(medium priority|normal|p2)\b', '', cleaned, flags=re.IGNORECASE)

    # Recurrence extraction
    if re.search(r'\b(every day|daily)\b', cleaned, re.IGNORECASE):
        recurrence = 'DAILY'
        cleaned = re.sub(r'\b(every day|daily)\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\b(every week|weekly|every (monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b', cleaned, re.IGNORECASE):
        recurrence = 'WEEKLY'
        cleaned = re.sub(r'\b(every week|weekly|every (monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\b(every month|monthly)\b', cleaned, re.IGNORECASE):
        recurrence = 'MONTHLY'
        cleaned = re.sub(r'\b(every month|monthly)\b', '', cleaned, flags=re.IGNORECASE)

    # Category extraction
    cat_match = re.search(r'#(\w+)', cleaned)
    if cat_match:
        tag = cat_match.group(1).capitalize()
        if tag in ['Work', 'Personal', 'Health', 'Study', 'Finance', 'Other']:
            category = tag
        cleaned = re.sub(r'#\w+', '', cleaned)

    # Relative Date extraction
    today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
    if re.search(r'\btomorrow\b', cleaned, re.IGNORECASE):
        due_date = today + datetime.timedelta(days=1)
        cleaned = re.sub(r'\btomorrow\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\btoday\b', cleaned, re.IGNORECASE):
        due_date = today
        cleaned = re.sub(r'\btoday\b', '', cleaned, flags=re.IGNORECASE)
    elif re.search(r'\bnext week\b', cleaned, re.IGNORECASE):
        due_date = today + datetime.timedelta(days=7)
        cleaned = re.sub(r'\bnext week\b', '', cleaned, flags=re.IGNORECASE)
    else:
        # Check for weekday (e.g., "on friday", "this friday", "next monday")
        weekday_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        day_match = re.search(r'\b(?:on|next|this)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', cleaned, re.IGNORECASE)
        if day_match:
            target_wd = weekday_map[day_match.group(1).lower()]
            current_wd = today.weekday()
            days_ahead = (target_wd - current_wd) % 7
            if days_ahead == 0:
                days_ahead = 7
            due_date = today + datetime.timedelta(days=days_ahead)
            cleaned = re.sub(r'\b(?:on|next|this)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', cleaned, flags=re.IGNORECASE)

    # Time extraction (e.g., "at 5pm", "5:30 pm", "17:00", "at 9 am")
    time_match = re.search(r'\b(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', cleaned, re.IGNORECASE)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = time_match.group(3).lower()
        if ampm == 'pm' and hour < 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        due_time = datetime.time(hour, minute)
        cleaned = re.sub(r'\b(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)\b', '', cleaned, flags=re.IGNORECASE)
    else:
        # 24h format (e.g., "at 14:30" or "18:00")
        time_24_match = re.search(r'\b(?:at\s+)?([01]?\d|2[0-3]):([0-5]\d)\b', cleaned, re.IGNORECASE)
        if time_24_match:
            hour = int(time_24_match.group(1))
            minute = int(time_24_match.group(2))
            due_time = datetime.time(hour, minute)
            cleaned = re.sub(r'\b(?:at\s+)?[01]?\d|2[0-3]:[0-5]\d\b', '', cleaned, flags=re.IGNORECASE)

    # Clean leftover whitespace and punctuation
    cleaned_title = re.sub(r'\s+', ' ', cleaned).strip(' -.,;:_')
    if not cleaned_title:
        cleaned_title = text.strip()

    return {
        'title': cleaned_title,
        'priority': priority,
        'category': category,
        'recurrence': recurrence,
        'due_date': due_date.isoformat(),
        'due_time': due_time.strftime('%H:%M') if due_time else '',
    }


def suggest_priority(due_date, due_time=None):
    """
    Intelligently suggests a priority based on proximity of due date:
    - Due today or overdue -> HIGH
    - Due tomorrow or within 2 days -> MEDIUM
    - Due later -> LOW
    """
    if not due_date:
        return 'MEDIUM'
    
    today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
    if isinstance(due_date, str):
        try:
            due_date = datetime.date.fromisoformat(due_date)
        except ValueError:
            return 'MEDIUM'
            
    diff_days = (due_date - today).days
    if diff_days <= 0:
        return 'HIGH'
    elif diff_days <= 2:
        return 'MEDIUM'
    else:
        return 'LOW'
