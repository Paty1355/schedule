"""
service for data transformation
"""
from typing import Dict, List, Any
from app_config.constants import (
    ROOM_TYPE_LABELS_PL, 
    COURSE_TYPE_LABELS_PL,
    WEEK_PARITY_LABELS_PL,
    WEEKDAY_LABELS_PL
)


class DataTransformService:
    """service for transforming data from database to UI format"""
    
    def __init__(self, repos: Dict):
        self.repos = repos
    
    # departments
    
    def transform_department(self, dept: tuple) -> Dict[str, Any]:
        """transforms department tuple to dictionary"""
        return {
            'ID': dept[0],
            'Kod': dept[1],
            'Nazwa': dept[2]
        }
    
    # buildings
    
    def transform_building(self, building: tuple) -> Dict[str, Any]:
        """transforms building tuple to dictionary with department name"""
        dept = self.repos['departments'].get_by_id('id', building[3])
        return {
            'ID': building[0],
            'Nazwa': building[1],
            'Adres': building[2] or '-',
            'Wydział': dept[2] if dept else '-'
        }
    
    # rooms
    
    def transform_room(self, room: tuple) -> Dict[str, Any]:
        """transforms room tuple to dictionary with building name and type"""
        building = self.repos['buildings'].get_by_id('id', room[1])
        return {
            'ID': room[0],
            'Kod': room[2],
            'Nazwa': room[3] or '-',
            'Budynek': building[1] if building else '-',
            'Pojemność': room[4],
            'Typ': ROOM_TYPE_LABELS_PL.get(room[5], room[5]),
            'Notatki': room[6] or '-'
        }
    
    # groups
    
    def transform_group(self, group: tuple) -> Dict[str, Any]:
        """transforms group tuple to dictionary with department and parent group"""
        dept = self.repos['departments'].get_by_id('id', group[3])
        parent = self.repos['groups'].get_by_id('id', group[6]) if group[6] else None
        return {
            'ID': group[0],
            'Kod': group[1],
            'Nazwa': group[2],
            'Wydział': dept[2] if dept else '-',
            'Studenci': group[4],
            'Grupa nadrzędna': parent[2] if parent else '-'
        }
    
    # teachers
    
    def transform_teacher(self, teacher: tuple) -> Dict[str, Any]:
        """transforms teacher tuple to dictionary with department"""
        dept = self.repos['departments'].get_by_id('id', teacher[3])
        return {
            'ID': teacher[0],
            'Imię': teacher[1],
            'Nazwisko': teacher[2],
            'Wydział': dept[2] if dept else '-'
        }
    
    def get_teacher_full_name(self, teacher_id: int) -> str:
        """returns teacher's full name"""
        teacher = self.repos['teachers'].get_by_id('id', teacher_id)
        if teacher:
            return f"{teacher[1]} {teacher[2]}"
        return '-'
    
    # courses
    
    def transform_course(self, course: tuple) -> Dict[str, Any]:
        """transforms course tuple to dictionary"""
        dept = self.repos['departments'].get_by_id('id', course[3])
        return {
            'ID': course[0],
            'Kod': course[1],
            'Nazwa': course[2],
            'Wydział': dept[2] if dept else '-',
            'Typ': COURSE_TYPE_LABELS_PL.get(course[4], course[4]),
            'Godzin': course[5]
        }
    
    # course assignments
    
    def transform_course_assignment(self, assignment: tuple) -> Dict[str, Any]:
        """transforms course assignment to dictionary with full data"""
        course = self.repos['courses'].get_by_id('id', assignment[1])
        group = self.repos['groups'].get_by_id('id', assignment[2])
        teacher = self.repos['teachers'].get_by_id('id', assignment[3])
        
        course_type_pl = COURSE_TYPE_LABELS_PL.get(course[4], course[4]) if course else '-'
        
        return {
            'ID': assignment[0],
            'Przedmiot': f"{course[2]} ({course_type_pl})" if course else '-',
            'Grupa': f"{group[1]} - {group[2]}" if group else '-',
            'Prowadzący': f"{teacher[1]} {teacher[2]}" if teacher else '-',
            'Semestr': assignment[4],
            'Notatka': assignment[5] or '-'
        }
    
    # time slots
    
    def transform_time_slot(self, timeslot: tuple) -> Dict[str, Any]:
        """transforms time slot to dictionary"""
        return {
            'ID': timeslot[0],
            'Początek': str(timeslot[1]),
            'Koniec': str(timeslot[2]),
            'Kolejność': timeslot[3],
            'Czas trwania (min)': timeslot[4] if len(timeslot) > 4 else '-'
        }
    
    # unavailabilities
    
    def transform_teacher_unavailability(self, unavail: tuple) -> Dict[str, Any]:
        """transforms teacher unavailability to dictionary"""
        teacher = self.repos['teachers'].get_by_id('id', unavail[1])
        return {
            'ID': unavail[0],
            'Prowadzący': f"{teacher[1]} {teacher[2]}" if teacher else '-',
            'Dzień': WEEKDAY_LABELS_PL.get(unavail[2], unavail[2]),
            'Od': str(unavail[3]),
            'Do': str(unavail[4]),
            'Powód': unavail[5] or '-'
        }
    
    def transform_group_unavailability(self, unavail: tuple) -> Dict[str, Any]:
        """transforms group unavailability to dictionary"""
        group = self.repos['groups'].get_by_id('id', unavail[1])
        return {
            'ID': unavail[0],
            'Grupa': group[2] if group else '-',
            'Dzień': WEEKDAY_LABELS_PL.get(unavail[2], unavail[2]),
            'Od': str(unavail[3]),
            'Do': str(unavail[4]),
            'Powód': unavail[5] or '-'
        }
    
    # assignments (schedule)
    
    def transform_assignment(self, assignment: tuple) -> Dict[str, Any]:
        """transforms schedule assignment to dictionary with full data"""
        course_assignment = self.repos['course_assignments'].get_by_id('id', assignment[1])
        
        if not course_assignment:
            return {}
        
        course = self.repos['courses'].get_by_id('id', course_assignment[1])
        group = self.repos['groups'].get_by_id('id', course_assignment[2])
        teacher = self.repos['teachers'].get_by_id('id', course_assignment[3])
        room = self.repos['rooms'].get_by_id('id', assignment[2])
        
        # assignment[4] = start_time, assignment[5] = end_time
        start_time = assignment[4]
        end_time = assignment[5]
        
        return {
            'ID': assignment[0],
            'Dzień': WEEKDAY_LABELS_PL.get(assignment[3], assignment[3]),
            'Godzina': f"{start_time} - {end_time}",
            'Przedmiot': course[2] if course else '-',
            'Typ': COURSE_TYPE_LABELS_PL.get(course[4], course[4]) if course else '-',
            'Grupa': f"{group[1]} - {group[2]}" if group else '-',
            'Prowadzący': f"{teacher[1]} {teacher[2]}" if teacher else '-',
            'Sala': f"{room[2]} ({room[3]})" if room else '-',
            'Parzystość': WEEK_PARITY_LABELS_PL.get(assignment[7], assignment[7]),
            'Notatka': assignment[8] or '-'
        }
    
    # bulk transforms
    
    def transform_all(self, items: List[tuple], transform_func) -> List[Dict[str, Any]]:
        """transforms list of tuples using the provided transformation function"""
        return [transform_func(item) for item in items]
