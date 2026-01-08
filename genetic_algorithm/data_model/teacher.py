from enum import Enum
from typing import Optional, List
from pydantic import *

from .location import Departments
from .time_models import *


class Teacher_unavailabities(BaseModel):
    id: PositiveInt = Field(..., description="id of teacher unavailabities must be declared")
    teacher_id: PositiveInt = Field(..., description="id of teacher id must be declared")
    weekday: Weekdays = Field(..., description="weekdays must be declared")
    start_time: time = Field(..., description="start time must be declared")
    end_time: time = Field(..., description="end time must be declared")
    reason: Optional[str]=None

class Teachers(BaseModel):
    id: PositiveInt = Field(..., description="id of teacher must be declared")
    first_name: str = Field(..., description="first name of teacher must be declared")
    last_name: str = Field(..., description="last name of teacher must be declared")
    department_id: Optional[PositiveInt] = None
    accessibility: Optional[dict[str,bool]]=None
