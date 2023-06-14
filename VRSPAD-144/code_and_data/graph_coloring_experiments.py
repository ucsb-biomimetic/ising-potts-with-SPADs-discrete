#different tasks to run: run different tasks based on cmd line input
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--potts_cal', action='store_true') #scans weight param to find optimal potts weight
parser.add_argument('--cpuSA_cal', action='store_true') #scan thru temperature in cpu implementation of simulated annealing
parser.add_argument('--ising_cal', action='store_true') #scans ising parameters
parser.add_argument('--dist_graph', action='store_true') #using fixed parameters, measures statistics of ising and potts solutions
parser.add_argument('--soln_graph', action='store_true') #plots an instance of a solved graph
parser.add_argument('--weights_vis', action='store_true') #plots time to solution vs problem size
parser.add_argument('--ntrials', type=int) #applies to any/all of the tasks

args = parser.parse_args()

ntrials = args.ntrials

import numpy
from matplotlib import pyplot as plt
import matplotlib
import time
import networkx as nx
from labellines import labelLines
import pickle
import ColoringRefs
import VRSPADmodel
import spi_ftdi_hw_control as hw_ctrl
import graph_coloring_plots as gcp

#===============================================================================================================
#set up various aspects of the problem parameters:
#nodes and connectivity
nnodes=48
p = 4.5/nnodes #probability of an edge is chosen so that graphs are around the 3-colorability phase transition
print("edge probability: ", p)

hw_ctrl.FTDI_init()

#analog operating coditions
spad_bias = 30.0
spad_illumination = 500e-6
window_range = 0.6
window_offset = 0.07

# ising and potts models.  The potts model is used more than the ising, since graph coloring is inherently potts - 
# for instance, even when the HW is set up as an ising model, we read it as though it were configured as a potts model.
coloring_ising = VRSPADmodel.VRSPADmodel(nnodes*3*[1])
coloring_potts = VRSPADmodel.VRSPADmodel(nnodes*[3])

minbias, maxbias = coloring_potts.set_calibration(spad_bias, spad_illumination, window_range, window_offset, 10)
print("Potts calibration bias range: %i-%i"%(minbias, maxbias))
minbias, maxbias = coloring_ising.set_calibration(spad_bias, spad_illumination, window_range, window_offset, 50)
print("Ising calibration bias range: %i-%i"%(minbias, maxbias))

def potts_run(G, tmax, w):
	#given a graph G, sets up a potts model with weights w and searches for a solution for tmax seconds
	#set up weights:
	#analog operating coditions

	# minbias, maxbias = coloring_potts.set_calibration(spad_bias, spad_illumination, window_range, window_offset, 10)
	coloring_potts.set_analog_parameters(spad_bias, spad_illumination, window_range, window_offset)

	coloring_potts.weight_matrix = coloring_potts.weight_matrix*0 #reset each time, since we reuse the object
	for i in range(nnodes):
		for j in range(i+1, nnodes):
			if G.has_edge(i,j):
				#if they are connected, there is an energy penalty for being in the same state:
				for k in range(3):
					coloring_potts.set_weight(w, i, k, j, k)

	#execute model:

	hw_ctrl.set_cycle_properties(100, 80) #start by disabling boltzmann machine
	coloring_potts.write_weights() #weights and biases etc have all been specified already
	hw_ctrl.reset_low_energy_checker()

	tstart = time.perf_counter()
	hw_ctrl.set_cycle_properties(60, 80) #calculation enabled here

	telapsed = tmax + 1 #default if solution is not actually found
	while(time.perf_counter() - tmax < tstart):
		if hw_ctrl.read_lowest_energy() == 0: #the way the weights are set up, we know that a found solution equals zero energy
			tdone = time.perf_counter()
			telapsed = tdone-tstart
			#check that the Potts state is actually valid - otherwise reset low energy checker and keep going:
			if coloring_potts.is_valid_state(mode = "lowest energy"):
				break
			hw_ctrl.reset_low_energy_checker() #reset low energy
			telapsed = tmax + 1 #set timer result back to default value

	return (telapsed, hw_ctrl.read_lowest_energy())

def cpuSA_run(G, tmax, temp):
	nnodes = G.number_of_nodes()
	edges = numpy.zeros([nnodes, nnodes], dtype=numpy.int32)
	coloring = numpy.zeros([nnodes], dtype=numpy.int32)

	for j in range(nnodes):
		for k in range(nnodes):
			if G.has_edge(j, k):
				edges[j,k] = 1
			else:
				edges[j,k] = 0

	#get a sense of the time on this computer by doing a small run:
	cal_iters = 100000 #should be large enough to get an accurate measurement, but not so large that it takes a lot of time
	tstart = time.perf_counter()
	ColoringRefs.annealing_sampling(2, cal_iters, temp, edges, coloring) #won't work with 2 colors, will just run for cal_iters
	cal_time = time.perf_counter() - tstart
	cal_factor = tmax/cal_time

	tstart = time.perf_counter()
	ColoringRefs.annealing_sampling(3, int(cal_iters*cal_factor), temp, edges, coloring)
	if coloring[0] == -1: #coloring failed
		return tmax+1
	else: #coloring succeeded
		return (time.perf_counter() - tstart)

