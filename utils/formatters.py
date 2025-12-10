from datetime import time, datetime
from app_config.constants import WEEKDAY_LABELS_PL, WEEK_PARITY_LABELS_PL


def format_time_slot(start_time: time, end_time: time) -> str:
    """formats a time slot as a string HH:MM-HH:MM"""
    return f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"


def format_time_short(time_obj: time) -> str:
    """formats time as HH:MM"""
    return time_obj.strftime('%H:%M')


def parse_time(time_str: str) -> time:
    """
    parses a time string in various formats
    supports: HH:MM:SS, HH:MM
    """
    time_str = str(time_str).strip()
    if '.' in time_str:
        time_str = time_str.split('.')[0]
    
    for fmt in ['%H:%M:%S', '%H:%M']:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    
    raise ValueError(f"Nie można sparsować czasu: {time_str}")


def format_weekday_pl(weekday: str) -> str:
    """returns the Polish name of the weekday"""
    return WEEKDAY_LABELS_PL.get(weekday, weekday)


def format_parity_pl(parity: str) -> str:
    """returns the Polish name of the parity"""
    return WEEK_PARITY_LABELS_PL.get(parity, parity)


def format_teacher_name(first_name: str, last_name: str) -> str:
    """formats the full name of the teacher"""
    return f"{first_name} {last_name}"


def format_full_name_short(first_name: str, last_name: str) -> str:
    """formats as: F. Lastname"""
    return f"{first_name[0]}. {last_name}"