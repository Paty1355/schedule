WEEKDAYS_CONFIG = [
    {'en': 'monday',    'pl': 'Poniedziałek', 'order': 1},
    {'en': 'tuesday',   'pl': 'Wtorek',       'order': 2},
    {'en': 'wednesday', 'pl': 'Środa',        'order': 3},
    {'en': 'thursday',  'pl': 'Czwartek',     'order': 4},
    {'en': 'friday',    'pl': 'Piątek',       'order': 5},
    {'en': 'saturday',  'pl': 'Sobota',       'order': 6},
    {'en': 'sunday',    'pl': 'Niedziela',    'order': 7}
]

WEEKDAYS = [day['en'] for day in WEEKDAYS_CONFIG]
WEEKDAY_OPTIONS_PL = [day['pl'] for day in WEEKDAYS_CONFIG]
WEEKDAY_LABELS_PL = {day['en']: day['pl'] for day in WEEKDAYS_CONFIG}
WEEKDAY_PL_TO_EN = {day['pl']: day['en'] for day in WEEKDAYS_CONFIG}
WEEKDAY_ORDER = {day['en']: day['order'] for day in WEEKDAYS_CONFIG}


ROOM_TYPES = [
    'lecture_hall',
    'classroom',
    'auditorium',
    'computer_lab',
    'chemistry_lab',
    'physics_lab',
    'biology_lab',
    'language_lab',
    'seminar_room',
    'workshop',
    'gym',
    'other'
]

ROOM_TYPE_LABELS_PL = {
    'lecture_hall': 'Sala wykładowa',
    'classroom': 'Sala ćwiczeniowa',
    'auditorium': 'Audytorium',
    'computer_lab': 'Lab. komputerowe',
    'chemistry_lab': 'Lab. chemiczne',
    'physics_lab': 'Lab. fizyczne',
    'biology_lab': 'Lab. biologiczne',
    'language_lab': 'Lab. językowe',
    'seminar_room': 'Sala seminaryjna',
    'workshop': 'Warsztat',
    'gym': 'Sala gimnastyczna',
    'other': 'Inna'
}


COURSE_TYPES = [
    'lecture',
    'exercise',
    'seminar',
    'project',
    'computer_lab',
    'chemistry_lab',
    'physics_lab',
    'biology_lab',
    'language_lab',
    'workshop',
    'gym_class',
    'other'
]

COURSE_TYPE_LABELS_PL = {
    'lecture': 'Wykład',
    'exercise': 'Ćwiczenia',
    'seminar': 'Seminarium',
    'project': 'Projekt',
    'computer_lab': 'Lab. komputerowe',
    'chemistry_lab': 'Lab. chemiczne',
    'physics_lab': 'Lab. fizyczne',
    'biology_lab': 'Lab. biologiczne',
    'language_lab': 'Lab. językowe',
    'workshop': 'Warsztat',
    'gym_class': 'WF',
    'other': 'Inne'
}


COURSE_TO_ROOM_TYPE_MAPPING = {
    'lecture': ['lecture_hall', 'auditorium'],
    'exercise': ['classroom', 'seminar_room'],
    'seminar': ['seminar_room', 'classroom'],
    'project': ['classroom', 'seminar_room'],
    'computer_lab': ['computer_lab'],
    'chemistry_lab': ['chemistry_lab'],
    'physics_lab': ['physics_lab'],
    'biology_lab': ['biology_lab'],
    'language_lab': ['language_lab', 'classroom'],
    'workshop': ['workshop'],
    'gym_class': ['gym'],
    'other': ['other', 'classroom']
}


WEEK_PARITY_OPTIONS = {
    'Oba (co tydzień)': 'both',
    'Parzyste': 'even',
    'Nieparzyste': 'odd'
}

WEEK_PARITY_LABELS_PL = {
    'both': 'Oba',
    'even': 'Parzyste',
    'odd': 'Nieparzyste'
}


CONFLICT_WEIGHTS = {
    'teacher_conflicts': 100,
    'group_conflicts': 100,
    'room_conflicts': 50,
    'capacity_violations': 75,
    'room_type_mismatch': 100
}