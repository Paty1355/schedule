from datetime import time
from enum import Enum
from typing import Optional, List
from pydantic import *

class Week_parity(str, Enum):
    odd = 'odd'
    even = 'even'
    both = 'both'

class Weekdays(str, Enum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'

class Time_slots(BaseModel):
    id: PositiveInt = Field(..., description="id of time slots must be declared")
    start_time: time = Field(..., description="start time of time slots must be declared")
    end_time: time = Field(..., description="end time of time slots must be declared")
    slot_order: PositiveInt = Field(..., description="order of time slots must be declared")
    duration_minutes: Optional[PositiveInt]=None
