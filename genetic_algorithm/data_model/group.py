from datetime import time
from enum import Enum
from typing import Optional, List
from pydantic import *
from .time_models import *


class GroupUnavailabilities(BaseModel):
    id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    group_id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    weekday: Weekdays = Field(..., description="Weekdays of group unavailabilities must be declared")
    start_time: time = Field(..., description="start time of group unavailabilities must be declared")
    end_time: time = Field(..., description="end time of group unavailabilities must be declared")
    reason: Optional[str]= None

class Groups(BaseModel):
    id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    code: str = Field(..., description="group code of group unavailabilities must be declared")
    name: str = Field(..., description="name of group unavailabilities must be declared")
    department_id: PositiveInt = Field(..., description="department id of the building must be declared ")
    students_count: PositiveInt = Field(..., description="students count of group unavailabilities must be declared")
    accessibility_requirements: Optional[dict[str,bool]]=None
    parent_group_id: Optional[PositiveInt]=None

    # @field_validator("students_count")
    # def check_students_count(cls, v):
    #     if v <1:
    #         raise ValueError("students count must be greater than 0")

