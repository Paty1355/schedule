from __future__ import annotations
from typing import Optional, List, Dict
import numpy as np

from genetic_algorithm.genetic_algorithms_tool.algorithm_data_schema import Chromosome
from genetic_algorithm.data_model.teacher import Teacher_unavailabities
from genetic_algorithm.data_model.group import GroupUnavailabilities
from utils.type_mappings import *

class ScheduleFitness:
    def __init__(self,
         # Obligatory
         overlaps_penalty=35, #Kara za nachodzenie się zajęć
         unavailable_time_penalty=35, #Kara za nieprzestrzeganie niedostępności

         #Teacher obligatory
         teacher_overlaps_penalty=None, #Kara za nachodzenie się zajęć dla prowadzącego
         teacher_unavailable_time_penalty=None, #Kara za nieprzestrzeganie niedostępności prowadzącego

         #Group obligatory
         group_overlaps_penalty=None, #Kara za nachodzenie się zajęc dla grupy
         group_unavailable_time_penalty=None, #Kara za nieprzestrzeganie niedostępności grupy

         #Room obligatory
         room_capacity_penalty=5,  # Kara za każdego studenta bez miejsca (proporcjonalna)
         room_type_mismatch_penalty=35,  # Kara za zły typ sali
         room_overlaps_penalty=None,
         room_accessibility_penalty=35,

         #Optional
         teacher_gaps_penalty=0.2, #Kara za okna
         teacher_daily_load_penalty=0.2, #Kara za za małą ilość zajęć danego dnia
         teacher_after_hours_penalty=0.2, #Ilość kary za pracowanie np.po 17
         teacher_end_hour_limit=18, #Przekroczenie pracowanie np. po 17
         teacher_travel_distance_penalty=0.2, #Kara za przechodzenie między wydziałami dotyczy (kolejnych zajęć)
         teacher_wrong_department_penalty=0.2, #Kara za zajęcia w innym wydziale

         group_gaps_penalty=0.2,
         group_daily_load_penalty=0.2,
         group_after_hours_penalty=0.2,
         group_end_hour_limit=18, #Godzina -> 8
         group_travel_distance_penalty=0.2,
         group_wrong_department_penalty=0.2
                 ):

        penalties = [
            overlaps_penalty,
            unavailable_time_penalty,
            room_capacity_penalty,
            room_type_mismatch_penalty,
            teacher_overlaps_penalty,
            teacher_unavailable_time_penalty,
            room_overlaps_penalty,
            room_accessibility_penalty,
            group_overlaps_penalty,
            group_unavailable_time_penalty,
            teacher_gaps_penalty,
            teacher_daily_load_penalty,
            teacher_after_hours_penalty,
            teacher_travel_distance_penalty,
            teacher_wrong_department_penalty,
            group_gaps_penalty,
            group_daily_load_penalty,
            group_after_hours_penalty,
            group_travel_distance_penalty,
            group_wrong_department_penalty
        ]
        for p in penalties:
            if p is None:
                continue
            if p < 0:
                raise ValueError(f"Penalty value cannot be negative: {p}")

        self.teacher_overlaps_penalty=teacher_overlaps_penalty if teacher_overlaps_penalty is not None else overlaps_penalty
        self.teacher_unavailable_time_penalty=teacher_unavailable_time_penalty if teacher_unavailable_time_penalty is not None else unavailable_time_penalty
        self.teacher_gaps_penalty=teacher_gaps_penalty
        self.teacher_daily_load_penalty=teacher_daily_load_penalty
        self.teacher_after_hours_penalty=teacher_after_hours_penalty
        self.teacher_end_hour_limit=teacher_end_hour_limit
        self.teacher_travel_distance_penalty=teacher_travel_distance_penalty
        self.teacher_wrong_department_penalty=teacher_wrong_department_penalty

        self.room_overlaps_penalty = room_overlaps_penalty if room_overlaps_penalty is not None else overlaps_penalty
        self.room_accessibility_penalty = room_accessibility_penalty

        self.group_overlaps_penalty=group_overlaps_penalty if group_overlaps_penalty is not None else overlaps_penalty
        self.group_unavailable_time_penalty=group_unavailable_time_penalty if group_unavailable_time_penalty is not None else unavailable_time_penalty
        self.group_gaps_penalty=group_gaps_penalty
        self.group_daily_load_penalty=group_daily_load_penalty
        self.group_after_hours_penalty=group_after_hours_penalty
        self.group_end_hour_limit=group_end_hour_limit
        self.group_travel_distance_penalty=group_travel_distance_penalty
        self.group_wrong_department_penalty=group_wrong_department_penalty

        self.room_capacity_penalty=room_capacity_penalty
        self.room_type_mismatch_penalty=room_type_mismatch_penalty

        for p in (self.teacher_overlaps_penalty, self.teacher_unavailable_time_penalty, self.room_overlaps_penalty,self.group_overlaps_penalty,self.group_unavailable_time_penalty,self.room_capacity_penalty, self.room_type_mismatch_penalty, self.room_accessibility_penalty):
            if p is None:
                raise ValueError(f"Penalty value cannot be None: {p}")

    def calculate_fittnes(self, chromosome, teachers_unav, groups_unav):
        for g in chromosome.genes:
            g.flag = False
        teacher_score = self.fitness_teacher(chromosome, teachers_unav)
        group_score = self.fitness_group(chromosome, groups_unav)
        room_score = self.fitness_room(chromosome)

        total_score = teacher_score + group_score + room_score
        return total_score

    def fitness_teacher(self, chromosome:Chromosome, teachers_unavailabilities: Optional[Dict[int, List[Teacher_unavailabities]]] = None) -> float:
        #Referancja do słownika z Teacher_unavailabities
        conflict = 0
        for teacher_id, gene_indices in chromosome.teacher_chromosome.items():
            # print("Nauczyciel ",teacher_id)
            teacher_gen = [chromosome.genes[i] for i in gene_indices] #Uzyskuje miejsca pamięci każdego z genów
            n=len(teacher_gen)

            start_time_course = np.array([i.time_slot_id.start_time.hour*60+i.time_slot_id.start_time.minute for i in teacher_gen])
            end_time_course = np.array([i.time_slot_id.end_time.hour*60+i.time_slot_id.end_time.minute for i in teacher_gen])
            weekdays_numeric_value = {
                'monday': 1,
                'tuesday': 2,
                'wednesday': 3,
                'thursday': 4,
                'friday': 5,
                'saturday': 6,
                'sunday': 7
            }
            weekdays_course = np.array([weekdays_numeric_value[i.weekday] for i in teacher_gen])
            week_parities_numeric_value = {
                'odd': 1,
                'even': 2,
                'both': 3
            }
            week_parities = np.array([week_parities_numeric_value[i.week_parity] for i in teacher_gen])
            departament_id = np.array([i.room_id.building_id for i in teacher_gen]) #Dane o wydziale, wykorzytujemy nizej

            # -------Nachodzenie się zajęć
            if(n>1):
                time_conflict = ((start_time_course[:, None] < end_time_course[None, :]) &
                                 (start_time_course[None, :] < end_time_course[:, None])) #Macierz z wartościami True na zajęciach nakładających się na siebie
                same_day = weekdays_course[:, None] == weekdays_course[None,:]#Macierz nachodzenia się dni
                same_week = ((week_parities[:, None] == week_parities[None, :])| #Macierz nachodzenia się tyoodni
                            (week_parities[:, None] == 3)|
                            (week_parities[None, :] == 3))
                mask_upper = np.triu(np.ones((n, n), dtype=bool), k=1) #Macierz lewostronna błędu

                # if(np.sum(time_conflict & same_day & same_week & mask_upper)):
                #     print("Naliczam kare na nachodzące się zajecia w ilości nauczyciela")
                #     print(np.sum(time_conflict & same_day & same_week & mask_upper))
                #     print(f"Nauczyciel {teacher_gen[0].course_assignment_id.teacher_id.first_name} {teacher_gen[0].course_assignment_id.teacher_id.last_name}  ")
                #     print("Poczatek lekcji")
                #     print(start_time_course)
                #     print("Koniec lekcji")
                #     print(end_time_course)
                #     print("Dzien lekcji")
                #     print(weekdays_course)
                #     print("Tydzien lekcji")
                #     print(week_parities)

                conflict += np.sum(time_conflict & same_day & same_week & mask_upper)*self.teacher_overlaps_penalty

                matrix_conflict = (time_conflict & same_day & same_week & mask_upper) #Macierz z wartościami TRUE/FALSE - nachodzenie się zajeć
                bad_i, bad_j = np.where(matrix_conflict)
                for ii, jj in zip(bad_i, bad_j):
                    # print(f"Ustawiam dla genotypu {chromosome.genes[gene_indices[ii]].id}")
                    chromosome.genes[gene_indices[ii]].flag = True
                    chromosome.genes[gene_indices[jj]].flag = True

            # ------ Nachodzenie na zajecia w czasie niedostepność nauczyciela
            if(teachers_unavailabilities and self.teacher_unavailable_time_penalty is not None):
                unav_list = teachers_unavailabilities[teacher_id]
                start_time_teacher_unavailabities = np.array([i.start_time.hour*60+i.start_time.minute for i in unav_list])
                end_time_teacher_unavailabities = np.array([i.end_time.hour*60+i.end_time.minute for i in unav_list])
                weekdays_teacher_unavailabities = np.array([weekdays_numeric_value[i.weekday] for i in unav_list])


                time_conflict_unavailabilities = ((start_time_course[:,None] < end_time_teacher_unavailabities[None,:]) &
                                                  (end_time_course[:,None]> start_time_teacher_unavailabities[None,:]) &
                                                  (weekdays_course[:,None] == weekdays_teacher_unavailabities[None,:]))

                # if (np.sum(time_conflict_unavailabilities)):
                #     print("Naliczam kare Nachodzenie na zajecia w czasie niedostepność nauczyiela")
                #     print(np.sum(time_conflict_unavailabilities))

                conflict += np.sum(time_conflict_unavailabilities)*self.teacher_unavailable_time_penalty
                if np.any(time_conflict_unavailabilities):
                    bad_indices = np.where(time_conflict_unavailabilities[:, 0])[0]
                    for idx in bad_indices:
                        chromosome.genes[gene_indices[idx]].flag = True

            if((self.teacher_after_hours_penalty is not None and self.teacher_end_hour_limit is not None)): # Kara za zajęcia po danej godzinie
                teacher_after_hours_penalty_to_minute = self.teacher_end_hour_limit*60
                course_after_hours_penalty = np.where(start_time_course>=teacher_after_hours_penalty_to_minute)[0]
                conflict+=len(course_after_hours_penalty)*self.teacher_after_hours_penalty

                # if (len(course_after_hours_penalty)):
                #     print("Naliczam kare za zajęcia po danej godzinie")
                #     print(len(course_after_hours_penalty))


            #Kara za długą przerwe(okna), małą ilość zajęć danego dnia,

            if(self.teacher_gaps_penalty is not None):
                #Zrobić do porządku if
                for day in np.unique(weekdays_course):
                    course_idx_day = np.where(weekdays_course==day)[0]

                    if len(course_idx_day)<2: #Kara za za małą ilość zajęć
                        conflict += self.teacher_daily_load_penalty if self.teacher_daily_load_penalty is not None else 0
                        continue

                    start_course_day = start_time_course[course_idx_day]
                    end_course_day = end_time_course[course_idx_day]

                    order = np.argsort(start_course_day)
                    start_course_day = start_course_day[order]
                    end_course_day = end_course_day[order]

                    gaps = abs(start_course_day[1:]-end_course_day[:-1])
                    conflict += np.sum(np.count_nonzero(gaps[gaps>30])*self.teacher_gaps_penalty)

                    # if (np.sum(np.count_nonzero(gaps[gaps>30]))):
                    #     print("Naliczam kare  za za małą ilość zajęć")
                    #     print(np.sum(np.count_nonzero(gaps[gaps>30])))

                    #Kara za przechodzenie pomiędzy wydziałami i za zajęcia na obcym wydziale

                    if(self.teacher_overlaps_penalty or self.teacher_wrong_department_penalty is not None):
                        departament_id_day = departament_id[course_idx_day]
                        departament_id_day=departament_id_day[order]

                        if(self.teacher_overlaps_penalty is not None): #Kara za przechodzenie pomiędzy wydziałami
                            travel_department = departament_id_day[:-1]!=departament_id_day[1:] #Tablica true false określająca czy kolejne zajęcia są realzowane są w tym samym budynku
                            conflict+= np.sum(np.count_nonzero(travel_department)*self.teacher_travel_distance_penalty)

                            # if (np.sum(np.count_nonzero(travel_department))):
                            #     print("Naliczam Kara za przechodzenie pomiędzy wydziałami")
                            #     print(np.sum(np.count_nonzero(travel_department)))

                        if(self.teacher_wrong_department_penalty is not None): #Kara za zajęcia na obcym wydziale
                            conflict += np.sum(np.count_nonzero(departament_id_day != teacher_gen[0].course_assignment_id.teacher_id.department_id)*self.teacher_wrong_department_penalty)

                            # if (np.sum(np.count_nonzero(departament_id_day != teacher_gen[0].course_assignment_id.teacher_id.department_id))):
                            #     print("Naliczam Kara za zajęcia na obcym wydziale")
                            #     print(np.sum(np.count_nonzero(departament_id_day != teacher_gen[0].course_assignment_id.teacher_id.department_id)))
        return conflict

    def fitness_group(self, chromosome: Chromosome,
                      groups_unavailabilities: Optional[Dict[int, List[GroupUnavailabilities]]] = None) -> float:
        # Referancja do słownika z group_unavailabities
        conflict = 0
        for group_id, gene_indices in chromosome.group_chromosome.items():
            # print("Grupa ", group_id)
            group_gen = [chromosome.genes[i] for i in gene_indices]  # Uzyskuje miejsca pamięci każdego z genów
            n = len(group_gen)

            start_time_course = np.array(
                [i.time_slot_id.start_time.hour * 60 + i.time_slot_id.start_time.minute for i in group_gen])
            end_time_course = np.array(
                [i.time_slot_id.end_time.hour * 60 + i.time_slot_id.end_time.minute for i in group_gen])
            weekdays_numeric_value = {
                'monday': 1,
                'tuesday': 2,
                'wednesday': 3,
                'thursday': 4,
                'friday': 5,
                'saturday': 6,
                'sunday': 7
            }
            weekdays_course = np.array([weekdays_numeric_value[i.weekday] for i in group_gen])
            week_parities_numeric_value = {
                'odd': 1,
                'even': 2,
                'both': 3
            }
            week_parities = np.array([week_parities_numeric_value[i.week_parity] for i in group_gen])
            departament_id = np.array(
                [i.room_id.building_id for i in group_gen])  # Dane o wydziale, wykorzytujemy nizej

            # -------Nachodzenie się zajęć
            if (n >1 ): #Wcześniej było n<2

                time_conflict = ((start_time_course[:, None] < end_time_course[None, :]) &
                                 (start_time_course[None, :] < end_time_course[:,
                                                               None]))  # Macierz z wartościami True na zajęciach nakładających się na siebie
                same_day = weekdays_course[:, None] == weekdays_course[None, :]  # Macierz nachodzenia się dni
                same_week = ((week_parities[:, None] == week_parities[None, :]) |  # Macierz nachodzenia się tyoodni
                             (week_parities[:, None] == 3) |
                             (week_parities[None, :] == 3))
                mask_upper = np.triu(np.ones((n, n), dtype=bool), k=1)  # Macierz lewostronna błędu

                # print(time_conflict & same_day & same_week & mask_upper)
                # print(np.sum(time_conflict & same_day & same_week & mask_upper))
                # if (np.sum(time_conflict & same_day & same_week & mask_upper)):
                #     print("Naliczam kare na nachodzące się zajecia w ilości grupy")
                #     print(np.sum(time_conflict & same_day & same_week & mask_upper))
                #
                #     print("Poczatek lekcji")
                #     print(start_time_course)
                #     print("Koniec lekcji")
                #     print(end_time_course)
                #     print("Dzien lekcji")
                #     print(weekdays_course)
                #     print("Tydzien lekcji")
                #     print(week_parities)

                conflict += np.sum(time_conflict & same_day & same_week & mask_upper) * self.group_overlaps_penalty

                matrix_conflict = (time_conflict & same_day & same_week & mask_upper)
                bad_i, bad_j = np.where(matrix_conflict)
                for ii, jj in zip(bad_i, bad_j):
                    #print(f"Ustawiam dla genotypu {chromosome.genes[gene_indices[ii]].id}")
                    chromosome.genes[gene_indices[ii]].flag = True
                    chromosome.genes[gene_indices[jj]].flag = True

            # ------ Nachodzenie na zajecia w czasie niedostepność nauczyciela
            if (groups_unavailabilities and self.group_unavailable_time_penalty is not None):
                unav_list = groups_unavailabilities[group_id]
                start_time_group_unavailabities = np.array(
                    [i.start_time.hour * 60 + i.start_time.minute for i in unav_list])
                end_time_group_unavailabities = np.array([i.end_time.hour * 60 + i.end_time.minute for i in unav_list])
                weekdays_group_unavailabities = np.array([weekdays_numeric_value[i.weekday] for i in unav_list])

                time_conflict_unavailabilities = (
                            (start_time_course[:, None] < end_time_group_unavailabities[None, :]) &
                            (end_time_course[:, None] > start_time_group_unavailabities[None, :]) &
                            (weekdays_course[:, None] == weekdays_group_unavailabities[None, :]))

                conflict += np.sum(time_conflict_unavailabilities) * self.group_unavailable_time_penalty

                if np.any(time_conflict_unavailabilities):
                    bad_indices = np.where(time_conflict_unavailabilities[:, 0])[0]
                    for idx in bad_indices:
                        chromosome.genes[gene_indices[idx]].flag = True

            if ((
                    self.group_after_hours_penalty is not None and self.group_end_hour_limit is not None)):  # Kara za zajęcia po danej godzinie
                group_after_hours_penalty_to_minute = self.group_end_hour_limit * 60
                course_after_hours_penalty = np.where(start_time_course >= group_after_hours_penalty_to_minute)[0]
                conflict += len(course_after_hours_penalty) * self.group_after_hours_penalty

            # Kara za długą przerwe(okna), małą ilość zajęć danego dnia,

            if (self.group_gaps_penalty is not None):
                # Zrobić do porządku if
                for day in np.unique(weekdays_course):
                    course_idx_day = np.where(weekdays_course == day)[0]

                    if len(course_idx_day) < 2:  # Kara za za małą ilość zajęć
                        conflict += self.group_daily_load_penalty if self.group_daily_load_penalty is not None else 0
                        continue

                    start_course_day = start_time_course[course_idx_day]
                    end_course_day = end_time_course[course_idx_day]

                    order = np.argsort(start_course_day)
                    start_course_day = start_course_day[order]
                    end_course_day = end_course_day[order]

                    gaps = abs(start_course_day[1:] - end_course_day[:-1])
                    conflict += np.sum(np.count_nonzero(gaps[gaps > 30]) * self.group_gaps_penalty)

                    # Kara za przechodzenie pomiędzy wydziałami i za zajęcia na obcym wydziale

                    if (self.group_overlaps_penalty is not None or self.group_wrong_department_penalty):
                        departament_id_day = departament_id[course_idx_day]
                        departament_id_day = departament_id_day[order]

                        if (self.group_travel_distance_penalty is not None):  # Kara za przechodzenie pomiędzy wydziałami
                            travel_department = departament_id_day[:-1] != departament_id_day[
                                                                           1:]  # Tablica true false określająca czy kolejne zajęcia są realzowane są w tym samym budynku
                            conflict += np.sum(np.count_nonzero(travel_department) * self.group_travel_distance_penalty)

                        if (self.group_wrong_department_penalty is not None):  # Kara za zajęcia na obcym wydziale
                            conflict += np.sum(np.count_nonzero(departament_id_day != group_gen[
                                0].course_assignment_id.group_id.department_id) * self.group_wrong_department_penalty)

        return conflict


    def fitness_room(self, chromosome:Chromosome) -> float:
        conflict = 0

        for room_id, gene_indices in chromosome.room_chromosome.items():
            room_gen = [chromosome.genes[i] for i in gene_indices]
            n=len(room_gen)
            # print("Sala id", room_id)

            start_time_course = np.array([i.time_slot_id.start_time.hour*60+i.time_slot_id.start_time.minute for i in room_gen])
            end_time_course = np.array([i.time_slot_id.end_time.hour*60+i.time_slot_id.end_time.minute for i in room_gen])

            weekdays_numeric_value = {
                'monday': 1,
                'tuesday': 2,
                'wednesday': 3,
                'thursday': 4,
                'friday': 5,
                'saturday': 6,
                'sunday': 7
            }

            weekdays_course = np.array([weekdays_numeric_value[i.weekday] for i in room_gen])
            week_parities_numeric_value = {
                'odd': 1,
                'even': 2,
                'both': 3
            }
            week_parities = np.array([week_parities_numeric_value[i.week_parity] for i in room_gen])

            # -------Nachodzenie się zajęć
            if (n > 1):
                time_conflict = ((start_time_course[:, None] < end_time_course[None, :]) &
                                 (start_time_course[None, :] < end_time_course[:,
                                                               None]))  # Macierz z wartościami True na zajęciach nakładających się na siebie
                same_day = weekdays_course[:, None] == weekdays_course[None, :]  # Macierz nachodzenia się dni
                same_week = ((week_parities[:, None] == week_parities[None, :]) |  # Macierz nachodzenia się tyoodni
                             (week_parities[:, None] == 3) |
                             (week_parities[None, :] == 3))
                mask_upper = np.triu(np.ones((n, n), dtype=bool), k=1)  # Macierz lewostronna błędu

                conflict += np.sum(time_conflict & same_day & same_week & mask_upper)*self.room_overlaps_penalty

                matrix_conflict = (
                            time_conflict & same_day & same_week & mask_upper)  # Macierz z wartościami TRUE/FALSE - nachodzenie się zajeć
                bad_i, bad_j = np.where(matrix_conflict)
                for ii, jj in zip(bad_i, bad_j):
                    # print(f"Ustawiam dla genotypu {chromosome.genes[gene_indices[ii]].id}")
                    chromosome.genes[gene_indices[ii]].flag = True
                    chromosome.genes[gene_indices[jj]].flag = True

                # if (np.sum(time_conflict & same_day & same_week & mask_upper)):
                #     print("Naliczam kare na nachodzące się zajecia w sali")
                #     print(np.sum(time_conflict & same_day & same_week & mask_upper))
                #     print("Poczatek lekcji")
                #     print(start_time_course)
                #     print("Koniec lekcji")
                #     print(end_time_course)
                #     print("Dzien lekcji")
                #     print(weekdays_course)
                #     print("Tydzien lekcji")
                #     print(week_parities)



            #Kara za pojemność sali
            if(self.room_capacity_penalty is not None):
                room_capacity = room_gen[0].room_id.capacity
                student_count = np.array([i.course_assignment_id.group_id.students_count for i in room_gen])
                overflow_room = student_count - room_capacity  # Ile osób nie mieści się
                # Kara proporcjonalna do tego, ile osób się nie mieści (tylko dla przepełnionych sal)
                overflow_penalty = np.sum(overflow_room[overflow_room > 0])
                conflict += overflow_penalty * self.room_capacity_penalty

                # if (negative_overflow_count):
                #     print("Naliczam kare za pojemność sali")
                #     print( negative_overflow_count)

            #Dostępność ON sali
            if(self.room_accessibility_penalty is not None):
                room_accessibility = room_gen[0].room_id.accessibility or {} #Wymagania dostępnościowe sali
                group_accessibility_requirements = [i.course_assignment_id.group_id.accessibility_requirements or {} for i in room_gen]
                teacher_accessibility_requirements = [i.course_assignment_id.teacher_id.accessibility or {} for i in room_gen]

                for group_req, teacher_req in zip(group_accessibility_requirements, teacher_accessibility_requirements):
                    total_requirement = {} #
                    for key in set(room_accessibility.keys()).union(group_req.keys(),teacher_req.keys()): #Łączymy wymagania nauczyciela i grupy
                        total_requirement[key] = group_req.get(key, False) or teacher_req.get(key, False) #Wpisujemy True/False czy występuje jakaś niedospność Wozek:True/FAlse

                    for requirements_name, requirements_value in total_requirement.items(): #Nazwa_dostępności (Wozek), True/Fasle
                        if(requirements_value and not room_accessibility.get(requirements_name, False)):
                            conflict+=self.room_accessibility_penalty


                #Wymagania sali
            if(self.room_type_mismatch_penalty is not None):
                room_type = room_gen[0].room_id.type
                course_type_requirements = [i.course_assignment_id.course_id.type for i in room_gen]

                room_type_count_mismatch = 0
                for course_type in course_type_requirements:
                    course_type_value = course_type.value if hasattr(course_type, 'value') else course_type
                    room_type_value = room_type.value if hasattr(room_type, 'value') else room_type
                    if not is_room_type_compatible(course_type_value, room_type_value):
                        room_type_count_mismatch += 1
                conflict += room_type_count_mismatch * self.room_type_mismatch_penalty









        return conflict











