class TimetableValidator:
    """Sprawdza wszystkie konflikty w planie"""

    def __init__(self, timetable):
        self.timetable = timetable
        self.conflicts = defaultdict(list)

    def validate(self) -> dict:
        """Zwraca raport walidacji"""
        self.conflicts.clear()

        self._check_teacher_conflicts()
        self._check_group_conflicts()
        self._check_room_conflicts()
        self._check_capacity()
        self._check_room_type()

        return {
            'is_valid': len(self.conflicts) == 0,
            'total_conflicts': sum(len(v) for v in self.conflicts.values()),
            'conflicts_by_type': dict(self.conflicts),
            'summary': self._get_summary()
        }

    def _check_teacher_conflicts(self):
        """Sprawdź czy nauczyciel nie ma dwóch zajęć w tym samym czasie"""
        for weekday in self.timetable.weekdays:
            for time_slot in self.timetable.time_slots:
                for parity in [WeekParity.ODD, WeekParity.EVEN]:
                    assignments = self.timetable.get_assignments_at(weekday, time_slot, parity)
                    teacher_ids = [a.course_assignment.teacher.id for a in assignments]

                    if len(teacher_ids) != len(set(teacher_ids)):
                        duplicates = [tid for tid in set(teacher_ids) if teacher_ids.count(tid) > 1]
                        for tid in duplicates:
                            conflicting = [a for a in assignments if a.course_assignment.teacher.id == tid]
                            self.conflicts['teacher_conflicts'].append({
                                'teacher_id': tid,
                                'teacher_name': conflicting[0].course_assignment.teacher.full_name,
                                'weekday': weekday.value,
                                'time_slot': f"{time_slot.start_time}-{time_slot.end_time}",
                                'parity': parity.value,
                                'courses': [a.course_assignment.course.name for a in conflicting]
                            })

    def _check_group_conflicts(self):
        """Sprawdź czy grupa nie ma dwóch zajęć w tym samym czasie"""
        for weekday in self.timetable.weekdays:
            for time_slot in self.timetable.time_slots:
                for parity in [WeekParity.ODD, WeekParity.EVEN]:
                    assignments = self.timetable.get_assignments_at(weekday, time_slot, parity)
                    group_ids = [a.course_assignment.group.id for a in assignments]

                    if len(group_ids) != len(set(group_ids)):
                        duplicates = [gid for gid in set(group_ids) if group_ids.count(gid) > 1]
                        for gid in duplicates:
                            conflicting = [a for a in assignments if a.course_assignment.group.id == gid]
                            self.conflicts['group_conflicts'].append({
                                'group_id': gid,
                                'group_name': conflicting[0].course_assignment.group.name,
                                'weekday': weekday.value,
                                'time_slot': f"{time_slot.start_time}-{time_slot.end_time}",
                                'parity': parity.value,
                                'courses': [a.course_assignment.course.name for a in conflicting]
                            })

    def _check_room_conflicts(self):
        """Sprawdź czy sala nie jest zajęta przez dwie grupy"""
        for weekday in self.timetable.weekdays:
            for time_slot in self.timetable.time_slots:
                for parity in [WeekParity.ODD, WeekParity.EVEN]:
                    assignments = self.timetable.get_assignments_at(weekday, time_slot, parity)
                    room_ids = [a.room.id for a in assignments]

                    if len(room_ids) != len(set(room_ids)):
                        duplicates = [rid for rid in set(room_ids) if room_ids.count(rid) > 1]
                        for rid in duplicates:
                            conflicting = [a for a in assignments if a.room.id == rid]
                            self.conflicts['room_conflicts'].append({
                                'room_id': rid,
                                'room_code': conflicting[0].room.code,
                                'weekday': weekday.value,
                                'time_slot': f"{time_slot.start_time}-{time_slot.end_time}",
                                'parity': parity.value,
                                'courses': [a.course_assignment.course.name for a in conflicting]
                            })

    def _check_capacity(self):
        """Sprawdź czy sale mają wystarczającą pojemność"""
        for assignment in self.timetable.assignments:
            if assignment.room.capacity < assignment.course_assignment.group.students_count:
                self.conflicts['capacity_violations'].append({
                    'room': assignment.room.code,
                    'room_capacity': assignment.room.capacity,
                    'group': assignment.course_assignment.group.name,
                    'students_count': assignment.course_assignment.group.students_count,
                    'course': assignment.course_assignment.course.name
                })

    def _check_room_type(self):
        """Sprawdź czy typ sali pasuje do typu kursu"""
        type_mapping = {
            CourseType.LECTURE: [RoomType.LECTURE_HALL, RoomType.AUDITORIUM, RoomType.CLASSROOM],
            CourseType.LAB: [RoomType.LAB, RoomType.COMPUTER_LAB],
            CourseType.SEMINAR: [RoomType.SEMINAR_ROOM, RoomType.CLASSROOM],
            CourseType.PROJECT: [RoomType.CLASSROOM, RoomType.COMPUTER_LAB],
            CourseType.EXERCISE: [RoomType.CLASSROOM, RoomType.GYM]
        }

        for assignment in self.timetable.assignments:
            course_type = assignment.course_assignment.course.type
            if course_type in type_mapping:
                if assignment.room.type not in type_mapping[course_type]:
                    self.conflicts['room_type_mismatch'].append({
                        'course': assignment.course_assignment.course.name,
                        'course_type': course_type.value,
                        'room': assignment.room.code,
                        'room_type': assignment.room.type.value
                    })

    def _get_summary(self) -> str:
        """Podsumowanie walidacji"""
        if not self.conflicts:
            return "✓ Plan jest poprawny - brak konfliktów!"

        lines = ["✗ Znalezione konflikty:"]
        for conflict_type, items in self.conflicts.items():
            lines.append(f"  - {conflict_type}: {len(items)}")
        return "\n".join(lines)