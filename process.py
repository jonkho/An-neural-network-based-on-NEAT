from net import *
from ga import *
import os

class Data(object):
	def __init__(self):
		self.prices = self.import_data()
		
	def get_frame(self, frame_number, frame_size):
		frame_start = frame_number
		frame_end = frame_number + frame_size
		result = []
		
		for (date, price) in self.prices[frame_start:frame_end]:
			result.append(price)
		
		return result
		
	def calculate_gain_loss(self, frame_number, frame_size, history_size):
		frame = self.get_frame(frame_number, frame_size)
		history_index = history_size - 1
		return float(frame[-1]) - float(frame[history_index])
	
	def import_data(self):
		APP_ROOT = os.path.realpath(os.path.dirname(__file__))
		DATAFILE_PATH = APP_ROOT+"/data.txt"
		days = open(DATAFILE_PATH).readlines()
		data = [day[:-2].split(',') for day in days]
		data.reverse()
		prices = [(record[0], record[4]) for record in data]
		prices = prices[:-1]
		return prices
		

class Process(object):
	'''
	Training the network to read 5 days of historical price data to predict
	whether 3 days later, the instrument will be higher priced.
	
	Training Strategy:
	We will train the network with 30 days of data. There will be 30 sets
	of 8-day frames and 30 predictions.  Fitness will be determined as the 
	net gain (in percentage points) for each frame. 
	
	Network topography:
	5 inputs and 1 output. 5 inputs corresponds to the 5-day historical 
	price, and the output is a binary decision whether to buy or not.
	10 hidden nodes will be used in a single layer.
	
	Genetic diversity:
	Have an initial population of 20 networks to breed
	'''

	
	def __init__(self, population_size):
		
		self.network_population = []
		self.average_fitness_history = []
		self.best_fitness_history = []
		self.generation = 0
		
		for i in range(population_size):
			# Set up the network population
			network = Network(number_of_inputs=5, number_of_outputs=1, number_of_hidden_layers=1, neurons_per_hidden_layer=10)
			network.create_net()
			self.network_population.append(network)
		
		# Set up gene pool
		self.genetic_algorithm = Genetic_Algorithm(population_size=population_size, mutation_rate=0.1, crossover_rate=0.7, number_of_weights=network.get_number_of_weights())
		
		# Insert the genes into the network population
		self.chromosomes = self.genetic_algorithm.get_chromosomes()	
		for i in range(population_size):
			self.network_population[i].put_weights(self.chromosomes[i].sequence)
		
		# Import the dataset
		self.data = Data()
		
		
	
	def update(self, frame_number):
		inputs = self.data.get_frame(frame_number=frame_number, frame_size=5)
		
		
		# evaluate each network in the population
		for (i, network) in enumerate(self.network_population):
			#print self.chromosomes[i].fitness
			output = network.update(inputs)

			# if output value > 0.5, then it's a buy signal, else it's an abstain.
			# check how good the outcome is and increment/decrement fitness accordingly
			if output[0] > 0.5:
				net_result = self.data.calculate_gain_loss(frame_number=frame_number, frame_size=8, history_size=5)
				if net_result > 0:
					print "chromosome %s with fitness %s has made a good decision to buy and net is at %s" % (i, self.chromosomes[i].fitness, net_result)
					self.chromosomes[i].fitness += net_result
				
				else:
					print "chromosome %s with fitness %s has made a poor decision to buy and net is at %s" % (i, self.chromosomes[i].fitness, net_result)
			
			# else: # if it abstained when it should have
			# 				net_result = self.data.calculate_gain_loss(frame_number=frame_number, frame_size=8, history_size=5)
			# 				if net_result < 0:
			# 					print "chromosome %s with fitness %s has made a good decision to abstain and net is at %s" % (i, self.chromosomes[i].fitness, net_result)
			# 					self.chromosomes[i].fitness -= net_result
			# 				
			# 				else:	
			# 					print "chromosome %s with fitness %s has made a poor decision to abstain and net is at %s" % (i, self.chromosomes[i].fitness, net_result)	
				
				print "new fitness is: %s" % self.chromosomes[i].fitness
			
		# calculate and track fitness scores	
		self.genetic_algorithm.calculate_fitness_scores()	
		self.average_fitness_history.append(self.genetic_algorithm.average_fitness)
		self.best_fitness_history.append(self.genetic_algorithm.best_fitness)
		
		self.generation = self.generation + 1
		self.chromosomes = self.genetic_algorithm.epoch(self.chromosomes)	
		
		for (i, network) in enumerate(self.network_population):
			network.put_weights(self.chromosomes[i].sequence)
			self.chromosomes[i].fitness = 0.0
		
		return True
			

		
		