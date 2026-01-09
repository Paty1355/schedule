"""
pytest fixtures and configuration for the test suite
"""
import sys
from pathlib import Path
import pytest
from datetime import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from genetic_algorithm.data_model.course import Course, CourseType, Course_assignments
from genetic_algorithm.data_model.group import Groups, GroupUnavailabilities
from genetic_algorithm.data_model.teacher import Teachers, Teacher_unavailabities
from genetic_algorithm.data_model.location import Rooms, RoomType, Buildings, Departments
from genetic_algorithm.data_model.time_models import Weekdays, Week_parity, Time_slots
from genetic_algorithm.genetic_algorithms_tool.algorithm_data_schema import Gene


@pytest.fixture
def sample_department():
    """sample department fixture"""
    return Departments(
        id=1,
        code="WEiI",
        name="Wydział Elektryczny i Informatyczny"
    )


@pytest.fixture
def sample_building(sample_department):
    """sample building fixture"""
    return Buildings(
        id=1,
        name="Budynek A",
        address="ul. Testowa 1",
        department_id=str(sample_department.id)
    )


@pytest.fixture
def sample_room(sample_building):
    """sample room fixture"""
    return Rooms(
        id=1,
        building_id=sample_building.id,
        code="A101",
        name="Sala wykładowa",
        capacity=50,
        type=RoomType.lecture_hall,
        note="Projector available"
    )


@pytest.fixture
def sample_rooms(sample_building):
    """multiple sample rooms fixture"""
    return [
        Rooms(
            id=1,
            building_id=sample_building.id,
            code="A101",
            name="Sala wykładowa",
            capacity=50,
            type=RoomType.lecture_hall
        ),
        Rooms(
            id=2,
            building_id=sample_building.id,
            code="A102",
            name="Laboratorium komputerowe",
            capacity=30,
            type=RoomType.computer_lab
        ),
        Rooms(
            id=3,
            building_id=sample_building.id,
            code="A103",
            name="Sala ćwiczeniowa",
            capacity=25,
            type=RoomType.classroom
        )
    ]


@pytest.fixture
def sample_teacher(sample_department):
    """sample teacher fixture"""
    return Teachers(
        id=1,
        first_name="Jan",
        last_name="Kowalski",
        department_id=sample_department.id
    )


@pytest.fixture
def sample_group(sample_department):
    """sample group fixture"""
    return Groups(
        id=1,
        code="IO_1",
        name="Informatyka I rok",
        department_id=sample_department.id,
        students_count=30
    )


@pytest.fixture
def sample_parent_group(sample_department):
    """sample parent group fixture"""
    return Groups(
        id=2,
        code="IO",
        name="Informatyka",
        department_id=sample_department.id,
        students_count=100
    )


@pytest.fixture
def sample_subgroup(sample_department, sample_parent_group):
    """sample subgroup fixture"""
    return Groups(
        id=3,
        code="IO_1_1",
        name="Informatyka I rok grupa 1",
        department_id=sample_department.id,
        students_count=15,
        parent_group_id=sample_parent_group.id
    )


@pytest.fixture
def sample_course(sample_department):
    """sample course fixture"""
    return Course(
        id=1,
        code="INF101",
        name="Podstawy programowania",
        departament_id=sample_department.id,
        type=CourseType.lecture,
        hours_per_semester=30
    )


@pytest.fixture
def sample_course_assignment(sample_course, sample_group, sample_teacher):
    """sample course assignment fixture"""
    return Course_assignments(
        id=1,
        course_id=sample_course,
        group_id=sample_group,
        teacher_id=sample_teacher,
        semester="2025/2026 Zimowy"
    )


@pytest.fixture
def sample_time_slot():
    """sample time slot fixture"""
    return Time_slots(
        id=1,
        start_time=time(8, 0),
        end_time=time(9, 45),
        slot_order=1
    )


@pytest.fixture
def sample_gene(sample_course_assignment, sample_room, sample_time_slot):
    """sample gene fixture"""
    return Gene(
        id=1,
        course_assignment_id=sample_course_assignment,
        room_id=sample_room,
        weekday=Weekdays.monday,
        week_parity=Week_parity.both,
        time_slot_id=sample_time_slot
    )


@pytest.fixture
def sample_teacher_unavailability(sample_teacher):
    """sample teacher unavailability fixture"""
    return Teacher_unavailabities(
        id=1,
        teacher_id=sample_teacher.id,
        weekday=Weekdays.monday,
        start_time=time(8, 0),
        end_time=time(10, 0),
        reason="Rada Wydziału"
    )


@pytest.fixture
def sample_group_unavailability(sample_group):
    """sample group unavailability fixture"""
    return GroupUnavailabilities(
        id=1,
        group_id=sample_group.id,
        weekday=Weekdays.friday,
        start_time=time(16, 0),
        end_time=time(20, 0),
        reason="Organizacja studencka"
    )


@pytest.fixture
def mock_repos():
    """mock repositories for testing services"""
    class MockRepo:
        def __init__(self, data):
            self.data = data
        
        def get_by_id(self, field, value):
            for item in self.data:
                if isinstance(item, tuple) and item[0] == value:
                    return item
            return None
        
        def get_all(self):
            return self.data
    
    return {
        'departments': MockRepo([
            (1, 'WEiI', 'Wydział Elektryczny'),
            (2, 'WM', 'Wydział Mechaniczny')
        ]),
        'buildings': MockRepo([
            (1, 'Budynek A', 'ul. Testowa 1', 1),
            (2, 'Budynek B', 'ul. Testowa 2', 2)
        ]),
        'rooms': MockRepo([
            (1, 1, 'A101', 'Sala wykładowa', 50, 'lecture_hall', None),
            (2, 1, 'A102', 'Lab', 30, 'computer_lab', None)
        ]),
        'groups': MockRepo([
            (1, 'IO_1', 'Informatyka I', 1, 30, None, None),
            (2, 'IO_2', 'Informatyka II', 1, 28, None, None)
        ]),
        'teachers': MockRepo([
            (1, 'Jan', 'Kowalski', 1),
            (2, 'Anna', 'Nowak', 1)
        ]),
        'courses': MockRepo([
            (1, 'INF101', 'Programowanie', 1, 'lecture', 30),
            (2, 'MAT101', 'Matematyka', 1, 'exercise', 30)
        ]),
        'course_assignments': MockRepo([
            (1, 1, 1, 1, '2024/2025', None),
            (2, 2, 2, 2, '2024/2025', None)
        ]),
        'assignments': MockRepo([])
    }