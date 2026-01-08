from enum import Enum
from typing import Optional, List
from pydantic import *

class Departments(BaseModel):
    id: PositiveInt = Field(..., description="id of department must be declared")
    code: str = Field(..., description="code of department must be declared")
    name: str = Field(..., description="name of department must be declared")

class Buildings(BaseModel):
    id: PositiveInt = Field(..., description="id of the building must be declared ")
    name: str = Field(..., description="name of the building must be declared ")
    address: Optional[str]= None
    department_id: str = Field(..., description="department id of the building must be declared ")

class RoomType(str, Enum):
    lecture_hall = 'lecture_hall'
    classroom = 'classroom'
    auditorium = 'auditorium'
    computer_lab = 'computer_lab'
    chemistry_lab = 'chemistry_lab'
    physics_lab = 'physics_lab'
    biology_lab = 'biology_lab'
    language_lab = 'language_lab'
    seminar_room = 'seminar_room'
    workshop = 'workshop'
    gym = 'gym'
    other = 'other'


class Rooms(BaseModel):
    id : PositiveInt = Field(..., description="id of the room must be declared ")
    building_id: PositiveInt = Field(..., description="id of the building must be declared ")
    code: str = Field(..., description="code of room must be declared ")
    name: Optional[str]= None
    capacity: PositiveInt = Field(..., description="capacity of room must be declared ")
    type: RoomType = Field(..., description="type of room must be declared ")
    note: Optional[str]= None
    equipment: Optional[List[str]]=None
    accessibility: Optional[dict[str,bool]]=None

    @field_validator("capacity")
    def check_capacity(cls, v):
        if v < 1:
            raise ValueError("capacity must be greater than 0")
        return v