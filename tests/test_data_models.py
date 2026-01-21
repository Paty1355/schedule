"""
tests for data models (course, group, teacher, location, time_models)
"""
import pytest
from datetime import time
from pydantic import ValidationError
from genetic_algorithm.data_model.course import Course, CourseType, Course_assignments, Assignment
from genetic_algorithm.data_model.group import Groups, GroupUnavailabilities
from genetic_algorithm.data_model.teacher import Teachers, Teacher_unavailabities
from genetic_algorithm.data_model.location import Rooms, RoomType, Buildings, Departments
from genetic_algorithm.data_model.time_models import Weekdays, Week_parity, Time_slots


class TestDepartments:
    """tests for Departments model"""
    
    def test_create_valid_department(self, sample_department):
        """test creating a valid department"""
        assert sample_department.id == 1
        assert sample_department.code == "WEiI"
        assert sample_department.name == "Wydział Elektryczny i Informatyczny"
    
    def test_department_invalid_id(self):
        """test department with invalid id"""
        with pytest.raises(ValidationError):
            Departments(id=0, code="WEiI", name="Test")
        
        with pytest.raises(ValidationError):
            Departments(id=-1, code="WEiI", name="Test")
    
    def test_department_missing_fields(self):
        """test department with missing required fields"""
        with pytest.raises(ValidationError):
            Departments(id=1)


class TestBuildings:
    """tests for Buildings model"""
    
    def test_create_valid_building(self, sample_building):
        """test creating a valid building"""
        assert sample_building.id == 1
        assert sample_building.name == "Budynek A"
        assert sample_building.address == "ul. Testowa 1"
    
    def test_building_optional_address(self, sample_department):
        """test building with optional address"""
        building = Buildings(
            id=1,
            name="Budynek B",
            department_id=str(sample_department.id)
        )
        assert building.address is None
    
    def test_building_invalid_id(self):
        """test building with invalid id"""
        with pytest.raises(ValidationError):
            Buildings(id=0, name="Test", department_id="1")


class TestRooms:
    """tests for Rooms model"""
    
    def test_create_valid_room(self, sample_room):
        """test creating a valid room"""
        assert sample_room.id == 1
        assert sample_room.code == "A101"
        assert sample_room.capacity == 50
        assert sample_room.type == RoomType.lecture_hall
    
    def test_room_capacity_validation(self, sample_building):
        """test room capacity validation"""
        with pytest.raises(ValidationError):
            Rooms(
                id=1,
                building_id=sample_building.id,
                code="A101",
                capacity=0,
                type=RoomType.classroom
            )
        
        with pytest.raises(ValidationError):
            Rooms(
                id=1,
                building_id=sample_building.id,
                code="A101",
                capacity=-5,
                type=RoomType.classroom
            )
    
    def test_room_types(self, sample_building):
        """test different room types"""
        room_types = [
            RoomType.lecture_hall,
            RoomType.computer_lab,
            RoomType.chemistry_lab,
            RoomType.gym
        ]
        
        for room_type in room_types:
            room = Rooms(
                id=1,
                building_id=sample_building.id,
                code="TEST",
                capacity=30,
                type=room_type
            )
            assert room.type == room_type
    
    def test_room_optional_fields(self, sample_building):
        """test room with optional fields"""
        room = Rooms(
            id=1,
            building_id=sample_building.id,
            code="A101",
            capacity=30,
            type=RoomType.classroom,
            equipment=["projector", "whiteboard"],
            accessibility={"wheelchair": True, "elevator": True}
        )
        assert room.equipment == ["projector", "whiteboard"]
        assert room.accessibility["wheelchair"] is True


class TestGroups:
    """tests for Groups model"""
    
    def test_create_valid_group(self, sample_group):
        """test creating a valid group"""
        assert sample_group.id == 1
        assert sample_group.code == "IO_1"
        assert sample_group.students_count == 30
    
    def test_group_with_parent(self, sample_subgroup, sample_parent_group):
        """test group with parent group"""
        assert sample_subgroup.parent_group_id == sample_parent_group.id
    
    def test_group_invalid_students_count(self, sample_department):
        """test group with invalid students count"""
        with pytest.raises(ValidationError):
            Groups(
                id=1,
                code="TEST",
                name="Test",
                department_id=sample_department.id,
                students_count=0
            )
    
    def test_group_with_accessibility(self, sample_department):
        """test group with accessibility requirements"""
        group = Groups(
            id=1,
            code="IO_1",
            name="Test",
            department_id=sample_department.id,
            students_count=25,
            accessibility_requirements={"wheelchair": True}
        )
        assert group.accessibility_requirements["wheelchair"] is True


