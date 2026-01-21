"""
tests for genetic algorithm components and tools
"""
import pytest
from datetime import time
from genetic_algorithm.genetic_algorithms_tool.genetic_algorithm import GeneticAlgorithm
from genetic_algorithm.genetic_algorithms_tool.algorithm_tools import ScheduleTools
from genetic_algorithm.genetic_algorithms_tool.fitness_tools import ScheduleFitness
from genetic_algorithm.genetic_algorithms_tool.algorithm_data_schema import Gene, Chromosome, Split_chromosome
from genetic_algorithm.data_model.time_models import Weekdays, Week_parity
from genetic_algorithm.data_model.teacher import Teacher_unavailabities
from genetic_algorithm.data_model.group import GroupUnavailabilities


class TestScheduleTools:
    """tests for ScheduleTools class"""
    
    def test_schedule_tools_initialization(self):
        """test ScheduleTools initialization"""
        tools = ScheduleTools()
        assert tools.start_time_course_in_minute == 8 * 60
        assert tools.end_time_course_in_minute == 20 * 60
        assert len(tools.slots) > 0
        assert len(tools.weekdays_value) == 7
        assert len(tools.week_parity_value) == 3
    
    def test_time_slots_generator(self):
        """test time slot generation"""
        tools = ScheduleTools()
        time_slot = tools.time_slots_generator(2.0, 1)
        
        assert time_slot.id == 1
        assert isinstance(time_slot.start_time, time)
        assert isinstance(time_slot.end_time, time)
        assert time_slot.slot_order == 1
        
        # check that duration is correct (2 hours = 120 minutes)
        start_minutes = time_slot.start_time.hour * 60 + time_slot.start_time.minute
        end_minutes = time_slot.end_time.hour * 60 + time_slot.end_time.minute
        duration = end_minutes - start_minutes
        assert duration == 120
    
    def test_time_slots_generator_overflow_handling(self):
        """test that time slot generator handles overflow correctly"""
        tools = ScheduleTools()
        # try to create a very long time slot
        time_slot = tools.time_slots_generator(10.0, 1)
        
        # should not exceed 23:59
        assert time_slot.end_time.hour < 24
        assert time_slot.start_time.hour < 24
    
    def test_first_population_generator(
        self, sample_course_assignment, sample_rooms
    ):
        """test first population generator"""
        tools = ScheduleTools()
        course_assignments = [sample_course_assignment]
        
        genotype = tools.first_population_generator(course_assignments, sample_rooms)
        
        assert len(genotype) == len(course_assignments)
        assert all(isinstance(gene, Gene) for gene in genotype)
        assert all(gene.room_id in sample_rooms for gene in genotype)
        assert all(gene.weekday in Weekdays for gene in genotype)
    
    def test_crossover_gene(self, sample_gene, sample_course_assignment, sample_rooms, sample_time_slot):
        """test gene crossover changes at least one scheduling attribute"""
        tools = ScheduleTools()

        gene1 = Gene(
            id=1,
            course_assignment_id=sample_course_assignment,
            room_id=sample_rooms[0],
            weekday=Weekdays.monday,
            week_parity=Week_parity.odd,
            time_slot_id=sample_time_slot
        )

        gene2 = Gene(
            id=2,
            course_assignment_id=sample_course_assignment,
            room_id=sample_rooms[1],
            weekday=Weekdays.tuesday,
            week_parity=Week_parity.even,
            time_slot_id=sample_time_slot
        )

        before_gene1 = (gene1.room_id, gene1.weekday, gene1.week_parity, gene1.time_slot_id)
        before_gene2 = (gene2.room_id, gene2.weekday, gene2.week_parity, gene2.time_slot_id)

        new_gene1, new_gene2 = tools.crossover_gene(gene1, gene2)

        after_gene1 = (new_gene1.room_id, new_gene1.weekday, new_gene1.week_parity, new_gene1.time_slot_id)
        after_gene2 = (new_gene2.room_id, new_gene2.weekday, new_gene2.week_parity, new_gene2.time_slot_id)

        assert after_gene1 != before_gene1 or after_gene2 != before_gene2


