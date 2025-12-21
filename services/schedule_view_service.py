from typing import List, Tuple, Dict, Optional
from utils.formatters import format_time_slot, format_weekday_pl
from app_config.constants import WEEKDAY_ORDER



class ScheduleViewService:
    """service for displaying and filtering schedule"""
    
    def __init__(self, repos):
        self.repos = repos
    
    def get_full_schedule(self, department_id: Optional[int] = None) -> List[Dict]:
        """
        fetches full schedule with optional department filter
        """
        assignments = self.repos['assignments'].get_all()
        
        if not assignments:
            return []
        
        schedule_data = []
        
        for a in assignments:
            ca = self.repos['course_assignments'].get_by_id('id', a[1])
            if not ca:
                continue
            
            # filter by department if provided
            if department_id:
                group = self.repos['groups'].get_by_id('id', ca[2])
                if not group or group[3] != department_id:
                    continue
            
            # fetch full data
            course = self.repos['courses'].get_by_id('id', ca[1])
            group = self.repos['groups'].get_by_id('id', ca[2])
            teacher = self.repos['teachers'].get_by_id('id', ca[3])
            room = self.repos['rooms'].get_by_id('id', a[2])
            
            if course and group and teacher and room:
                # a[4] = start_time, a[5] = end_time, a[7] = week_parity, a[8] = note
                start_time = a[4]
                end_time = a[5]
                schedule_data.append({
                    'id': a[0],
                    'weekday': a[3],
                    'weekday_pl': format_weekday_pl(a[3]),
                    'weekday_order': WEEKDAY_ORDER.get(a[3], 0),
                    'timeslot': format_time_slot(start_time, end_time),
                    'timeslot_order': start_time.hour * 60 + start_time.minute,
                    'course_code': course[1],
                    'course_name': course[2],
                    'course_type': course[4],
                    'group_code': group[1],
                    'group_name': group[2],
                    'teacher_name': f"{teacher[1]} {teacher[2]}",
                    'room_code': room[2],
                    'room_name': room[3],
                    'parity': a[7],
                    'note': a[8]
                })
        
        # sort by day and time
        schedule_data.sort(key=lambda x: (x['weekday_order'], x['timeslot_order']))
        
        return schedule_data
    
    def get_group_schedule(self, group_id: int) -> List[Dict]:
        """
        fetches schedule for specific group (including parent group classes)
        """
        schedule = self.repos['assignments'].get_full_schedule(group_id=group_id)
        
        if not schedule:
            return []
        
        schedule_data = []
        
        # fetch current group information
        current_group = self.repos['groups'].get_by_id('id', group_id)
        if not current_group:
            return []
        
        for s in schedule:
            # check if this is parent group class
            is_from_parent = s[13].startswith('!') if s[13] else False
            
            schedule_data.append({
                'weekday': s[10],
                'weekday_pl': format_weekday_pl(s[10]),
                'weekday_order': WEEKDAY_ORDER.get(s[10], 0),
                'timeslot': format_time_slot(s[8], s[9]),
                'timeslot_order': self._get_timeslot_order(s[8]),
                'course_name': s[2],
                'course_type': s[3],
                'teacher_name': f"{s[4]} {s[5]}",
                'room_code': s[6],
                'room_name': s[7],
                'parity': s[11],
                'is_from_parent': is_from_parent,
                'group_code': s[13],
                'note': s[12]
            })
        
        schedule_data.sort(key=lambda x: (x['weekday_order'], x['timeslot_order']))
        
        return schedule_data
    
    def get_teacher_schedule(self, teacher_id: int) -> List[Dict]:
        """fetches schedule for teacher"""
        schedule = self.repos['assignments'].get_full_schedule(teacher_id=teacher_id)
        
        if not schedule:
            return []
        
        schedule_data = []
        
        for s in schedule:
            schedule_data.append({
                'weekday': s[10],
                'weekday_pl': format_weekday_pl(s[10]),
                'weekday_order': WEEKDAY_ORDER.get(s[10], 0),
                'timeslot': format_time_slot(s[8], s[9]),
                'timeslot_order': self._get_timeslot_order(s[8]),
                'course_name': s[2],
                'course_type': s[3],
                'group_code': s[13],
                'group_name': s[14],
                'room_code': s[6],
                'room_name': s[7],
                'parity': s[11],
                'note': s[12]
            })
        
        schedule_data.sort(key=lambda x: (x['weekday_order'], x['timeslot_order']))
        
        return schedule_data
    
    def get_room_schedule(self, room_id: int) -> List[Dict]:
        """fetches schedule for room"""
        schedule = self.repos['assignments'].get_full_schedule(room_id=room_id)
        
        if not schedule:
            return []
        
        schedule_data = []
        
        for s in schedule:
            schedule_data.append({
                'weekday': s[10],
                'weekday_pl': format_weekday_pl(s[10]),
                'weekday_order': WEEKDAY_ORDER.get(s[10], 0),
                'timeslot': format_time_slot(s[8], s[9]),
                'timeslot_order': self._get_timeslot_order(s[8]),
                'course_name': s[2],
                'course_type': s[3],
                'teacher_name': f"{s[4]} {s[5]}",
                'group_code': s[13],
                'group_name': s[14],
                'parity': s[11],
                'note': s[12]
            })
        
        schedule_data.sort(key=lambda x: (x['weekday_order'], x['timeslot_order']))
        
        return schedule_data
    
    def _get_timeslot_order(self, start_time) -> int:
        """helper function to get time slot order from time"""
        return start_time.hour * 60 + start_time.minute