from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from database.db_manager import DBManager
from database.db_utils import conn_params, create_database_if_not_exists, run_sql_file
from database.repositories import (
    AssignmentRepository,
    CourseAssignmentsRepository,
    CoursesRepository,
    GroupUnavailabilitiesRepository,
    GroupsRepository,
    RoomsRepository,
    TeacherUnavailabilitiesRepository,
    TeachersRepository,
    TimeSlotsRepository,
)
from genetic_algorithm.data_loader import GADataLoader
from genetic_algorithm.genetic_algorithms_tool.genetic_algorithm import GeneticAlgorithm


def bootstrap_database() -> DBManager:
    dbname = conn_params.get("dbname", "timetable_db")
    create_database_if_not_exists(conn_params, dbname)
    db_manager = DBManager(conn_params)
    schema_path = Path(__file__).resolve().parents[1] / "database" / "db_schema.sql"
    run_sql_file(conn_params, str(schema_path))
    return db_manager


def build_repositories(db_manager: DBManager) -> dict:
    return {
        "rooms": RoomsRepository(db_manager),
        "courses": CoursesRepository(db_manager),
        "groups": GroupsRepository(db_manager),
        "teachers": TeachersRepository(db_manager),
        "course_assignments": CourseAssignmentsRepository(db_manager),
        "time_slots": TimeSlotsRepository(db_manager),
        "assignments": AssignmentRepository(db_manager),
        "teacher_unavailabilities": TeacherUnavailabilitiesRepository(db_manager),
        "group_unavailabilities": GroupUnavailabilitiesRepository(db_manager),
    }


def main() -> None:
    db_manager = bootstrap_database()
    repos = build_repositories(db_manager)
    loader = GADataLoader(repos)
    data = loader.load()

    if not data["course_assignments"]:
        raise RuntimeError("Brak danych w tabeli course_assignments – dodaj rekordy i uruchom ponownie.")

    if not data["rooms"]:
        raise RuntimeError("Brak danych w tabeli rooms – uzupełnij sale w bazie.")

    if not data["time_slots"]:
        raise RuntimeError("Brak danych w tabeli time_slots – dodaj sloty czasowe.")

    teacher_unav = defaultdict(list)
    for unav in data["teacher_unavailabilities"]:
        teacher_unav[unav.teacher_id].append(unav)

    group_unav = defaultdict(list)
    for unav in data["group_unavailabilities"]:
        group_unav[unav.group_id].append(unav)

    ga = GeneticAlgorithm(
        course_assignments=data["course_assignments"],
        rooms=data["rooms"],
        time_slots=data["time_slots"],
        teachers_unavailabities=teacher_unav,
        groups_unavailabities=group_unav,
        population_size=100,
        generations=200,
        mutation_rate=0.05,
    )

    best = ga.run()
    print(f"Najlepszy wynik fitness: {best.fitness}")
    for gene in best.genes[:10]:
        ca = gene.course_assignment_id
        print(
            f"[{gene.weekday.value}] {ca.course_id.name} → {gene.room_id.code} (slot {gene.time_slot_id.id})"
        )

    db_manager.close()


if __name__ == "__main__":
    main()

# 3. Uruchamiamy algorytm
best_schedule = ga.run()

# 4. Wyświetlamy wynik
print("Najlepszy plan zajęć ma fitness:", best_schedule.fitness)
print("Genes (plan zajęć):", best_schedule.genes)

for group_id, gene_indices in best_schedule.group_chromosome.items():
    group_gen = [best_schedule.genes[i] for i in gene_indices]
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

    print(f"Plan lekcji dla grupy {group_gen[0].course_assignment_id.group_id.code}")
    print("Poczatek lekcji")
    print(start_time_course)
    print("Koniec lekcji")
    print(end_time_course)
    print("Dzien lekcji")
    print(weekdays_course)
    print("Tydzien lekcji")
    print(week_parities)