class TestScheduleFitness:
    """tests for ScheduleFitness class"""
    
    def test_fitness_initialization_default(self):
        """test ScheduleFitness initialization with default values"""
        fitness = ScheduleFitness()
        
        assert fitness.teacher_overlaps_penalty == 35
        assert fitness.group_overlaps_penalty == 35
        assert fitness.room_capacity_penalty == 5
        assert fitness.room_type_mismatch_penalty == 35
    
    def test_fitness_initialization_custom(self):
        """test ScheduleFitness initialization with custom values"""
        fitness = ScheduleFitness(
            overlaps_penalty=50,
            room_capacity_penalty=30,
            teacher_gaps_penalty=0.5
        )
        
        assert fitness.teacher_overlaps_penalty == 50
        assert fitness.room_capacity_penalty == 30
        assert fitness.teacher_gaps_penalty == 0.5
    
    def test_fitness_negative_penalty_validation(self):
        """test that negative penalties raise ValueError"""
        with pytest.raises(ValueError):
            ScheduleFitness(overlaps_penalty=-10)
        
        with pytest.raises(ValueError):
            ScheduleFitness(teacher_gaps_penalty=-0.5)
    
    def test_fitness_none_required_penalty_validation(self):
        """test that None values for required penalties raise ValueError"""
        with pytest.raises(ValueError):
            ScheduleFitness(
                overlaps_penalty=35,
                unavailable_time_penalty=35,
                room_capacity_penalty=None
            )
    
    def test_fitness_inheritance(self):
        """test that specific penalties inherit from general ones"""
        fitness = ScheduleFitness(
            overlaps_penalty=40,
            unavailable_time_penalty=30
        )
        
        # teacher and group penalties should inherit
        assert fitness.teacher_overlaps_penalty == 40
        assert fitness.group_overlaps_penalty == 40
        assert fitness.teacher_unavailable_time_penalty == 30
        assert fitness.group_unavailable_time_penalty == 30
    
    def test_fitness_override_inheritance(self):
        """test that specific penalties can override general ones"""
        fitness = ScheduleFitness(
            overlaps_penalty=40,
            teacher_overlaps_penalty=50,
            group_overlaps_penalty=45
        )
        
        assert fitness.teacher_overlaps_penalty == 50
        assert fitness.group_overlaps_penalty == 45
        assert fitness.room_overlaps_penalty == 40


class TestGene:
    """tests for Gene model"""
    
    def test_create_valid_gene(self, sample_gene):
        """test creating a valid gene"""
        assert sample_gene.id == 1
        assert sample_gene.weekday == Weekdays.monday
        assert sample_gene.week_parity == Week_parity.both
        assert isinstance(sample_gene.room_id.capacity, int)
    
    def test_gene_properties(self, sample_gene):
        """test gene properties access"""
        assert sample_gene.course_assignment_id.course_id.name == "Podstawy programowania"
        assert sample_gene.room_id.code == "A101"
        assert sample_gene.time_slot_id.start_time == time(8, 0)


class TestChromosome:
    """tests for Chromosome model"""
    
    def test_create_chromosome(self, sample_gene):
        """test creating a chromosome"""
        genes = [sample_gene]
        chromosome = Chromosome(
            genes=genes,
            teacher_chromosome={},
            group_chromosome={},
            room_chromosome={},
            fitness=0
        )
        
        assert len(chromosome.genes) == 1
        assert chromosome.fitness == 0
        assert isinstance(chromosome.teacher_chromosome, dict)
        assert isinstance(chromosome.group_chromosome, dict)
        assert isinstance(chromosome.room_chromosome, dict)
    
    def test_chromosome_fitness_update(self, sample_gene):
        """test updating chromosome fitness"""
        genes = [sample_gene]
        chromosome = Chromosome(
            genes=genes,
            teacher_chromosome={},
            group_chromosome={},
            room_chromosome={},
            fitness=0
        )
        
        chromosome.fitness = 10.5
        assert chromosome.fitness == 10.5


class TestSplitChromosome:
    """tests for Split_chromosome function"""
    
    def test_split_chromosome_basic(self, sample_gene):
        """test basic chromosome splitting"""
        genes = [sample_gene]
        unique_groups = {sample_gene.course_assignment_id.group_id.id: sample_gene.course_assignment_id.group_id}
        path_to_group = {sample_gene.course_assignment_id.group_id.id: []}
        
        teacher_chr, group_chr, room_chr = Split_chromosome(genes, unique_groups, path_to_group)
        
        assert isinstance(teacher_chr, dict)
        assert isinstance(group_chr, dict)
        assert isinstance(room_chr, dict)