def dsatur_run(G):
	d = nx.coloring.greedy_color(G, strategy='DSATUR')
	# print(d)
	colorable = True
	for node in d:
		# print(node)
		# print(d[node])
		if d[node] > 2:
			colorable = False

	#pretend solution times, so that plotting methodology is the same
	if colorable:
		return 0
	else:
		return 2

def nonredundant_search(G):
	edges = numpy.zeros([nnodes, nnodes], dtype=numpy.int32)
	coloring = numpy.zeros([nnodes], dtype=numpy.int32)
	for j in range(nnodes):
		for k in range(nnodes):
			if G.has_edge(j, k):
				edges[j,k] = 1
			else:
				edges[j,k] = 0

	ColoringRefs.nonredundant_search(3, edges, coloring)
	#under construction #

def ising_run(G, tmax, w, inhib, bias):
	#given a graph G, use an ising model to search for 3-colorings for tmax seconds.
	#the ising model is set up using w weights, i inhibition within each node, and b biases on each ising bit.
	#set up weights: (ising)
	#very similar to potts, except must add inhibitory connections

	minbias, maxbias = coloring_ising.set_calibration(spad_bias, spad_illumination, window_range, window_offset, -bias)
	coloring_ising.set_analog_parameters(spad_bias, spad_illumination, window_range, window_offset)

	coloring_ising.weight_matrix = coloring_ising.weight_matrix*0
	coloring_ising.biases = coloring_ising.biases*0
	for i in range(nnodes):
		for j in range(i+1, nnodes):
			if G.has_edge(i,j):
				#if they are connected, there is an energy penalty for being in the same state:
				for k in range(3):
					coloring_ising.set_weight(w, i*3+k, 0, j*3+k, 0)

	#per-node inhibitory connections:
	for i in range(nnodes):
		coloring_ising.set_weight(inhib, i*3+0, 0, i*3+1, 0)
		coloring_ising.set_weight(inhib, i*3+0, 0, i*3+2, 0)
		coloring_ising.set_weight(inhib, i*3+1, 0, i*3+2, 0)

	#negative biases, to drive nodes towards 1 state (otherwise, all-zeros would be a low-energy solution)
	for i in range(nnodes*3):
		coloring_ising.set_bias(bias, i, 0)

	#also recalibrate offsets so that full negative bias is within the full range of the DACs (note -bias):
	coloring_ising.set_calibration(spad_bias, spad_illumination, window_range, window_offset, -bias+10)

	#execute model:

	hw_ctrl.set_cycle_properties(100, 80) #start by disabling boltzmann machine

	coloring_ising.write_weights() #weights and biases etc have all been specified already
	hw_ctrl.reset_low_energy_checker()

	tstart = time.perf_counter()
	hw_ctrl.set_cycle_properties(60, 80) #calculation enabled here

	e_target = G.number_of_nodes()*bias
	# print("Expected ising ground state energy: ", e_target)

	#search for tmax seconds maximum:
	telapsed = tmax + 1 #default if solution is not actually found
	while(time.perf_counter() - tmax < tstart):
		if hw_ctrl.read_lowest_energy() == e_target: #the way the weights are set up, we know that a found solution equals zero energy
			tdone = time.perf_counter()
			telapsed = tdone-tstart
			break

	return (telapsed, hw_ctrl.read_lowest_energy())

def potts_cal():
	w_opts = [20, 25, 30, 35, 40]
	success_rates = []
	tmax = 0.05

	nnodes=48
	p = 4.5/nnodes #probability of an edge is chosen so that graphs are around the 3-colorability phase transition
	print("edge probability: ", p)

	#create set of graphs first, so that the same set of graphs is used for all of the different conditions
	Graphs = [nx.erdos_renyi_graph(nnodes, p) for trial in range(ntrials)]

	for w in w_opts:
		nsuccess = 0
		for trial in range(ntrials):
			G = Graphs[trial]
			tts, energy = potts_run(G, tmax, w)
			if tts < tmax:
				nsuccess = nsuccess + 1
			#print progress info:
			print("Potts_cal: w=%i, Trial %i, tts/energy: %.4f, %.4f"%(w, trial, tts, energy), end="\r")

		success_rates.append(nsuccess/ntrials)

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/potts_cal_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.potts_cal() #plot the data that was just collected

def cpuSA_cal():
	temp_opts = [0.1, 0.125, 0.15, 0.175, 0.2]
	success_rates = []
	tmax = 0.05

	nnodes=48
	p = 4.5/nnodes #probability of an edge is chosen so that graphs are around the 3-colorability phase transition
	print("edge probability: ", p)

	#create set of graphs first, so that the same set of graphs is used for all of the different conditions
	Graphs = [nx.erdos_renyi_graph(nnodes, p) for trial in range(ntrials)]

	for temp in temp_opts:
		nsuccess = 0
		for trial in range(ntrials):
			G = Graphs[trial]
			tts = cpuSA_run(G, tmax, temp)
			if tts < tmax:
				nsuccess = nsuccess + 1
			#print progress info:
			print("cpuSA_cal: temp=%.2f, Trial %i, tts: %.4f"%(temp, trial, tts), end="\r")

		success_rates.append(nsuccess/ntrials)

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/cpuSA_cal_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.cpuSA_cal() #plot the data that was just collected

