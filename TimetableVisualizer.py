class TimetableVisualizer:
    """Wizualizacja planu zajęć"""
    
    def __init__(self, timetable):
        self.timetable = timetable
    
    def print_group_schedule(self, group_id: int):
        """Wyświetl plan dla grupy"""
        print(f"\n{'='*80}")
        group = next((ca.group for ca in self.timetable.course_assignments 
                     if ca.group.id == group_id), None)
        if not group:
            print(f"Nie znaleziono grupy o ID {group_id}")
            return
        
        print(f"PLAN ZAJĘĆ: {group.name} ({group.code})")
        print(f"{'='*80}\n")
        
        for weekday in self.timetable.weekdays:
            day_assignments = [a for a in self.timetable.assignments 
                             if a.weekday == weekday and a.course_assignment.group.id == group_id]
            
            if not day_assignments:
                continue
            
            print(f"{weekday.value.upper()}:")
            print("-" * 80)
            
            for assignment in sorted(day_assignments, key=lambda a: a.time_slot.slot_order):
                ts = assignment.time_slot
                parity = f" [{assignment.week_parity.value}]" if assignment.week_parity != WeekParity.BOTH else ""
                
                print(f"  {ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}{parity}")
                print(f"    {assignment.course_assignment.course.name} ({assignment.course_assignment.course.type.value})")
                print(f"    Nauczyciel: {assignment.course_assignment.teacher.full_name}")
                print(f"    Sala: {assignment.room.code} ({assignment.room.type.value})")
                print()
    
    def print_teacher_schedule(self, teacher_id: int):
        """Wyświetl plan dla nauczyciela"""
        print(f"\n{'='*80}")
        teacher = next((ca.teacher for ca in self.timetable.course_assignments 
                       if ca.teacher.id == teacher_id), None)
        if not teacher:
            print(f"Nie znaleziono nauczyciela o ID {teacher_id}")
            return
        
        print(f"PLAN ZAJĘĆ: {teacher.full_name}")
        print(f"{'='*80}\n")
        
        for weekday in self.timetable.weekdays:
            day_assignments = [a for a in self.timetable.assignments 
                             if a.weekday == weekday and a.course_assignment.teacher.id == teacher_id]
            
            if not day_assignments:
                continue
            
            print(f"{weekday.value.upper()}:")
            print("-" * 80)
            
            for assignment in sorted(day_assignments, key=lambda a: a.time_slot.slot_order):
                ts = assignment.time_slot
                parity = f" [{assignment.week_parity.value}]" if assignment.week_parity != WeekParity.BOTH else ""
                
                print(f"  {ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}{parity}")
                print(f"    {assignment.course_assignment.course.name}")
                print(f"    Grupa: {assignment.course_assignment.group.name}")
                print(f"    Sala: {assignment.room.code}")
                print()
    
    def print_room_schedule(self, room_id: int):
        """Wyświetl wykorzystanie sali"""
        print(f"\n{'='*80}")
        room = next((r for r in self.timetable.rooms if r.id == room_id), None)
        if not room:
            print(f"Nie znaleziono sali o ID {room_id}")
            return
        
        print(f"WYKORZYSTANIE SALI: {room.code} ({room.name or room.type.value})")
        print(f"Pojemność: {room.capacity} osób")
        print(f"{'='*80}\n")
        
        for weekday in self.timetable.weekdays:
            day_assignments = [a for a in self.timetable.assignments 
                             if a.weekday == weekday and a.room.id == room_id]
            
            if not day_assignments:
                continue
            
            print(f"{weekday.value.upper()}:")
            print("-" * 80)
            
            for assignment in sorted(day_assignments, key=lambda a: a.time_slot.slot_order):
                ts = assignment.time_slot
                parity = f" [{assignment.week_parity.value}]" if assignment.week_parity != WeekParity.BOTH else ""
                
                print(f"  {ts.start_time.strftime('%H:%M')}-{ts.end_time.strftime('%H:%M')}{parity}")
                print(f"    {assignment.course_assignment.course.name}")
                print(f"    {assignment.course_assignment.group.name} ({assignment.course_assignment.group.students_count} studentów)")
                print(f"    Nauczyciel: {assignment.course_assignment.teacher.full_name}")
                print()