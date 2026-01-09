from datetime import time
from enum import Enum
from typing import Optional, List
from pydantic import *


from genetic_algorithm.data_model.location import Rooms
from genetic_algorithm.data_model.group import Groups
from genetic_algorithm.data_model.teacher import Teachers
from genetic_algorithm.data_model.time_models import *


class CourseType(str, Enum):
    lecture = 'lecture'
    exercise= 'exercise'
    seminar = 'seminar'
    project='project'
    lab='lab'
    computer_lab='computer_lab'
    chemistry_lab='chemistry_lab'
    physics_lab='physics_lab'
    biology_lab='biology_lab'
    language_lab='language_lab'
    workshop='workshop'
    gym_class='gym_class'
    other='other'


class Course(BaseModel):
    id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    code: str = Field(..., description="code of group unavailabilities must be declared")
    name: str = Field(..., description="name of group unavailabilities must be declared")
    departament_id: Optional[PositiveInt] = None
    type: CourseType
    hours_per_semester: PositiveInt = Field(..., description="hours per semester must be declared")


class Course_assignments(BaseModel):
    id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    course_id: Course
    group_id: Groups
    teacher_id: Teachers
    semester: str = Field(..., description="semester of group unavailabilities must be declared")
    note: Optional[str] = None


class Assignment(BaseModel):
    id: PositiveInt = Field(..., description="id of group unavailabilities must be declared")
    course_assignments_id: Course_assignments = Field(..., description="id of group unavailabilities must be declared")
    room_id: Rooms = Field(..., description="id of room unavailabilities must be declared")
    weekday: Weekdays = Field(..., description="weekdays of group unavailabilities must be declared")
    time_slot_id: Time_slots = Field(..., description="id of time slot unavailabilities must be declared")
    week_parity: Week_parity = Field(..., description="week_parity of group unavailabilities must be declared")
    note: Optional[str] = None