def ising_cal():
	#ising calibration routine. Use iteratively to save time. ==============================================================
	nnodes=48
	p = 4.5/nnodes #probability of an edge is chosen so that graphs are around the 3-colorability phase transition
	print("edge probability: ", p)

	w_opts = [65, 75, 85, 95, 105, 115, 125]
	inhib_opts = [75, 85, 95, 105, 115, 125]
	bias_opts = [-35, -40, -45, -50, -55, -60, -65,]
	success_rates = []
	bar_labels = []
	tmax = 0.05

	#create set of graphs first, so that the same set of graphs is used for all of the different conditions
	Graphs = [nx.erdos_renyi_graph(nnodes, p) for trial in range(ntrials)]
	# solvable = [True if cpuSA_run(G) < 1 else False for G in Graphs] #only use graphs that are readily solvable, otherwise this takes forever to run
	#unroll into loop so we can have a progress indicator, since this step can take a while on its own
	solvable = []
	for i, G in enumerate(Graphs):
		print("checking graph %i for solvability..."%i, end='\r')
		if cpuSA_run(G) < 1:
			solvable.append(True)
		else:
			solvable.append(False)

	for w in w_opts:
		for inhib in inhib_opts:
			for bias in bias_opts:
				nsuccess = 0
				for trial in range(ntrials):
					if not solvable[trial]:
						continue #don't waste time on un-solvable graphs
					G = Graphs[trial]
					tts, energy = ising_run(G, tmax, w, inhib, bias)
					if tts < tmax:
						nsuccess = nsuccess + 1
					#print progress info:
					print("Ising_cal: w=%i, inhib=%i, bias=%i, Trial %i, tts/energy: %.4f, %.4f"
						%(w, inhib, bias, trial, tts, energy), end="\r")

				success_rates.append(nsuccess/ntrials)
				bar_labels.append("%i\n%i\n%i"%(w, inhib, bias))

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/ising_cal_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.ising_cal() #plot the data that was just collected

def dist_graph():
	#best-case ising and potts tts-distribtion for various n (paper plot) ===============================================
	t_cpu = 0.15
	w_potts = 35
	w_ising = 95
	inhib = 105
	bias = -45
	tmax = 1.

	nnodes = 48
	p = 4.5/nnodes
	print("Edge probability for %i nodes: %.4f"%(nnodes, p))
	potts_times = []
	ising_times = []
	cpuSA_times = []
	dsatur_times = []
	for trial in range(ntrials):
		G = nx.erdos_renyi_graph(nnodes, p) #use the same graph for both models
		potts_tts, potts_energy = potts_run(G, tmax, w_potts)
		ising_tts, ising_energy = ising_run(G, tmax, w_ising, inhib, bias)
		cpuSA_tts = cpuSA_run(G, tmax, t_cpu)
		potts_times.append(potts_tts)
		ising_times.append(ising_tts)
		cpuSA_times.append(cpuSA_tts)
		dsatur_times.append(dsatur_run(G))
		print("Trial %i, tts/energy, Potts: %.4f/%.4f,  Ising: %.4f/%.4f, cpuSA: %.4f/-"
						%(trial, potts_tts, potts_energy, ising_tts, ising_energy, cpuSA_tts), end="\r")

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/dist_graph_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.dist_graph() #plot the data that was just collected

#do a single run and plot the solved graph ========================================================================
def soln_graph():
	
	nnodes = 48 #do max size
	p = 4.5/nnodes
	tmax = 1
	w_potts = 50
	print("Edge probability for %i nodes: %.4f"%(nnodes, p))
	for trial in range(ntrials): #try to get a solved instance, trying up to ntrial times
		G = nx.erdos_renyi_graph(nnodes, p)
		potts_tts, potts_energy = potts_run(G, tmax, w_potts)
		if potts_energy == 0:
			coloring = coloring_potts.sample_state(mode = "lowest energy")
			break

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/graph_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.soln_graph() #plot the data that was just collected

def weight_vis():

	w_ising = 85
	inhib = 110
	bias = -50
	tmax = 1.
	nnodes = 48
	p = 4.5/nnodes

	G = nx.erdos_renyi_graph(nnodes, p) #use the same graph for both models
	ising_tts, ising_energy = ising_run(G, tmax, w_ising, inhib, bias)

	#copy coloring_ising into a local var:
	ising_coloring_model = coloring_ising

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/coloring_weight_vis.pkl", 'wb') as f:
		pickle.dump(data2save, f)
	gcp.weights_vis() #plot the data that was just collected


#run one or more of the experiments:
if args.potts_cal:
	potts_cal()
if args.cpuSA_cal:
	cpuSA_cal()
if args.ising_cal:
	ising_cal()
if args.dist_graph:
	dist_graph()
if args.soln_graph:
	soln_graph()
if args.weights_vis:
	weight_vis()