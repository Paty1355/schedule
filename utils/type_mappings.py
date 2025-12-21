from typing import List
from app_config.constants import COURSE_TO_ROOM_TYPE_MAPPING



def get_allowed_room_types(course_type: str) -> List[str]:
    """
    returns list of allowed room types for given course type
    """
    return COURSE_TO_ROOM_TYPE_MAPPING.get(course_type, [])



def is_room_type_compatible(course_type: str, room_type: str) -> bool:
    """
    checks if room type is compatible with course type
    """
    allowed = get_allowed_room_types(course_type)
    return room_type in allowed