# excel_importer.py
"""
Excel importer - import data from Excel format
"""
from typing import Dict, Any, Set, Optional
import pandas as pd
import json
from utils.formatters import parse_time
from .base_importer import BaseImporter
from ..excel_schema import EXCEL_SCHEMA


class ExcelImporter(BaseImporter):
    """Imports data from Excel file"""
    
    def import_from_excel(self, excel_file) -> Dict[str, Any]:
        """Import data from Excel file"""
        stats = self._init_stats()
        errors = []
        db_manager = self.repos['departments'].db_manager
        
        try:
            excel_data = pd.ExcelFile(excel_file)
            
            # Import in order respecting dependencies
            self._import_departments(excel_file, excel_data, stats, errors, db_manager)
            self._import_buildings(excel_file, excel_data, stats, errors, db_manager)
            self._import_rooms(excel_file, excel_data, stats, errors, db_manager)
            self._import_groups(excel_file, excel_data, stats, errors, db_manager)
            self._import_teachers(excel_file, excel_data, stats, errors, db_manager)
            self._import_courses(excel_file, excel_data, stats, errors, db_manager)
            self._import_course_assignments(excel_file, excel_data, stats, errors, db_manager)
            self._import_schedule(excel_file, excel_data, stats, errors, db_manager)

            return {'success': True, 'stats': stats, 'errors': errors}
        
        except Exception as e:
            return {'success': False, 'stats': stats, 'errors': [f"Błąd krytyczny: {str(e)}"]}
    
    def _import_departments(self, excel_file, excel_data, stats, errors, db_manager):
        """Import departments from Excel"""
        existing_codes = {d[1] for d in self._get_all_cached('departments')}
        
        def check_exists(row, cols, existing):
            code = str(row[cols['code']])
            if code in existing:
                return True
            existing.add(code)
            return False
        
        def prepare(row, cols):
            return {'code': str(row[cols['code']]), 'name': str(row[cols['name']])}
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['departments'],
            'departments', 'wydzialy', stats, errors, db_manager,
            prepare, check_exists, existing_items=existing_codes
        )
    
    def _import_buildings(self, excel_file, excel_data, stats, errors, db_manager):
        """Import buildings from Excel"""
        depts_lookup = self._create_code_lookup(self._get_all_cached('departments'))
        building_names = {b[1] for b in self._get_all_cached('buildings')}
        
        def check_exists(row, cols, existing):
            name = str(row[cols['name']])
            if name in existing:
                return True
            existing.add(name)
            return False
        
        def prepare(row, cols):
            dept = depts_lookup.get(row[cols['department_code']])
            if not dept:
                errors.append(f"Nie znaleziono wydziału {row[cols['department_code']]}")
                return None
            return {
                'name': str(row[cols['name']]),
                'address': str(row[cols['address']]) if pd.notna(row[cols['address']]) else None,
                'department_id': dept[0]
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['buildings'],
            'buildings', 'budynki', stats, errors, db_manager,
            prepare, check_exists, existing_items=building_names
        )
    
    def _import_rooms(self, excel_file, excel_data, stats, errors, db_manager):
        """Import rooms from Excel"""
        buildings_lookup = self._create_code_lookup(self._get_all_cached('buildings'), code_index=1)
        room_codes = {r[2] for r in self._get_all_cached('rooms')}
        
        def check_exists(row, cols, existing):
            code = str(row[cols['code']])
            if code in existing:
                return True
            existing.add(code)
            return False
        
        def prepare(row, cols):
            building = buildings_lookup.get(row[cols['building_name']])
            if not building:
                errors.append(f"Nie znaleziono budynku {row[cols['building_name']]}")
                return None
            return {
                'building_id': building[0],
                'code': str(row[cols['code']]),
                'name': str(row[cols['name']]) if pd.notna(row[cols['name']]) else None,
                'capacity': int(row[cols['capacity']]),
                'type': str(row[cols['type']]).strip().lower(),
                'note': str(row[cols['note']]) if pd.notna(row[cols['note']]) else None,
                'equipment': json.dumps({}),
                'accessibility': json.dumps({})
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['rooms'],
            'rooms', 'sale', stats, errors, db_manager,
            prepare, check_exists, existing_items=room_codes
        )
    
    def _import_groups(self, excel_file, excel_data, stats, errors, db_manager):
        """Import groups from Excel (parent groups first, then subgroups)"""
        sheet = EXCEL_SCHEMA['groups']
        if sheet.sheet_name not in excel_data.sheet_names:
            return
        
        df_groups = pd.read_excel(excel_file, sheet_name=sheet.sheet_name)
        depts_lookup = self._create_code_lookup(self._get_all_cached('departments'))
        existing_codes = {g[1] for g in self._get_all_cached('groups')}
        
        # Import parent groups first
        self._import_groups_phase(df_groups, sheet.columns, depts_lookup, existing_codes, 
                                  stats, errors, db_manager, parent_phase=True)
        
        # Import subgroups
        self._invalidate_cache('groups')
        groups_lookup = self._create_code_lookup(self._get_all_cached('groups'))
        self._import_groups_phase(df_groups, sheet.columns, depts_lookup, 
                                  set(groups_lookup.keys()), stats, errors, db_manager, 
                                  parent_phase=False, groups_lookup=groups_lookup)
        
        self._invalidate_cache('groups')
    
    def _import_groups_phase(self, df, cols, depts_lookup, existing_codes, stats, errors, 
                            db_manager, parent_phase: bool, groups_lookup=None):
        """Helper to import groups in two phases"""
        for idx, row in df.iterrows():
            try:
                has_parent = pd.notna(row.get(cols['parent_code'], None)) and row[cols['parent_code']]
                if parent_phase and has_parent:
                    continue
                if not parent_phase and not has_parent:
                    continue
                
                code = str(row[cols['code']])
                if code in existing_codes:
                    stats['grupy']['skipped'] += 1
                    continue
                
                dept = depts_lookup.get(row[cols['department_code']])
                if not dept:
                    stats['grupy']['skipped'] += 1
                    errors.append(f"Nie znaleziono wydziału {row[cols['department_code']]}")
                    continue
                
                parent_id = None
                if not parent_phase and groups_lookup:
                    parent = groups_lookup.get(row[cols['parent_code']])
                    parent_id = parent[0] if parent else None
                
                self.repos['groups'].insert({
                    'code': code,
                    'name': str(row[cols['name']]),
                    'department_id': dept[0],
                    'students_count': int(row[cols['student_count']]),
                    'accessibility_requirements': json.dumps({}),
                    'parent_group_id': parent_id
                })
                stats['grupy']['added'] += 1
                existing_codes.add(code)
            except Exception as e:
                db_manager.conn.rollback()
                stats['grupy']['skipped'] += 1
                errors.append(f"Grupa wiersz {idx+2}: {str(e)}")
    
    def _import_teachers(self, excel_file, excel_data, stats, errors, db_manager):
        """Import teachers from Excel"""
        depts_lookup = self._create_code_lookup(self._get_all_cached('departments'))
        teachers_lookup = self._create_name_lookup(self._get_all_cached('teachers'), 1, 2)
        
        def check_exists(row, cols, existing):
            name = f"{row[cols['first_name']]} {row[cols['last_name']]}"
            if name in existing:
                return True
            existing.add(name)
            return False
        
        def prepare(row, cols):
            dept = depts_lookup.get(row[cols['department_code']])
            if not dept:
                errors.append(f"Nie znaleziono wydziału {row[cols['department_code']]}")
                return None
            return {
                'first_name': str(row[cols['first_name']]),
                'last_name': str(row[cols['last_name']]),
                'department_id': dept[0],
                'accessibility': json.dumps({})
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['teachers'],
            'teachers', 'prowadzacy', stats, errors, db_manager,
            prepare, check_exists, existing_items=set(teachers_lookup.keys())
        )
        
        self._invalidate_cache('teachers')
    
    def _import_courses(self, excel_file, excel_data, stats, errors, db_manager):
        """Import courses from Excel"""
        depts_lookup = self._create_code_lookup(self._get_all_cached('departments'))
        existing_codes = {c[1] for c in self._get_all_cached('courses')}
        
        def check_exists(row, cols, existing):
            code = str(row[cols['code']])
            if code in existing:
                return True
            existing.add(code)
            return False
        
        def prepare(row, cols):
            dept = depts_lookup.get(row[cols['department_code']])
            if not dept:
                errors.append(f"Nie znaleziono wydziału {row[cols['department_code']]}")
                return None
            return {
                'code': str(row[cols['code']]),
                'name': str(row[cols['name']]),
                'department_id': dept[0],
                'type': str(row[cols['type']]).strip().lower(),
                'hours_per_semester': int(row[cols['hours']])
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['courses'],
            'courses', 'przedmioty', stats, errors, db_manager,
            prepare, check_exists, existing_items=existing_codes
        )
        
        self._invalidate_cache('courses')
    
    def _import_course_assignments(self, excel_file, excel_data, stats, errors, db_manager):
        """Import course assignments from Excel"""
        courses_lookup = self._create_code_lookup(self._get_all_cached('courses'))
        groups_lookup = self._create_code_lookup(self._get_all_cached('groups'))
        teachers_lookup = self._create_name_lookup(self._get_all_cached('teachers'), 1, 2)
        existing = {(ca[1], ca[2], ca[3], str(ca[4])) for ca in self._get_all_cached('course_assignments')}
        
        def check_exists(row, cols, existing_set):
            course = courses_lookup.get(row[cols['course_code']])
            group = groups_lookup.get(row[cols['group_code']])
            teacher = teachers_lookup.get(str(row[cols['teacher_full_name']]).strip())
            if not (course and group and teacher):
                return False
            key = (course[0], group[0], teacher[0], str(row[cols['semester']]))
            if key in existing_set:
                return True
            existing_set.add(key)
            return False
        
        def prepare(row, cols):
            course = courses_lookup.get(row[cols['course_code']])
            if not course:
                errors.append(f"Nie znaleziono przedmiotu {row[cols['course_code']]}")
                return None
            
            group = groups_lookup.get(row[cols['group_code']])
            if not group:
                errors.append(f"Nie znaleziono grupy {row[cols['group_code']]}")
                return None
            
            teacher = teachers_lookup.get(str(row[cols['teacher_full_name']]).strip())
            if not teacher:
                errors.append(f"Nie znaleziono prowadzącego {row[cols['teacher_full_name']]}")
                return None
            
            return {
                'course_id': course[0],
                'group_id': group[0],
                'teacher_id': teacher[0],
                'semester': str(row[cols['semester']]),
                'note': None
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['course_assignments'],
            'course_assignments', 'przypisania', stats, errors, db_manager,
            prepare, check_exists, existing_items=existing
        )
    
    def _import_schedule(self, excel_file, excel_data, stats, errors, db_manager):
        """Import schedule from Excel"""
        # Delete old schedule first
        try:
            self.repos['assignments'].delete_all()
            self._invalidate_cache('assignments')
        except Exception:
            db_manager.conn.rollback()
        
        courses_lookup = self._create_code_lookup(self._get_all_cached('courses'))
        groups_lookup = self._create_code_lookup(self._get_all_cached('groups'))
        teachers_lookup = self._create_name_lookup(self._get_all_cached('teachers'), 1, 2)
        rooms_lookup = self._create_code_lookup(self._get_all_cached('rooms'), code_index=2)
        course_assignments = {(ca[1], ca[2], ca[3]): ca for ca in self._get_all_cached('course_assignments')}
        
        def prepare(row, cols):
            course = courses_lookup.get(row[cols['course_code']])
            group = groups_lookup.get(row[cols['group_code']])
            teacher = teachers_lookup.get(str(row[cols['teacher_full_name']]).strip())
            
            if not (course and group and teacher):
                errors.append("Nie znaleziono przedmiotu/grupy/prowadzącego")
                return None
            
            ca = course_assignments.get((course[0], group[0], teacher[0]))
            if not ca:
                errors.append("Nie znaleziono przypisania przedmiotu")
                return None
            
            room = rooms_lookup.get(row[cols['room_code']])
            if not room:
                errors.append(f"Nie znaleziono sali {row[cols['room_code']]}")
                return None
            
            return {
                'course_assignment_id': ca[0],
                'room_id': room[0],
                'weekday': str(row[cols['weekday']]).strip().lower(),
                'start_time': parse_time(row[cols['start_time']]),
                'end_time': parse_time(row[cols['end_time']]),
                'week_parity': str(row[cols['parity']]).strip().lower(),
                'note': str(row[cols['note']]) if pd.notna(row[cols['note']]) else None
            }
        
        self._generic_import(
            excel_file, excel_data, EXCEL_SCHEMA['schedule'],
            'assignments', 'plan', stats, errors, db_manager,
            prepare, None
        )
