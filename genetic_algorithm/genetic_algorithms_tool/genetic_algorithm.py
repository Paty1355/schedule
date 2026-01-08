import math
import random
import copy
from os.path import exists


from genetic_algorithm.genetic_algorithms_tool.algorithm_data_schema import *
from genetic_algorithm.genetic_algorithms_tool.algorithm_tools import *
from genetic_algorithm.genetic_algorithms_tool.fitness_tools import *
from genetic_algorithm.data_model.teacher import Teacher_unavailabities
from genetic_algorithm.data_model.group import GroupUnavailabilities

class GeneticAlgorithm:

    def __init__(self,course_assignments: Course_assignments,
                 rooms: Rooms,
                 teachers_unavailabities: Teacher_unavailabities,
                 groups_unavailabities: GroupUnavailabilities,
                 population_size: int = 100,
                 generations: int = 100,
                 mutation_rate: float = 0.05,
                 schedule_fitness_params: dict = None,
                 print_preference = True,
                 stop_function= None
                 ):
        self.course_assignments = course_assignments
        self.rooms = rooms
        self.teachers_unavailabities = teachers_unavailabities
        self.groups_unavailabities = groups_unavailabities
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.print_preference=print_preference
        self.genetic_tools = ScheduleTools()

        if schedule_fitness_params is None:
            schedule_fitness_params = {}
        self.schedule_fitness = ScheduleFitness(**schedule_fitness_params)
        self.genetic_tools = ScheduleTools()
        self.path_to_group={} #Twowrzy powiązanie pomiędzy group a parents_group
        self.unique_groups = {}
        self.stop_function = stop_function if stop_function is not None else self.get_stop_function()


    def get_stop_function(self):
        return 25 #Najmniejsza wartość wymagań obowiazkowych

    def create_population(self):
        population = []
        for i in range(self.population_size):
            chromosome_genes = self.genetic_tools.first_population_generator(self.course_assignments, self.rooms)
            #chromosome = self.create_chromosome(chromosome_genes) tak było i działało
            chromosome = self.create_chromosome(copy.deepcopy(chromosome_genes))
            population.append(chromosome)
        return population

    def create_chromosome(self, chromosome_genes):
        teacher_chromosome, group_chromosome, room_chromosome = Split_chromosome(chromosome_genes, self.unique_groups, self.path_to_group)
        return Chromosome(
            genes=chromosome_genes,
            teacher_chromosome=teacher_chromosome,
            group_chromosome=group_chromosome,
            room_chromosome=room_chromosome,
            fitness=0
        )

    def map_group(self): #Tworzy powiązanie groupy podrzędnej z rodzicem. W celu wykrywania kolizcji grupy 1/1 a wykładem dla całego semestru
        self.unique_groups = {i.group_id.id: i.group_id for i in self.course_assignments}
        self.path_to_group = {}

        for idx, idx_group in self.unique_groups.items():
            curr_group = idx_group
            parents = []
            while curr_group.parent_group_id is not None:
                parents.append(curr_group.parent_group_id)
                curr_group = self.unique_groups.get(curr_group.parent_group_id)
            self.path_to_group[idx] = parents

        return self.path_to_group


    def evaluate_fitness(self, population):
        for chromosome in population:
            # aktualizujemy teacher/group/room przed fitness
            t, g, r = Split_chromosome(chromosome.genes,self.unique_groups, self.path_to_group)
            chromosome.teacher_chromosome = t
            chromosome.group_chromosome = g
            chromosome.room_chromosome = r

            chromosome.fitness = self.schedule_fitness.calculate_fittnes(
                chromosome,
                self.teachers_unavailabities,
                self.groups_unavailabities
            )


    def select_parents(self, population, k=5):
        def tournament_selection(pop, k):
            competitors = random.sample(pop, k)
            return min(competitors, key=lambda c: c.fitness)

        def roulette_selection(pop):
            max_f = max(c.fitness for c in pop)
            weights = [(max_f - c.fitness + 1) for c in pop]
            return random.choices(pop, weights=weights, k=1)[0]

        if random.random() < 0.35:
            parent1 = tournament_selection(population, k)
            parent2 = tournament_selection(population, k)
        else:
            parent1 = roulette_selection(population)
            parent2 = roulette_selection(population)


        return parent1, parent2

    def select_genotype(self, gene_idx, population_list): #Jeżeli wybrany rodzić w danym genotypie (np. programowanie labolatorium) ma flagę - czyli zajęcia na siebie się nachodzą. To próbujemy zabrać taki bez flagi
        candidates = []

        for chromosome in population_list:
            gene = chromosome.genes[gene_idx-1]

            if not gene.flag:
                candidates.append(gene)
        if candidates:
            return random.choice(candidates).copy(deep=True)
        return None #Jeżeli wszystkie mają flagi to nic nie zwracamy

    def crossover(self, parent1, parent2, population_list):
        child1_genes = []
        child2_genes = []
        temp_i = 0

        for g1, g2 in zip(parent1.genes, parent2.genes):
            if(g1.flag == False and g2.flag == False):
                # if (g1.id != g2.id):
                #     print(f"G1 {g1.id} != {g2.id} /n"
                #           f"Problem---------------------------------------------------------------------------------------")
                #     print(f"{g1.course_assignment_id.course_id.name} i  {g2.course_assignment_id.course_id.name}")

                new_g1, new_g2 = self.genetic_tools.crossover_gene(
                    g1.copy(deep=True),
                    g2.copy(deep=True)
                )
                child1_genes.append(new_g1)
                child2_genes.append(new_g2)
            else:
                if(g1.flag == True or g2.flag == True): #Kiedy
                    res1 = self.select_genotype(g1.id, population_list)
                    g1=res1 if res1 is not None else g1
                    res2 = self.select_genotype(g2.id, population_list)
                    g2=res2 if res2 is not None else g2
                if(res1 is not None and res2 is not None):
                    new_g1, new_g2 = self.genetic_tools.crossover_gene(
                        g1.copy(deep=True),
                        g2.copy(deep=True)
                    )
                else:
                    new_g1 = self.genetic_tools.mutation_gene(g1.copy(deep=True))
                    new_g2 = self.genetic_tools.mutation_gene(g2.copy(deep=True))
                child1_genes.append(new_g1)
                child2_genes.append(new_g2)
        return self.create_chromosome(child1_genes), self.create_chromosome(child2_genes)

    def mutate(self, chromosome):
        child1_genes = []
        for g1 in chromosome.genes:
            if(np.random.random() < 0.15):
                new_g1 = self.genetic_tools.mutation_gene(g1.copy(deep=True), self.rooms)
                child1_genes.append(new_g1)
            else:
                child1_genes.append(g1.copy(deep=True))
        return self.create_chromosome(child1_genes)

    def run(self):
        population = self.create_population()
        self.map_group()
        self.evaluate_fitness(population)
        stagnation_count = 0
        best_fitness = math.inf
        last_best_fitness = math.inf
        valid_schedule_count = 0

        for generation in range(self.generations):
            if self.print_preference:
                print(f"\nGeneracja {generation + 1}/{self.generations}")

            elite = sorted(population, key=lambda c: c.fitness)[:5] #DO zachowania najlepszych elementów
            new_population = []

            while len(new_population) < self.population_size:
                parent1, parent2 = self.select_parents(population)
                if(random.random() < self.mutation_rate):
                    child1 = self.mutate(parent1)
                    child2 = self.mutate(parent2)
                else:
                    child1, child2 = self.crossover(parent1, parent2, population)
                # if(random.random() < self.mutation_rate): #Testowe dodanie nowcy osobników
                #     child1 = self.create_population(1)
                #     child2 = self.create_population(1)
                new_population.extend([child1, child2])

            print("Tworzenie nowej populacji")

            population = new_population[:self.population_size]

            print("Oliczanie fittnes nowej populacji")
            self.evaluate_fitness(population)
            population[-5:] = elite
            self.evaluate_fitness(population)
            last_best_fitness = best_fitness if best_fitness < last_best_fitness else last_best_fitness # Czy model robi postęp

            best_fitness = min(chromosome.fitness for chromosome in population)
            worst_fitness = max(chromosome.fitness for chromosome in population)
            print(f"Generation {generation + 1}: Best Fitness = {best_fitness} Worst Fittnes = {worst_fitness}")


            if(best_fitness < self.stop_function):
                if (best_fitness == 0):#Wynik = 0 Najelpsze rozwiazanie
                    return min(population, key=lambda c: c.fitness)
                valid_schedule_count+=1
                if(valid_schedule_count==7): #Wynik optymalny pod względem wymagan obowiazkowych
                    return min(population, key=lambda c: c.fitness)

            if (last_best_fitness <= best_fitness):
                stagnation_count += 1
                if (stagnation_count >= 14): #Tworenie nowej populacji - model nie uczy się
                    print("Uruchomiono generacje nowych osobników")
                    replace_count = max(1, int(self.population_size * 0.10)) #Ilość nowych osobników do wygenerowania
                    new_chromosome = self.create_population()[:replace_count]

                    indices_to_mutate = random.sample(range(len(population)), int(self.population_size *0.08)) #Ilość osobników do mutacji - w przypadku stagnacji

                    for id in indices_to_mutate:
                        population[id] = self.mutate(population[id])

                    population = sorted(population, key=lambda c: c.fitness)
                    population[-replace_count:] = new_chromosome
                    stagnation_count = 0

                    self.evaluate_fitness(population)

            else:
                stagnation_count = 0

        return min(population, key=lambda c: c.fitness)






