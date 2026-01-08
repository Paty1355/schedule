from __future__ import annotations
import copy
import random
from datetime import time
import numpy as np
from typing import List, Optional

from ..data_model.course import Course_assignments
from ..data_model.location import Rooms
from ..data_model.time_models import Week_parity, Time_slots, Weekdays
from .algorithm_data_schema import Gene

class ScheduleTools:
    start_time_course_in_minute = 8 * 60 #Domyślna wartość rozpoczęcia zajęć 8:00
    end_time_course_in_minute = 20 * 60 #Domyślna wartość ostatniego rozpoczęcia się zajęć 21:00

    slots = [
    480, 495, 510, 525,
    540, 555, 570, 585,
    600, 615, 630, 645,
    660, 675, 690, 705,
    720, 735, 750, 765,
    780, 795, 810, 825,
    840, 855, 870, 885,
    900, 915, 930, 945,
    960, 975, 990, 1005,
    1020, 1035, 1050, 1065,
    1080, 1095, 1110, 1125,
    1140, 1155, 1170, 1185,
    1200
]

    weekdays_value = list(Weekdays)
    week_parity_value = list(Week_parity)

    column_to_exclude=['id','course_assignment_id','week_parity','note']


    def time_slots_generator(self, curse_time_per_week, idx):
        start_time_course= random.choice(self.slots)
        duration_minutes = int(curse_time_per_week * 60) #Czas zajęć w minutach w danym tyodniu

        end_time_course = start_time_course + duration_minutes

        if end_time_course > 1439: #Zajęcia koniec po 24:00 - wykrywanie błedu
            overflow = end_time_course - 1439
            end_time_course = 1439  # ustaw na 23:59
            start_time_course = 1439 - duration_minutes

        end_time_course = time(end_time_course // 60, end_time_course % 60)
        start_time_course = time(start_time_course//60, start_time_course%60)


        time_slot = Time_slots(
            id=idx,
            start_time=start_time_course,
            end_time = end_time_course,
            slot_order = 1 # Do zmiany
        )
        return time_slot

    def first_population_generator(self,course_assignments: Course_assignments, rooms:Rooms):
        genotype=[] #Lista propozycji planu dla kursów - Czyli Chromosom
        for i, course in enumerate(course_assignments,start=1):
            hours = course.course_id.hours_per_semester
            week_parity_value = (random.choice(self.week_parity_value) if hours <30 else Week_parity.both)
            time_slot = self.time_slots_generator(hours/(15 if week_parity_value.value == "both" else 7), i)
            genotype.append(
                Gene(
                    id=i,
                    course_assignment_id = course,
                    room_id = random.choice(rooms),
                    weekday= random.choice(self.weekdays_value),
                    week_parity = week_parity_value,
                    time_slot_id = time_slot
                )
            )
        return genotype

    def crossover_gene(self, g1:Gene, g2:Gene ):
        crossover_point = random.choice([2,3,5,6])
        #Dlaczego 2 i 3 - bo jedynie co możemy crossover to room_id pozycja 2, weekday pozycja 3, time_slot pozycja
        # 4 która bezpośrednio połączona jest z pozycją 5 week parity. Jeżeli podmienilibyśmy samo time_sloi ti bez week_parity to ilość zajęć
        # nam nie wyjdzie np: ustalamy 2h co tydzień -> a po mutacji dostaniemy 3h co tydzień co już jest nie taką wartością

        if crossover_point == 2:
            g1.room_id, g2.room_id = g2.room_id, g1.room_id
        elif crossover_point == 3:
            g1.room_id, g2.room_id = g2.room_id, g1.room_id
            g1.weekday, g2.weekday = g2.weekday, g1.weekday
        elif crossover_point == 5:
            g1.room_id, g2.room_id = g2.room_id, g1.room_id
            g1.time_slot_id, g2.time_slot_id = g2.time_slot_id, g1.time_slot_id
            g1.week_parity, g2.week_parity = g2.week_parity, g1.week_parity
        else:
            g1.weekday, g2.weekday = g2.weekday, g1.weekday
            g1.time_slot_id, g2.time_slot_id = g2.time_slot_id, g1.time_slot_id
            g1.week_parity, g2.week_parity = g2.week_parity, g1.week_parity
        return g1, g2


    def mutation_gene(self, g1:Gene, rooms:Rooms):

        if(random.random() < 0.85): #Mutate room_id
            g1.room_id = random.choice(rooms)

        if (random.random() < 0.85):  # Mutate weekday
            g1.weekday = random.choice(self.weekdays_value)

        if (random.random() < 0.85):  # Mutate Time_slots and Week_parity
            hours = g1.course_assignment_id.course_id.hours_per_semester
            week_parity_value = (random.choice(self.week_parity_value) if hours < 30 else Week_parity.both)
            g1.time_slot_id = self.time_slots_generator(hours/(15 if week_parity_value.value == "both" else 7), g1.time_slot_id.id)
            g1.week_parity = week_parity_value
        return g1



