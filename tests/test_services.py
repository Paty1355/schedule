
"""
tests for services (data_service, validation_service, schedule_service)
"""
import pytest
from services.data_service import DataTransformService
from services.validation_service import ValidationService


class TestDataTransformService:
    """tests for DataTransformService"""
    
    def test_service_initialization(self, mock_repos):
        """test service initialization"""
        service = DataTransformService(mock_repos)
        assert service.repos == mock_repos
    
    def test_transform_department(self, mock_repos):
        """test department transformation"""
        service = DataTransformService(mock_repos)
        dept = (1, 'WEiI', 'Wydział Elektryczny')
        
        result = service.transform_department(dept)
        
        assert result['ID'] == 1
        assert result['Kod'] == 'WEiI'
        assert result['Nazwa'] == 'Wydział Elektryczny'
    
    def test_transform_building(self, mock_repos):
        """test building transformation"""
        service = DataTransformService(mock_repos)
        building = (1, 'Budynek A', 'ul. Testowa 1', 1)
        
        result = service.transform_building(building)
        
        assert result['ID'] == 1
        assert result['Nazwa'] == 'Budynek A'
        assert result['Adres'] == 'ul. Testowa 1'
        assert result['Wydział'] == 'Wydział Elektryczny'
    
    def test_transform_building_without_address(self, mock_repos):
        """test building transformation without address"""
        service = DataTransformService(mock_repos)
        building = (2, 'Budynek B', None, 1)
        
        result = service.transform_building(building)
        
        assert result['Adres'] == '-'
    
    def test_transform_room(self, mock_repos):
        """test room transformation"""
        service = DataTransformService(mock_repos)
        room = (1, 1, 'A101', 'Sala wykładowa', 50, 'lecture_hall', None)
        
        result = service.transform_room(room)
        
        assert result['ID'] == 1
        assert result['Kod'] == 'A101'
        assert result['Nazwa'] == 'Sala wykładowa'
        assert result['Pojemność'] == 50
        assert 'Typ' in result
    
    def test_transform_group(self, mock_repos):
        """test group transformation"""
        service = DataTransformService(mock_repos)
        group = (1, 'IO_1', 'Informatyka I', 1, 30, None, None)
        
        result = service.transform_group(group)
        
        assert result['ID'] == 1
        assert result['Kod'] == 'IO_1'
        assert result['Nazwa'] == 'Informatyka I'
        assert result['Studenci'] == 30
        assert result['Grupa nadrzędna'] == '-'
    
    def test_transform_group_with_parent(self, mock_repos):
        """test group transformation with parent group"""
        service = DataTransformService(mock_repos)
        # adding parent group to mock
        mock_repos['groups'].data.append((3, 'IO', 'Informatyka', 1, 100, None, None))
        group = (4, 'IO_1', 'Informatyka I', 1, 30, None, 3)
        
        result = service.transform_group(group)
        
        assert result['Grupa nadrzędna'] == 'Informatyka'
    
    def test_transform_teacher(self, mock_repos):
        """test teacher transformation"""
        service = DataTransformService(mock_repos)
        teacher = (1, 'Jan', 'Kowalski', 1)
        
        result = service.transform_teacher(teacher)
        
        assert result['ID'] == 1
        assert result['Imię'] == 'Jan'
        assert result['Nazwisko'] == 'Kowalski'
        assert result['Wydział'] == 'Wydział Elektryczny'
    
    def test_get_teacher_full_name(self, mock_repos):
        """test getting teacher full name"""
        service = DataTransformService(mock_repos)
        
        full_name = service.get_teacher_full_name(1)
        assert full_name == 'Jan Kowalski'
        
        # testing with non-existent teacher
        full_name = service.get_teacher_full_name(999)
        assert full_name == '-'
    
    def test_transform_course(self, mock_repos):
        """test course transformation"""
        service = DataTransformService(mock_repos)
        course = (1, 'INF101', 'Programowanie', 1, 'lecture', 30)
        
        result = service.transform_course(course)
        
        assert result['ID'] == 1
        assert result['Kod'] == 'INF101'
        assert result['Nazwa'] == 'Programowanie'
        assert 'Typ' in result