class TestGeneticAlgorithm:
    """tests for GeneticAlgorithm class"""
    
    def test_genetic_algorithm_initialization(
        self, sample_course_assignment, sample_rooms
    ):
        """test GeneticAlgorithm initialization"""
        course_assignments = [sample_course_assignment]
        teacher_unavail = []
        group_unavail = []
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=teacher_unavail,
            groups_unavailabities=group_unavail,
            population_size=50,
            generations=100,
            mutation_rate=0.05
        )
        
        assert ga.population_size == 50
        assert ga.generations == 100
        assert ga.mutation_rate == 0.05
        assert isinstance(ga.genetic_tools, ScheduleTools)
        assert isinstance(ga.schedule_fitness, ScheduleFitness)
    
    def test_genetic_algorithm_custom_fitness_params(
        self, sample_course_assignment, sample_rooms
    ):
        """test GeneticAlgorithm with custom fitness parameters"""
        course_assignments = [sample_course_assignment]
        fitness_params = {
            'overlaps_penalty': 50,
            'teacher_gaps_penalty': 0.3
        }
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[],
            schedule_fitness_params=fitness_params
        )
        
        assert ga.schedule_fitness.teacher_overlaps_penalty == 50
        assert ga.schedule_fitness.teacher_gaps_penalty == 0.3
    
    def test_create_population(self, sample_course_assignment, sample_rooms):
        """test population creation"""
        course_assignments = [sample_course_assignment]
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[],
            population_size=10
        )
        
        ga.map_group()
        population = ga.create_population()
        
        assert len(population) == 10
        assert all(isinstance(chromosome, Chromosome) for chromosome in population)
        assert all(len(chromosome.genes) == len(course_assignments) for chromosome in population)
    
    def test_create_chromosome(self, sample_course_assignment, sample_rooms, sample_gene):
        """test chromosome creation"""
        course_assignments = [sample_course_assignment]
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[]
        )
        
        ga.map_group()
        genes = [sample_gene]
        chromosome = ga.create_chromosome(genes)
        
        assert isinstance(chromosome, Chromosome)
        assert len(chromosome.genes) == len(genes)
        assert chromosome.fitness == 0
    
    def test_evaluate_fitness(self, sample_course_assignment, sample_rooms):
        """test fitness evaluation"""
        course_assignments = [sample_course_assignment]
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[]
        )
        
        ga.map_group()
        population = ga.create_population()
        
        # initial fitness should be 0
        assert all(chromosome.fitness == 0 for chromosome in population)
        
        # after evaluation, fitness should be calculated
        ga.evaluate_fitness(population)
        
        #  fitness should be non-negative numbers
        assert all(chromosome.fitness >= 0 for chromosome in population)
    
    def test_get_stop_function(self, sample_course_assignment, sample_rooms):
        """test stop function"""
        course_assignments = [sample_course_assignment]
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[]
        )
        
        stop_value = ga.get_stop_function()
        assert stop_value == 25
    
    def test_custom_stop_function(self, sample_course_assignment, sample_rooms):
        """test custom stop function"""
        course_assignments = [sample_course_assignment]
        custom_stop = 15
        
        ga = GeneticAlgorithm(
            course_assignments=course_assignments,
            rooms=sample_rooms,
            teachers_unavailabities=[],
            groups_unavailabities=[],
            stop_function=custom_stop
        )
        
        assert ga.stop_function == custom_stop


class TestScheduleToolsEdgeCases:
    """edge case tests for ScheduleTools"""
    
    def test_time_slot_minimum_duration(self):
        """test creating time slot with minimum duration"""
        tools = ScheduleTools()
        time_slot = tools.time_slots_generator(0.25, 1)  # 15 minutes
        
        assert isinstance(time_slot.start_time, time)
        assert isinstance(time_slot.end_time, time)
    
    def test_time_slot_maximum_duration(self):
        """test creating time slot with maximum feasible duration"""
        tools = ScheduleTools()
        time_slot = tools.time_slots_generator(8.0, 1)  # 8 hours
        
        # should handle long durations
        assert time_slot.end_time.hour <= 23
        assert time_slot.end_time.minute <= 59