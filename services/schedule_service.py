"""schedule generation service - business logic"""

from collections import defaultdict
from types import SimpleNamespace
from typing import Any, Dict

from genetic_algorithm.data_loader import GADataLoader
from genetic_algorithm.genetic_algorithms_tool.genetic_algorithm import GeneticAlgorithm


class ScheduleService:
    """service for schedule generation and management"""

    def __init__(self, repos):
        self.repos = repos
        self.loader = GADataLoader(repos)

    def generate_schedule_with_ga(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schedule using the dedicated genetic algorithm stack."""
        data = self.loader.load()

        if not data["course_assignments"] or not data["rooms"]:
            return {"success": False, "error": "Brak wymaganych danych"}

        teacher_unav = defaultdict(list)
        for unav in data["teacher_unavailabilities"]:
            teacher_unav[unav.teacher_id].append(unav)

        group_unav = defaultdict(list)
        for unav in data["group_unavailabilities"]:
            group_unav[unav.group_id].append(unav)

        ga = GeneticAlgorithm(
            course_assignments=data["course_assignments"],
            rooms=data["rooms"],
            teachers_unavailabities=teacher_unav,
            groups_unavailabities=group_unav,
            population_size=params.get("population_size", 100),
            generations=params.get("generations", 200),
            mutation_rate=params.get("mutation_rate", 0.05),
        )

        best = ga.run()
        assignments = best.genes
        timetable = SimpleNamespace(assignments=assignments)
        report = self._build_validation_report(best)

        return {
            "success": True,
            "timetable": timetable,
            "fitness": best.fitness,
            "validation_report": report,
            "assignments": assignments,
            "chromosome": best,
        }

    def save_schedule_to_db(self, schedule: Any):
        """Persist generated schedule to the database."""
        genes = getattr(schedule, "assignments", schedule)
        db_manager = self.repos["assignments"].db_manager

        db_manager.cur.execute("DELETE FROM assignments")
        db_manager.conn.commit()

        for gene in genes:
            self.repos["assignments"].insert(
                {
                    "course_assignment_id": gene.course_assignment_id.id,
                    "room_id": gene.room_id.id,
                    "weekday": gene.weekday.value,
                    "start_time": gene.time_slot_id.start_time,
                    "end_time": gene.time_slot_id.end_time,
                    "week_parity": gene.week_parity.value,
                    "note": getattr(gene, "note", None),
                }
            )

    def _build_validation_report(self, chromosome) -> Dict[str, Any]:
        flagged = [g.id for g in chromosome.genes if getattr(g, "flag", False)]
        return {
            "is_valid": chromosome.fitness == 0 and not flagged,
            "total_conflicts": len(flagged),
            "conflicts_by_type": {
                "flagged_genes": flagged,
                "fitness_penalty": chromosome.fitness,
            },
        }
