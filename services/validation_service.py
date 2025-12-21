from typing import Dict, List, Tuple, Any
from collections import defaultdict
from utils.type_mappings import is_room_type_compatible



class ValidationService:
    """service for schedule validation"""
    
    def __init__(self, repos):
        self.repos = repos
    
    def validate_schedule(self, assignments: List[Tuple]) -> Dict[str, Any]:
        """
        main schedule validation function
        """
        conflicts = {
            'teacher': [],
            'group': [],
            'room': [],
            'capacity': [],
            'room_type': []
        }
        
        # group assignments by time
        assignments_by_time = self._group_by_time(assignments)
        
        # check time conflicts
        self._check_time_conflicts(assignments_by_time, conflicts)
        
        # check capacity
        self._check_capacity(assignments, conflicts)
        
        # check room types
        self._check_room_types(assignments, conflicts)
        
        total = sum(len(v) for v in conflicts.values())
        
        return {
            'is_valid': total == 0,
            'total_conflicts': total,
            'conflicts': conflicts
        }
    
    def _group_by_time(self, assignments: List[Tuple]) -> Dict:
        """groups assignments by (weekday, time_slot_id)"""
        grouped = defaultdict(list)
        for a in assignments:
            key = (a[3], a[4])  # (weekday, time_slot_id)
            grouped[key].append(a)
        return grouped
    
    def _check_time_conflicts(self, assignments_by_time: Dict, conflicts: Dict):
        """checks time conflicts (teacher, group, room)"""
        for time_key, slot_assignments in assignments_by_time.items():
            weekday, time_slot_id = time_key
            
            teachers_in_slot = {}
            groups_in_slot = {}
            rooms_in_slot = {}
            
            for a in slot_assignments:
                ca = self.repos['course_assignments'].get_by_id('id', a[1])
                if not ca:
                    continue
                
                teacher_id = ca[3]
                group_id = ca[2]
                room_id = a[2]
                parity = a[5]
                
                # key with parity consideration
                teacher_key = (teacher_id, parity)
                group_key = (group_id, parity)
                room_key = (room_id, parity)
                
                # teacher conflicts
                if teacher_key in teachers_in_slot and parity != 'both':
                    teacher = self.repos['teachers'].get_by_id('id', teacher_id)
                    conflicts['teacher'].append(
                        f"{weekday} slot {time_slot_id}: {teacher[1]} {teacher[2]} ma 2+ zajęcia"
                    )
                teachers_in_slot[teacher_key] = True
                
                # group conflicts
                if group_key in groups_in_slot and parity != 'both':
                    group = self.repos['groups'].get_by_id('id', group_id)
                    conflicts['group'].append(
                        f"{weekday} slot {time_slot_id}: grupa {group[2]} ma 2+ zajęcia"
                    )
                groups_in_slot[group_key] = True
                
                # room conflicts
                if room_key in rooms_in_slot and parity != 'both':
                    room = self.repos['rooms'].get_by_id('id', room_id)
                    conflicts['room'].append(
                        f"{weekday} slot {time_slot_id}: sala {room[2]} ma 2+ zajęcia"
                    )
                rooms_in_slot[room_key] = True
    
    def _check_capacity(self, assignments: List[Tuple], conflicts: Dict):
        """checks if rooms have appropriate capacity"""
        for a in assignments:
            ca = self.repos['course_assignments'].get_by_id('id', a[1])
            if not ca:
                continue
            
            room = self.repos['rooms'].get_by_id('id', a[2])
            group = self.repos['groups'].get_by_id('id', ca[2])
            
            if room and group:
                if room[4] < group[4]:  # capacity < students_count
                    conflicts['capacity'].append(
                        f"Sala {room[2]} (poj. {room[4]}) za mała dla grupy {group[2]} ({group[4]} studentów)"
                    )
    
    def _check_room_types(self, assignments: List[Tuple], conflicts: Dict):
        """checks if room type matches class type"""
        for a in assignments:
            ca = self.repos['course_assignments'].get_by_id('id', a[1])
            if not ca:
                continue
            
            course = self.repos['courses'].get_by_id('id', ca[1])
            room = self.repos['rooms'].get_by_id('id', a[2])
            
            if course and room:
                course_type = course[4]
                room_type = room[5]
                
                if not is_room_type_compatible(course_type, room_type):
                    conflicts['room_type'].append(
                        f"Zajęcia '{course[2]}' ({course_type}) w nieodpowiedniej sali {room[2]} ({room_type})"
                    )