class TestGroupUnavailabilities:
    """tests for GroupUnavailabilities model"""
    
    def test_create_valid_unavailability(self, sample_group_unavailability):
        """test creating valid group unavailability"""
        assert sample_group_unavailability.weekday == Weekdays.friday
        assert sample_group_unavailability.start_time == time(16, 0)
        assert sample_group_unavailability.end_time == time(20, 0)
    
    def test_unavailability_without_reason(self, sample_group):
        """test unavailability without reason"""
        unavail = GroupUnavailabilities(
            id=1,
            group_id=sample_group.id,
            weekday=Weekdays.monday,
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        assert unavail.reason is None


class TestTeachers:
    """tests for Teachers model"""
    
    def test_create_valid_teacher(self, sample_teacher):
        """test creating a valid teacher"""
        assert sample_teacher.id == 1
        assert sample_teacher.first_name == "Jan"
        assert sample_teacher.last_name == "Kowalski"
    
    def test_teacher_with_accessibility(self, sample_department):
        """test teacher with accessibility needs"""
        teacher = Teachers(
            id=1,
            first_name="Anna",
            last_name="Nowak",
            department_id=sample_department.id,
            accessibility={"wheelchair": True}
        )
        assert teacher.accessibility["wheelchair"] is True
    
    def test_teacher_optional_department(self):
        """test teacher without department"""
        teacher = Teachers(
            id=1,
            first_name="Jan",
            last_name="Kowalski"
        )
        assert teacher.department_id is None


class TestTeacherUnavailabilities:
    """tests for Teacher_unavailabities model"""
    
    def test_create_valid_unavailability(self, sample_teacher_unavailability):
        """test creating valid teacher unavailability"""
        assert sample_teacher_unavailability.weekday == Weekdays.monday
        assert sample_teacher_unavailability.start_time == time(8, 0)
        assert sample_teacher_unavailability.end_time == time(10, 0)
        assert sample_teacher_unavailability.reason == "Rada Wydziału"


class TestCourse:
    """tests for Course model"""
    
    def test_create_valid_course(self, sample_course):
        """test creating a valid course"""
        assert sample_course.id == 1
        assert sample_course.code == "INF101"
        assert sample_course.name == "Podstawy programowania"
        assert sample_course.type == CourseType.lecture
        assert sample_course.hours_per_semester == 30
    
    def test_course_types(self, sample_department):
        """test different course types"""
        course_types = [
            CourseType.lecture,
            CourseType.exercise,
            CourseType.lab,
            CourseType.computer_lab,
            CourseType.project
        ]
        
        for course_type in course_types:
            course = Course(
                id=1,
                code="TEST",
                name="Test Course",
                type=course_type,
                hours_per_semester=30
            )
            assert course.type == course_type
    
    def test_course_invalid_hours(self):
        """test course with invalid hours"""
        with pytest.raises(ValidationError):
            Course(
                id=1,
                code="TEST",
                name="Test",
                hours_per_semester=0
            )


class TestCourseAssignments:
    """tests for Course_assignments model"""
    
    def test_create_valid_assignment(self, sample_course_assignment):
        """test creating valid course assignment"""
        assert sample_course_assignment.id == 1
        assert sample_course_assignment.semester == "2024/2025 Zimowy"
        assert sample_course_assignment.course_id.code == "INF101"
        assert sample_course_assignment.group_id.code == "IO_1"
        assert sample_course_assignment.teacher_id.last_name == "Kowalski"
    
    def test_assignment_with_note(self, sample_course, sample_group, sample_teacher):
        """test assignment with note"""
        assignment = Course_assignments(
            id=1,
            course_id=sample_course,
            group_id=sample_group,
            teacher_id=sample_teacher,
            semester="2024/2025",
            note="Zajęcia online"
        )
        assert assignment.note == "Zajęcia online"


class TestTimeModels:
    """tests for time-related models"""
    
    def test_weekdays_enum(self):
        """test Weekdays enum"""
        assert Weekdays.monday.value == "monday"
        assert Weekdays.friday.value == "friday"
        assert len(list(Weekdays)) == 7
    
    def test_week_parity_enum(self):
        """test Week_parity enum"""
        assert Week_parity.odd.value == "odd"
        assert Week_parity.even.value == "even"
        assert Week_parity.both.value == "both"
    
    def test_create_time_slot(self, sample_time_slot):
        """test creating time slot"""
        assert sample_time_slot.id == 1
        assert sample_time_slot.start_time == time(8, 0)
        assert sample_time_slot.end_time == time(9, 45)
        assert sample_time_slot.slot_order == 1
    
    def test_time_slot_validation(self):
        """test time slot with invalid data"""
        with pytest.raises(ValidationError):
            Time_slots(
                id=0,
                start_time=time(8, 0),
                end_time=time(10, 0),
                slot_order=1
            )