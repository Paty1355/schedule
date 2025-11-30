class TimetableOptimized:
    def __init__(self, course_assignments: list[CourseAssignment],
                 rooms: list[Room],
                 time_slots: list[TimeSlot],
                 weekdays: list[Weekday]):
        self.course_assignments = course_assignments
        self.rooms = rooms
        self.time_slots = time_slots
        self.weekdays = weekdays
        self.assignments: list[Assignment] = []
    
    def add_assignment(self, assignment: Assignment):
        self.assignments.append(assignment)
    
    def get_assignments_at(self, weekday: Weekday, time_slot: TimeSlot,
                          week_parity: Optional[WeekParity] = None) -> list[Assignment]:
        result = []
        for a in self.assignments:
            if a.weekday == weekday and a.time_slot.id == time_slot.id:
                if week_parity is None:
                    result.append(a)
                elif a.week_parity == WeekParity.BOTH or a.week_parity == week_parity:
                    result.append(a)
        return result