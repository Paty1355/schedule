from collections import defaultdict
from typing import Optional, List, Tuple, Dict, Any
from pydantic import BaseModel
from genetic_algorithm.data_model.course import Course_assignments
from genetic_algorithm.data_model.location import *
from genetic_algorithm.data_model.time_models import Weekdays, Time_slots, Week_parity


class Gene(BaseModel):
    id: PositiveInt
    course_assignment_id: Course_assignments
    room_id: Rooms
    weekday: Weekdays
    time_slot_id: Time_slots
    week_parity: Week_parity
    note: Optional[str]=None
    flag: Optional[StrictBool]=False #False - brak kolizji, True kolizja

class Chromosome(BaseModel):
    genes: List[Gene]

    teacher_chromosome: dict[int,list[int]] #Tworzymy podzielone chromosomy dla danej jednostki np. Adam Kowalski
    group_chromosome: dict[int,list[int]] # Tworzymy chromosom dla grupy Eko2/3 - dla nich plan lekcji, dzieki temu obliczamy fittnes
    room_chromosome: dict[int,list[int]]

    fitness: float = 0


def Split_chromosome(genes: List[Gene], dict_of_unique_groups, path_to_group) -> Tuple[Dict[int, List[int]], Dict[int, List[int]], Dict[int, List[int]]]:

    teacher_chromosome: dict[int, set[int]] = defaultdict(set)
    group_chromosome: dict[int, set[int]] = defaultdict(set)
    room_chromosome: dict[int, set[int]] = defaultdict(set)

    def _extract_id(value):
        return getattr(value, 'id', value)

    for idx, gene in enumerate(genes):
        #Pobieramy z course_assignment_id jego elementy np. grupe
        ca = gene.course_assignment_id

        teacher = getattr(ca, 'teacher_id', None)
        group = getattr(ca, 'group_id', None)

        teacher_id = _extract_id(teacher) if teacher is not None else None
        group_id = _extract_id(group) if group is not None else None
        room_id = _extract_id(gene.room_id)

        if teacher_id is not None:
            teacher_chromosome[int(teacher_id)].add(idx)

        if group_id is not None:
            group_chromosome[int(group_id)].add(idx)
            if group_id in path_to_group: #Poberanie nadrzędnych group
                for parent_id in path_to_group[group_id]:
                    if parent_id in group_chromosome:
                        group_chromosome[int(group_id)].update(group_chromosome[parent_id])

        if room_id is not None:
            room_chromosome[int(room_id)].add(idx)

    return (
        {k: list(v) for k, v in teacher_chromosome.items()},
        {k: list(v) for k, v in group_chromosome.items()},
        {k: list(v) for k, v in room_chromosome.items()},
    )