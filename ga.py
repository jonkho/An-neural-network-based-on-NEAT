import random
import copy

class Genome(object):
	def __init__(self, genome=None, fitness=0.00):
		if genome == None:
			self.sequence = []
		
		else:
			self.sequence = genome
			
		self.fitness = fitness
		
		
class Genetic_Algorithm(object):
	def __init__(self, population_size, mutation_rate, crossover_rate, number_of_weights):
		self.population_size = population_size
		self.mutation_rate = mutation_rate
		self.crossover_rate = crossover_rate
		self.chromosome_length = number_of_weights
		self.total_fitness = 0.0
		self.generation = 0
		self.fittest_genome = 0
		self.best_fitness = 0.0
		self.worst_fitness = 9999999
		self.average_fitness = 0.0
		self.max_perturbation = 0.3
		self.population = []
		
		for i in range(self.population_size):
			genome = Genome()
			
			for j in range(self.chromosome_length):
				genome.sequence.append(random.uniform(-1,1))
			
			self.population.append(genome)
		
				
	def mutate(self, chromosome):
		for (i, gene) in enumerate(chromosome.sequence):
			if random.uniform(0,1) < self.mutation_rate:
				gene = gene + (random.uniform(-1,1) * self.max_perturbation)
				chromosome.sequence[i] = gene
		
		return chromosome
				
	
	def get_chromosome_from_roulette(self):
		a_slice = random.uniform(0,1) * self.total_fitness
		fitness_so_far = 0.0
		
		for member in self.population:
			fitness_so_far = fitness_so_far + member.fitness
			
			if fitness_so_far >= a_slice:
				return copy.deepcopy(member)
				
		raise RuntimeError
		
	
	def crossover(self, mother, father):
		if random.uniform(0,1) > self.crossover_rate:
			#print "not crossing over due to crossover rate"
			return mother, father
			
		if mother == father:
			#print "mother == father"
			return mother, father	
		
		#print "crossing over"	
		crossover_point = random.randint(0, self.chromosome_length - 1) 
		child1 = mother.sequence[0:crossover_point] + father.sequence[crossover_point:]
		child2 = father.sequence[0:crossover_point] + mother.sequence[crossover_point:]
		
		return Genome(child1), Genome(child2)
			
	
	def grab_n_best(self, n_best, number_of_copies):
		population = []
		
		for i in range(n_best, -1, -1):
			for j in range(number_of_copies):
				index = self.population_size - 1 - i
				population.append(self.population[index])
		
		return population
		
		
	def calculate_fitness_scores(self):
		self.total_fitness = 0.0
		
		highest_so_far = 0.0
		lowest_so_far = 9999999
		
		for (i, genome) in enumerate(self.population):
			if genome.fitness > highest_so_far:
				highest_so_far = self.best_fitness = genome.fitness 
				self.fittest_genome = i
				
			if genome.fitness < lowest_so_far:
				lowest_so_far = self.worst_fitness = genome.fitness

			#print genome.fitness
			self.total_fitness += genome.fitness
		
		self.average_fitness = float(self.total_fitness / self.population_size)

	
	def epoch(self, old_population):
		self.population = old_population
		self.reset()
		self.population = sorted(self.population, key=lambda genome: genome.fitness)
		self.calculate_fitness_scores()

		new_population = self.grab_n_best(n_best=15, number_of_copies=1)
		
		while (len(new_population) < self.population_size):
			mother = self.get_chromosome_from_roulette()
			father = self.get_chromosome_from_roulette()
			
			offspring1, offspring2 = self.crossover(mother, father)
		
			offspring1 = self.mutate(offspring1)
			offspring2 = self.mutate(offspring2)
			
			new_population.append(offspring1)
			new_population.append(offspring2)
		
		self.population = new_population
		
		return self.population
		
	
	def reset(self):
		self.total_fitness = 0.0
		self.best_fitness = 0.0
		self.worst_fitness = 9999999
		self.average_fitness = 0.0
		
		
	def get_chromosomes(self):
		return self.population		
				
	def randomize_fitness(self):
		for member in self.population:
			member.fitness = random.uniform(0,1000)
		