# excel_schema.py
"""Shared Excel schema definitions used by import/export services."""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SheetSchema:
    """Static description of a worksheet with user-facing column names."""
    sheet_name: str
    columns: Dict[str, str]


EXCEL_SCHEMA: Dict[str, SheetSchema] = {
    'departments': SheetSchema(
        sheet_name='Wydzialy',
        columns={'code': 'kod', 'name': 'nazwa'}
    ),
    'buildings': SheetSchema(
        sheet_name='Budynki',
        columns={'name': 'nazwa', 'address': 'adres', 'department_code': 'kod_wydzialu'}
    ),
    'rooms': SheetSchema(
        sheet_name='Sale',
        columns={
            'code': 'kod',
            'name': 'nazwa',
            'building_name': 'nazwa_budynku',
            'capacity': 'pojemnosc',
            'type': 'typ',
            'note': 'notatki'
        }
    ),
    'groups': SheetSchema(
        sheet_name='Grupy',
        columns={
            'code': 'kod',
            'name': 'nazwa',
            'department_code': 'kod_wydzialu',
            'student_count': 'liczba_studentow',
            'parent_code': 'parent_kod'
        }
    ),
    'teachers': SheetSchema(
        sheet_name='Prowadzacy',
        columns={'first_name': 'imie', 'last_name': 'nazwisko', 'department_code': 'kod_wydzialu'}
    ),
    'courses': SheetSchema(
        sheet_name='Przedmioty',
        columns={'code': 'kod', 'name': 'nazwa', 'department_code': 'kod_wydzialu', 'type': 'typ', 'hours': 'godziny_semestr'}
    ),
    'course_assignments': SheetSchema(
        sheet_name='Przypisania',
        columns={
            'course_code': 'kod_przedmiotu',
            'group_code': 'kod_grupy',
            'teacher_full_name': 'prowadzacy',
            'semester': 'semestr'
        }
    ),
    'schedule': SheetSchema(
        sheet_name='PlanZajec',
        columns={
            'course_code': 'kod_przedmiotu',
            'group_code': 'kod_grupy',
            'teacher_full_name': 'prowadzacy',
            'room_code': 'kod_sali',
            'weekday': 'dzien_tygodnia',
            'start_time': 'od',
            'end_time': 'do',
            'parity': 'parzysto',
            'note': 'notatka'
        }
    )
}
