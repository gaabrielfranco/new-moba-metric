# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 14:31:36 2018

@author: marcos
"""
import random
import copy
from operator import attrgetter

from six.moves import range


class GeneticAlgorithm(object):
    """Genetic Algorithm class.
    
    This is the main class that controls the functionality of the Genetic
    Algorithm.

    A simple example of usage:

    >>> # Select only two items from the list and maximise profit
    >>> from pyeasyga.pyeasyga import GeneticAlgorithm
    >>> input_data = [('pear', 50), ('apple', 35), ('banana', 40)]
    >>> easyga = GeneticAlgorithm(input_data)
    >>> def fitness (member, data):
    >>>     return sum([profit for (selected, (fruit, profit)) in
    >>>                 zip(member, data) if selected and
    >>>                 member.count(1) == 2])
    >>> easyga.fitness_function = fitness
    >>> easyga.run()
    >>> print easyga.best_individual()

    """

    def __init__(self,
                 seed_data,
                 population_size=50,
                 generations=100,
                 crossover_probability=0.8,
                 mutation_probability=0.2,
                 elitism=0.05,
                 maximise_fitness=True,
                 max_no_improv=20,
                 verbose=False,
                 min_crossover_probability=0.1,
                 diversification_factor=0.1,
                 tournament_percent=0.2,
                 diversification_step=10):
        """Instantiate the Genetic Algorithm.
        :param seed_data: input data to the Genetic Algorithm
        :type seed_data: list of objects
        :param int population_size: size of population
        :param int generations: number of generations to evolve
        :param float crossover_probability: probability of crossover operation
        :param float mutation_probability: probability of mutation operation
        """

        self.seed_data = seed_data
        self.population_size = population_size
        self.generations = generations
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.elitism = elitism
        self.maximise_fitness = maximise_fitness
        self.max_no_improv = max_no_improv
        self.verbose = verbose
        self.min_crossover_probability = min_crossover_probability
        self.diversification_factor = diversification_factor
        self.diversification_step = diversification_step
        self.tournament_percent = tournament_percent
        
        self.diversify_solutions = False
        self.elite = None
        self.elite_size = int(self.elitism * self.population_size)

        self.current_generation = []

        def create_individual(seed_data):
            """Create a candidate solution representation.
            e.g. for a bit array representation:
            >>> return [random.randint(0, 1) for _ in range(len(data))]
            :param seed_data: input data to the Genetic Algorithm
            :type seed_data: list of objects
            :returns: candidate solution representation as a list
            """
            return [random.randint(0, 1) for _ in range(len(seed_data))]

        def crossover(parent_1, parent_2):
            """Crossover (mate) two parents to produce two children.
            :param parent_1: candidate solution representation (list)
            :param parent_2: candidate solution representation (list)
            :returns: tuple containing two children
            """
            index = random.randrange(1, len(parent_1))
            child_1 = parent_1[:index] + parent_2[index:]
            child_2 = parent_2[:index] + parent_1[index:]
            return child_1, child_2

        def mutate(individual):
            """Reverse the bit of a random index in an individual."""
            mutate_index = random.randrange(len(individual))
            individual[mutate_index] = (0, 1)[individual[mutate_index] == 0]
            
        def diversification(individual):
            """ Strongly perturb an individual, choosing randomly one of the
            two methods."""
            for i in range(len(individual)):
                individual[i] = (0, 1)[individual[i] == 0]
            
            return individual

        def random_selection(population):
            """Select and return a random member of the population."""
            return random.choice(population)

        def tournament_selection(population):
            """Select a random number of individuals from the population and
            return the fittest member of them all.
            """
            if self.tournament_size == 0:
                self.tournament_size = 2
            members = random.sample(population, self.tournament_size)
            members.sort(
                key=attrgetter('fitness'), reverse=self.maximise_fitness)
            return members[0]

        self.fitness_function = None
        self.tournament_selection = tournament_selection
        self.tournament_size = int(self.tournament_percent * self.population_size)
        self.random_selection = random_selection
        self.create_individual = create_individual
        self.crossover_function = crossover
        self.mutate_function = mutate
        self.selection_function = self.tournament_selection
        self.diversification_function = diversification

    def check_elite(self, individual):
        if individual.hash not in [obj.hash for obj in self.elite]:
            if len(self.elite) < self.elite_size:
                self.elite.append(copy.deepcopy(individual))
                self.elite.sort(key=attrgetter('fitness'), reverse=True)
            else:
                lower_bound = min(self.elite, key=attrgetter('fitness')).fitness
                if individual.fitness > lower_bound:
                    self.elite.pop(len(self.elite)-1)
                    self.elite.append(copy.deepcopy(individual))
                    self.elite.sort(key=attrgetter('fitness'), reverse=True)
                    
    def create_initial_population(self):
        """Create members of the first population randomly.
        """
        self.elite = []
        initial_population = []
        for _ in range(self.population_size):
            genes = self.create_individual(self.seed_data)
            individual = Chromosome(genes)
            initial_population.append(individual)
            self.check_elite(individual)
        self.current_generation = initial_population

    def calculate_population_fitness(self):
        """Calculate the fitness of every member of the given population using
        the supplied fitness_function.
        """
        for individual in self.current_generation:
            individual.fitness = self.fitness_function(
                individual.genes, self.seed_data)
            self.check_elite(individual)

    def rank_population(self):
        """Sort the population by fitness according to the order defined by
        maximise_fitness.
        """
        self.current_generation.sort(
            key=attrgetter('fitness'), reverse=self.maximise_fitness)

    def create_new_population(self):
        """Create a new population using the genetic operators (selection,
        crossover, and mutation) supplied.
        """
        new_population = []
        selection = self.selection_function

        while len(new_population) < self.population_size:
            parent_1 = copy.deepcopy(selection(self.current_generation))
            parent_2 = copy.deepcopy(selection(self.current_generation))

            child_1, child_2 = parent_1, parent_2
            child_1.fitness, child_2.fitness = 0, 0

            can_crossover = random.random() < self.crossover_probability
            can_mutate = random.random() < self.mutation_probability

            if can_crossover:
                child_1.genes, child_2.genes = self.crossover_function(
                    parent_1.genes, parent_2.genes)

            if can_mutate:
                self.mutate_function(child_1.genes)
                self.mutate_function(child_2.genes)

            new_population.append(child_1)
            if len(new_population) < self.population_size:
                new_population.append(child_2)
            
        if self.diversify_solutions:
            n_diversification = int(self.diversification_factor * self.population_size)
            diversification_pool = random.sample(range(len(new_population)), n_diversification)
            for index in diversification_pool:
                new_population[index].genes = self.diversification_function(new_population[index].genes)
            self.diversify_solutions = False
            
        if self.elitism:
            for i in range(self.elite_size):
                new_population[i] = copy.deepcopy(self.elite[i])

        self.current_generation = new_population

    def create_first_generation(self):
        """Create the first population, calculate the population's fitness and
        rank the population by fitness according to the order specified.
        """
        self.create_initial_population()
        self.calculate_population_fitness()
        self.rank_population()

    def create_next_generation(self):
        """Create subsequent populations, calculate the population fitness and
        rank the population by fitness in the order specified.
        """
        self.create_new_population()
        self.calculate_population_fitness()
        self.rank_population()
        
    def print_generation(self):
        print('\tGeneration:')
        i = 0
        for individual in self.current_generation:
            evaluation = individual[0]
            solution = individual[1]
            att_sel = []
            for selected in solution:
                att_sel.append('%d' % selected)
            s = '%f;' % evaluation
            s += ';'.join(att_sel) + '\n'
            print('\t\t%d -> [%s]: evaluation: %f' % (i, s, evaluation))
        print()

    def run(self):
        """Run (solve) the Genetic Algorithm."""
        if self.verbose:
            gen_count = 1
            print('\tProcessing generation %d of %d...' %
                (gen_count, self.generations))
            gen_count += 1
            
        decay_step = int(self.max_no_improv / 2)
            
        self.create_first_generation()
        
        ### Generations without improvement
        count_no_improv = 0
        count_decay = 0
        best = self.current_generation[0]

        for _ in range(1, self.generations):
            if self.verbose:
                print('\tProcessing generation %4d of %4d...' %
                    (gen_count, self.generations), end=' ')
                gen_count += 1
                
            self.create_next_generation()
            
            candidate = self.current_generation[0]
            if (self.maximise_fitness and candidate.fitness > best.fitness) \
            or (not self.maximise_fitness and candidate.fitness <best.fitness):
                if self.verbose:
                    print(' Improvement from %f to %f.' % (best.fitness, candidate.fitness))
                count_no_improv = 0
                best = candidate
            else:
                if self.verbose:
                    print(' No improvement.')
                count_no_improv += 1
                
            count_decay += 1
                
            if count_decay == decay_step:
                self.crossover_probability = max(self.min_crossover_probability, self.crossover_probability-0.1)
                count_decay = 0
                
            if count_no_improv % int(self.generations // self.diversification_step) == 0:
                self.diversify_solutions = True
                
            if count_no_improv >= self.max_no_improv:
                return False
        
        return True

    def best_individual(self):
        """Return the individual with the best fitness in the current
        generation.
        """
        best = self.current_generation[0]
        return (best.fitness, best.genes)

    def last_generation(self):
        """Return members of the last generation as a generator function."""
        return ((member.fitness, member.genes) for member
                in self.current_generation)


class Chromosome(object):
    """ Chromosome class that encapsulates an individual's fitness and solution
    representation.
    """
    def __init__(self, genes):
        """Initialise the Chromosome."""
        self.genes = genes
        self.fitness = 0
        self.hash = ''.join([str(gene) for gene in self.genes])

    def __repr__(self):
        """Return initialised Chromosome representation in human readable form.
        """
        return repr((self.fitness, self.genes))