class TestValidationService:
    """tests for ValidationService"""
    
    def test_service_initialization(self, mock_repos):
        """test service initialization"""
        service = ValidationService(mock_repos)
        assert service.repos == mock_repos
    
    def test_validate_schedule_teacher_conflict(self, mock_repos):
        """test validation with teacher time conflict"""
        service = ValidationService(mock_repos)
        
        # same teacher, same time slot
        assignments = [
            (1, 1, 1, 'monday', 1, 'odd'),
            (2, 1, 2, 'monday', 1, 'odd')
        ]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is False
        assert result['total_conflicts'] > 0
        assert len(result['conflicts']['teacher']) > 0
    
    def test_validate_schedule_group_conflict(self, mock_repos):
        """test validation with group time conflict"""
        service = ValidationService(mock_repos)
        
        # different course assignments but same group
        mock_repos['course_assignments'].data = [
            (1, 1, 1, 1, '2024/2025', None),
            (2, 2, 1, 2, '2024/2025', None)  # same group_id (1)
        ]
        
        assignments = [
            (1, 1, 1, 'monday', 1, 'odd'),
            (2, 2, 2, 'monday', 1, 'odd')
        ]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is False
        assert len(result['conflicts']['group']) > 0
    
    def test_validate_schedule_room_conflict(self, mock_repos):
        """test validation with room conflict"""
        service = ValidationService(mock_repos)
        
        # same room, same time
        assignments = [
            (1, 1, 1, 'monday', 1, 'odd'),
            (2, 2, 1, 'monday', 1, 'odd')  # same room_id (1)
        ]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is False
        assert len(result['conflicts']['room']) > 0
    
    def test_group_by_time(self, mock_repos):
        """test grouping assignments by time"""
        service = ValidationService(mock_repos)
        
        assignments = [
            (1, 1, 1, 'monday', 1, 'both'),
            (2, 2, 2, 'monday', 1, 'both'),
            (3, 1, 1, 'tuesday', 1, 'both')
        ]
        
        grouped = service._group_by_time(assignments)
        
        assert ('monday', 1) in grouped
        assert ('tuesday', 1) in grouped
        assert len(grouped[('monday', 1)]) == 2
        assert len(grouped[('tuesday', 1)]) == 1
    
    def test_check_capacity(self, mock_repos):
        """test capacity checking"""
        service = ValidationService(mock_repos)
        
        # creating assignment with group size > room capacity
        mock_repos['course_assignments'].data = [
            (1, 1, 1, 1, '2024/2025', None)
        ]
        mock_repos['rooms'].data = [
            (1, 1, 'A101', 'Small room', 10, 'classroom', None)  # capacity 10
        ]
        mock_repos['groups'].data = [
            (1, 'IO_1', 'Informatyka', 1, 50, None, None)  # 50 students
        ]
        
        assignments = [(1, 1, 1, 'monday', 1, 'both')]
        conflicts = {
            'teacher': [],
            'group': [],
            'room': [],
            'capacity': [],
            'room_type': []
        }
        
        service._check_capacity(assignments, conflicts)
        
        # should detect capacity conflict
        assert len(conflicts['capacity']) > 0
    
    def test_check_room_types(self, mock_repos):
        """test room type checking"""
        service = ValidationService(mock_repos)
        conflicts = {
            'teacher': [],
            'group': [],
            'room': [],
            'capacity': [],
            'room_type': []
        }
        
        # creating course needing lab but assigned to lecture hall
        mock_repos['courses'].data = [
            (1, 'INF101', 'Programowanie', 1, 'computer_lab', 30)
        ]
        mock_repos['course_assignments'].data = [
            (1, 1, 1, 1, '2024/2025', None)
        ]
        mock_repos['rooms'].data = [
            (1, 1, 'A101', 'Lecture hall', 50, 'lecture_hall', None)
        ]
        
        assignments = [(1, 1, 1, 'monday', 1, 'both')]
        
        service._check_room_types(assignments, conflicts)
        
        assert len(conflicts['room_type']) > 0
    
    def test_validate_empty_schedule(self, mock_repos):
        """test validation with empty schedule"""
        service = ValidationService(mock_repos)
        
        result = service.validate_schedule([])
        
        assert result['is_valid'] is True
        assert result['total_conflicts'] == 0
    
    def test_validate_schedule_with_parity(self, mock_repos):
        """test validation considering week parity"""
        service = ValidationService(mock_repos)
        
        # same time but different parity - should not conflict
        assignments = [
            (1, 1, 1, 'monday', 1, 'odd'),
            (2, 1, 1, 'monday', 1, 'even')
        ]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is True
        assert result['total_conflicts'] == 0


class TestDataTransformServiceEdgeCases:
    """edge case tests for DataTransformService"""
    
    def test_transform_with_missing_department(self, mock_repos):
        """test transformation when department doesn't exist"""
        service = DataTransformService(mock_repos)
        building = (10, 'Unknown Building', 'Address', 999)
        
        result = service.transform_building(building)
        
        assert result['Wydział'] == '-'
    
    def test_transform_with_missing_parent_group(self, mock_repos):
        """test group transformation when parent group doesn't exist"""
        service = DataTransformService(mock_repos)
        group = (10, 'TEST', 'Test Group', 1, 20, None, 999)
        
        result = service.transform_group(group)
        
        assert result['Grupa nadrzędna'] == '-'
    
    def test_transform_room_without_name(self, mock_repos):
        """test room transformation without name"""
        service = DataTransformService(mock_repos)
        room = (3, 1, 'A103', None, 30, 'classroom', None)
        
        result = service.transform_room(room)
        
        assert result['Nazwa'] == '-'
    
    def test_transform_room_without_notes(self, mock_repos):
        """test room transformation without notes"""
        service = DataTransformService(mock_repos)
        room = (1, 1, 'A101', 'Test', 30, 'classroom', None)
        
        result = service.transform_room(room)
        
        assert result['Notatki'] == '-'


class TestValidationServiceEdgeCases:
    """edge case tests for ValidationService"""
    
    def test_validate_single_assignment(self, mock_repos):
        """test validation with single assignment"""
        service = ValidationService(mock_repos)
        assignments = [(1, 1, 1, 'monday', 1, 'both')]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is True
        assert result['total_conflicts'] == 0
    
    def test_validate_all_conflicts_types(self, mock_repos):
        """test that all conflict types are initialized"""
        service = ValidationService(mock_repos)
        
        result = service.validate_schedule([])
        
        assert 'teacher' in result['conflicts']
        assert 'group' in result['conflicts']
        assert 'room' in result['conflicts']
        assert 'capacity' in result['conflicts']
        assert 'room_type' in result['conflicts']
    
    def test_validate_with_both_parity(self, mock_repos):
        """test validation with 'both' parity"""
        service = ValidationService(mock_repos)
        
        # 'both' parity should not trigger conflicts
        assignments = [
            (1, 1, 1, 'monday', 1, 'both'),
            (2, 1, 1, 'monday', 1, 'both')
        ]
        
        result = service.validate_schedule(assignments)
        
        assert result['is_valid'] is True
        assert result['total_conflicts'] == 0
