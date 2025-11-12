from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict
from typing import Optional, List, Tuple
from datetime import time
from enum import Enum
import random
import numpy as np
from collections import defaultdict
import copy

# Enums
class RoomType(str, Enum):
    LECTURE_HALL = 'lecture_hall'
    LAB = 'lab'
    SEMINAR_ROOM = 'seminar_room'
    CLASSROOM = 'classroom'
    AUDITORIUM = 'auditorium'
    COMPUTER_LAB = 'computer_lab'
    OTHER = 'other'
    GYM = 'gym'

class CourseType(str, Enum):
    LECTURE = 'lecture'
    LAB = 'lab'
    SEMINAR = 'seminar'
    PROJECT = 'project'
    EXERCISE = 'exercise'

class WeekParity(str, Enum):
    ODD = 'odd'
    EVEN = 'even'
    BOTH = 'both'

class Weekday(str, Enum):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'

class AccessibilityFeature(str, Enum):
    WHEELCHAIR_ACCESS = 'wheelchair_access'
    LIFT = 'lift'
    HEARING_AID = 'hearing_aid'
    BRAILLE = 'braille'
    LOW_VISION_SUPPORT = 'low_vision_support'

# Pydantic Models z ConfigDict (v2)
class Department(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1)

class Building(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    name: str
    address: Optional[str] = None
    department_id: Optional[int] = None

class Room(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    building_id: int
    code: str
    name: Optional[str] = None
    capacity: int = Field(gt=0)
    type: RoomType
    note: Optional[str] = None
    equipment: dict = Field(default_factory=dict)
    accessibility: dict = Field(default_factory=dict)
    
    @field_validator('capacity')
    @classmethod
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be positive')
        return v

class Group(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    code: str
    name: str
    department_id: int
    students_count: int = Field(gt=0)
    accessibility_requirements: dict = Field(default_factory=dict)
    parent_group_id: Optional[int] = None

class Teacher(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    first_name: str
    last_name: str
    department_id: int
    accessibility: dict = Field(default_factory=dict)
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Course(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    code: str
    name: str
    department_id: int
    type: CourseType
    hours_per_semester: int = Field(gt=0)

class CourseAssignment(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    course: Course
    group: Group
    teacher: Teacher
    semester: str
    note: Optional[str] = None

class TimeSlot(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: int
    start_time: time
    end_time: time
    slot_order: int
    duration_minutes: int = Field(gt=0)
    
    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class Assignment(BaseModel):
    """Mutable assignment for GA"""
    model_config = ConfigDict(frozen=False)
    
    id: Optional[int] = None
    course_assignment: CourseAssignment
    room: Room
    weekday: Weekday
    time_slot: TimeSlot
    week_parity: WeekParity

class TeacherUnavailability(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = None
    teacher_id: int
    weekday: Weekday
    start_time: time
    end_time: time
    reason: Optional[str] = None

class GroupUnavailability(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: Optional[int] = None
    group_id: int
    weekday: Weekday
    start_time: time
    end_time: time
    reason: Optional[str] = None