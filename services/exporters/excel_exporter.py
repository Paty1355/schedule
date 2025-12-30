"""
Excel exporter - export data to Excel format
"""
from typing import Dict
import pandas as pd
from io import BytesIO
from .base_exporter import BaseExporter
from ..excel_schema import EXCEL_SCHEMA


class ExcelExporter(BaseExporter):
    """Exports data to Excel file"""
    
    def export_all_data(self) -> BytesIO:
        """
        exports all data to excel file in import-compatible format
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            exported_sheets = 0
            
            # fetch all data at the beginning
            departments = self.repos['departments'].get_all()
            buildings_list = self.repos['buildings'].get_all()
            rooms = self.repos['rooms'].get_all()
            groups = self.repos['groups'].get_all()
            teachers = self.repos['teachers'].get_all()
            courses = self.repos['courses'].get_all()
            course_assignments = self.repos['course_assignments'].get_all()
            
            # create lookup maps for better performance
            dept_map = self._create_lookup_map(departments, 0) if departments else {}
            building_map = self._create_lookup_map(buildings_list, 0) if buildings_list else {}
            group_map = self._create_lookup_map(groups, 0) if groups else {}
            teacher_map = self._create_lookup_map(teachers, 0) if teachers else {}
            course_map = self._create_lookup_map(courses, 0) if courses else {}
            room_map = self._create_lookup_map(rooms, 0) if rooms else {}
            
            # export departments
            exported_sheets += self._export_departments(writer, departments)
            
            # export buildings
            exported_sheets += self._export_buildings(writer, buildings_list, departments, dept_map)
            
            # export rooms
            exported_sheets += self._export_rooms(writer, rooms, buildings_list, building_map)
            
            # export groups
            exported_sheets += self._export_groups(writer, groups, departments, dept_map, group_map)
            
            # export teachers
            exported_sheets += self._export_teachers(writer, teachers, departments, dept_map)
            
            # export courses
            exported_sheets += self._export_courses(writer, courses, departments, dept_map)
            
            # export course assignments
            exported_sheets += self._export_course_assignments(
                writer, course_assignments, courses, groups, teachers,
                course_map, group_map, teacher_map
            )
            
            # export schedule
            exported_sheets += self._export_schedule(
                writer, course_assignments, rooms,
                course_map, group_map, teacher_map, room_map
            )
            
            # if no data
            if exported_sheets == 0:
                df_info = pd.DataFrame({
                    'Informacja': ['Baza danych jest pusta'], 
                    'Status': ['Brak danych do eksportu']
                })
                df_info.to_excel(writer, sheet_name='Info', index=False)

        output.seek(0)
        return output
    
    def _export_departments(self, writer, departments) -> int:
        """Export departments sheet"""
        sheet = EXCEL_SCHEMA['departments']
        cols = sheet.columns
        if not departments:
            return 0
        
        data = []
        for d in departments:
            data.append({
                cols['code']: d[1],
                cols['name']: d[2]
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_buildings(self, writer, buildings_list, departments, dept_map) -> int:
        """Export buildings sheet"""
        sheet = EXCEL_SCHEMA['buildings']
        cols = sheet.columns
        if not (buildings_list and departments):
            return 0
        
        data = []
        for b in buildings_list:
            # b = (id, nazwa, adres, department_id)
            dept = dept_map.get(b[3])
            data.append({
                cols['name']: b[1],
                cols['address']: self._safe_str(b[2]),
                cols['department_code']: dept[1] if dept else ''
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_rooms(self, writer, rooms, buildings_list, building_map) -> int:
        """Export rooms sheet"""
        sheet = EXCEL_SCHEMA['rooms']
        cols = sheet.columns
        if not (rooms and buildings_list):
            return 0
        
        data = []
        for r in rooms:
            # r = (id, building_id, kod, nazwa, pojemnosc, typ, notatki, ...)
            building = building_map.get(r[1])
            data.append({
                cols['code']: r[2],
                cols['name']: self._safe_str(r[3]),
                cols['building_name']: building[1] if building else '',
                cols['capacity']: r[4],
                cols['type']: r[5],
                cols['note']: self._safe_str(r[6])
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_timeslots(self, writer, timeslots) -> int:
        """Export time slots sheet"""
        sheet = EXCEL_SCHEMA['time_slots']
        cols = sheet.columns
        if not timeslots:
            return 0
        
        data = []
        for ts in timeslots:
            # ts = (id, start_time, end_time, slot_order, duration)
            data.append({
                cols['start']: str(ts[1]),
                cols['end']: str(ts[2]),
                cols['order']: ts[3]
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_groups(self, writer, groups, departments, dept_map, group_map) -> int:
        """Export groups sheet"""
        sheet = EXCEL_SCHEMA['groups']
        cols = sheet.columns
        if not (groups and departments):
            return 0
        
        data = []
        for g in groups:
            # g = (id, kod, nazwa, department_id, students_count, requirements, parent_group_id)
            dept = dept_map.get(g[3])
            
            # find parent group code
            parent_code = ''
            if g[6]:
                parent = group_map.get(g[6])
                parent_code = parent[1] if parent else ''
            
            data.append({
                cols['code']: g[1],
                cols['name']: g[2],
                cols['department_code']: dept[1] if dept else '',
                cols['student_count']: g[4],
                cols['parent_code']: parent_code
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_teachers(self, writer, teachers, departments, dept_map) -> int:
        """Export teachers sheet"""
        sheet = EXCEL_SCHEMA['teachers']
        cols = sheet.columns
        if not (teachers and departments):
            return 0
        
        data = []
        for t in teachers:
            # t = (id, first_name, last_name, department_id, accessibility)
            dept = dept_map.get(t[3])
            data.append({
                cols['first_name']: t[1],
                cols['last_name']: t[2],
                cols['department_code']: dept[1] if dept else ''
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_courses(self, writer, courses, departments, dept_map) -> int:
        """Export courses sheet"""
        sheet = EXCEL_SCHEMA['courses']
        cols = sheet.columns
        if not (courses and departments):
            return 0
        
        data = []
        for c in courses:
            # c = (id, code, name, department_id, type, hours_per_semester)
            dept = dept_map.get(c[3])
            data.append({
                cols['code']: c[1],
                cols['name']: c[2],
                cols['department_code']: dept[1] if dept else '',
                cols['type']: c[4],
                cols['hours']: c[5]
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_course_assignments(self, writer, course_assignments, courses, groups, teachers,
                                   course_map, group_map, teacher_map) -> int:
        """Export course assignments sheet"""
        sheet = EXCEL_SCHEMA['course_assignments']
        cols = sheet.columns
        if not (course_assignments and courses and groups and teachers):
            return 0
        
        data = []
        for ca in course_assignments:
            # ca = (id, course_id, group_id, teacher_id, semester, note)
            course = course_map.get(ca[1])
            group = group_map.get(ca[2])
            teacher = teacher_map.get(ca[3])
            
            data.append({
                cols['course_code']: course[1] if course else '',
                cols['group_code']: group[1] if group else '',
                cols['teacher_full_name']: f"{teacher[1]} {teacher[2]}" if teacher else '',
                cols['semester']: ca[4]
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
        return 1
    
    def _export_schedule(self, writer, course_assignments, rooms,
                        course_map, group_map, teacher_map, room_map) -> int:
        """Export schedule sheet"""
        sheet = EXCEL_SCHEMA['schedule']
        cols = sheet.columns
        assignments = self.repos['assignments'].get_all()
        if not (assignments and course_assignments and rooms):
            return 0
        
        # create lookup map for course assignments
        ca_map = self._create_lookup_map(course_assignments, 0)
        
        data = []
        for a in assignments:
            # a = (id, course_assignment_id, room_id, weekday, start_time, end_time, duration_minutes, week_parity, note)
            
            # find course assignment
            ca = ca_map.get(a[1])
            if not ca:
                continue
            
            # find course, group, teacher using maps
            course = course_map.get(ca[1])
            group = group_map.get(ca[2])
            teacher = teacher_map.get(ca[3])
            
            # find room
            room = room_map.get(a[2])
            
            # a[4] = start_time, a[5] = end_time
            start_time = a[4]
            end_time = a[5]
            
            if course and group and teacher and room:
                data.append({
                    cols['course_code']: course[1],
                    cols['group_code']: group[1],
                    cols['teacher_full_name']: f"{teacher[1]} {teacher[2]}",
                    cols['room_code']: room[2],
                    cols['weekday']: a[3],
                    cols['start_time']: str(start_time),
                    cols['end_time']: str(end_time),
                    cols['parity']: a[7],
                    cols['note']: self._safe_str(a[8])
                })
        
        if data:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet.sheet_name, index=False)
            return 1
        
        return 0
