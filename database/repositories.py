import psycopg2
import re

class BaseRepository:
    def __init__(self, db_manager, table_name):
        self.db_manager = db_manager
        self.table_name = table_name
    
    def _handle_error(self, e):
        """handle database errors with a friendly message"""
        try:
            self.db_manager.conn.rollback()
        except:
            pass
        
        error_str = str(e).lower()
        
        if 'unique' in error_str or 'duplicate' in error_str:
            if 'code' in error_str:
                match = re.search(r'Klucz \(code\)=\(([^)]+)\)', str(e))
                if match:
                    duplicate_value = match.group(1)
                    return f"❌ Kod '{duplicate_value}' już istnieje w systemie. Użyj innego kodu."
                return "❌ Ten kod już istnieje w systemie. Użyj innego kodu."
            elif 'name' in error_str:
                return "❌ Ta nazwa już istnieje w systemie. Użyj innej nazwy."
            else:
                return "❌ Ten rekord już istnieje w bazie danych (duplikat)."
        
        elif 'foreign key' in error_str:
            return "❌ Nie można usunąć - istnieją powiązane dane. Usuń najpierw zależne rekordy."
        
        elif 'not null' in error_str:
            return "❌ Wszystkie wymagane pola muszą być wypełnione."
        
        elif 'check constraint' in error_str:
            return "❌ Podane wartości są nieprawidłowe (np. ujemna liczba studentów)."
        
        else:
            return f"❌ Błąd bazy danych: {str(e)}"
    
    def get_all(self):
        """get all records"""
        try:
            query = f"SELECT * FROM {self.table_name}"
            self.db_manager.cur.execute(query)
            return self.db_manager.cur.fetchall()
        except Exception as e:
            error_msg = self._handle_error(e)
            raise Exception(error_msg)
    
    def get_by_id(self, column, value):
        """get record by id or other column"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {column} = %s"
            self.db_manager.cur.execute(query, (value,))
            return self.db_manager.cur.fetchone()
        except Exception as e:
            error_msg = self._handle_error(e)
            raise Exception(error_msg)
    
    def insert(self, data):
        """insert a new record"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            self.db_manager.cur.execute(query, tuple(data.values()))
            self.db_manager.conn.commit()
        except Exception as e:
            error_msg = self._handle_error(e)
            raise Exception(error_msg)
    
    def update(self, id_column, id_value, data):
        """update a record"""
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %s"
            self.db_manager.cur.execute(query, tuple(data.values()) + (id_value,))
            self.db_manager.conn.commit()
        except Exception as e:
            error_msg = self._handle_error(e)
            raise Exception(error_msg)
    
    def delete(self, column, value):
        """delete a record"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE {column} = %s"
            self.db_manager.cur.execute(query, (value,))
            self.db_manager.conn.commit()
        except Exception as e:
            error_msg = self._handle_error(e)
            raise Exception(error_msg)


class DepartmentsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "departments")

    def get_buildings(self, department_id):
        query = "SELECT * FROM buildings WHERE department_id = %s"
        self.db_manager.cur.execute(query, [department_id])
        return self.db_manager.cur.fetchall()

    def get_courses(self, department_id):
        query = "SELECT * FROM courses WHERE department_id = %s"
        self.db_manager.cur.execute(query, [department_id])
        return self.db_manager.cur.fetchall()


class BuildingsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "buildings")

    def get_rooms(self, building_id):
        query = "SELECT * FROM rooms WHERE building_id = %s"
        self.db_manager.cur.execute(query, [building_id])
        return self.db_manager.cur.fetchall()


class RoomsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "rooms")


class GroupsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "groups")

    def get_assignments(self, group_id):
        query = """
            SELECT a.*
            FROM assignments a
            JOIN course_assignments ca ON a.course_assignment_id = ca.id
            WHERE ca.group_id = %s
        """
        self.db_manager.cur.execute(query, [group_id])
        return self.db_manager.cur.fetchall()


class TeachersRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "teachers")

    def get_assignments(self, teacher_id):
        query = """
            SELECT a.*
            FROM assignments a
            JOIN course_assignments ca ON a.course_assignment_id = ca.id
            WHERE ca.teacher_id = %s
        """
        self.db_manager.cur.execute(query, [teacher_id])
        return self.db_manager.cur.fetchall()


class CoursesRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "courses")


class CourseAssignmentsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "course_assignments")

    def get_by_teacher(self, teacher_id):
        query = "SELECT * FROM course_assignments WHERE teacher_id = %s"
        self.db_manager.cur.execute(query, [teacher_id])
        return self.db_manager.cur.fetchall() 

    def get_by_group(self, group_id):
        query = "SELECT * FROM course_assignments WHERE group_id = %s"
        self.db_manager.cur.execute(query, [group_id])
        return self.db_manager.cur.fetchall()

    def get_by_course(self, course_id):
        query = "SELECT * FROM course_assignments WHERE course_id = %s"
        self.db_manager.cur.execute(query, [course_id])
        return self.db_manager.cur.fetchall()


class TimeSlotsRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "time_slots")

    def get_by_order(self, slot_order):
        query = "SELECT * FROM time_slots WHERE slot_order = %s"
        self.db_manager.cur.execute(query, [slot_order]) 
        return self.db_manager.cur.fetchone()


class AssignmentRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, 'assignments')
    
    def get_full_schedule(self, group_id=None, teacher_id=None, room_id=None):
        """get full schedule with joins including parent group assignments for subgroups"""
        query = """
            SELECT 
                a.id,
                c.code as course_code,
                c.name as course_name,
                c.type as course_type,
                t.first_name,
                t.last_name,
                r.code as room_code,
                r.name as room_name,
                ts.start_time,
                ts.end_time,
                a.weekday,
                a.week_parity,
                a.note,
                g.code as group_code,
                g.name as group_name
            FROM assignments a
            JOIN course_assignments ca ON a.course_assignment_id = ca.id
            JOIN courses c ON ca.course_id = c.id
            JOIN groups g ON ca.group_id = g.id
            JOIN teachers t ON ca.teacher_id = t.id
            JOIN rooms r ON a.room_id = r.id
            JOIN time_slots ts ON a.time_slot_id = ts.id
            WHERE 1=1
        """
        
        params = []
        
        if group_id:
            query += " AND (ca.group_id = %s"
            params.append(group_id)
            
            self.db_manager.cur.execute("SELECT parent_group_id FROM groups WHERE id = %s", (group_id,))
            result = self.db_manager.cur.fetchone()
            
            if result and result[0]:
                query += " OR ca.group_id = %s"
                params.append(result[0])
            
            query += ")"
        
        if teacher_id:
            query += " AND ca.teacher_id = %s"
            params.append(teacher_id)
        
        if room_id:
            query += " AND a.room_id = %s"
            params.append(room_id)
        
        query += " ORDER BY a.weekday, ts.slot_order"
        
        self.db_manager.cur.execute(query, tuple(params) if params else None)
        return self.db_manager.cur.fetchall()


class TeacherUnavailabilitiesRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "teacher_unavailabilities")

    def get_for_day(self, teacher_id, weekday):
        query = """
            SELECT * FROM teacher_unavailabilities
            WHERE teacher_id = %s AND weekday = %s
        """
        self.db_manager.cur.execute(query, [teacher_id, weekday])
        return self.db_manager.cur.fetchall()


class GroupUnavailabilitiesRepository(BaseRepository):
    def __init__(self, db_manager):
        super().__init__(db_manager, "group_unavailabilities")

    def get_for_day(self, group_id, weekday):
        query = """
            SELECT * FROM group_unavailabilities
            WHERE group_id = %s AND weekday = %s
        """
        self.db_manager.cur.execute(query, [group_id, weekday])
        return self.db_manager.cur.fetchall()