import numpy
from matplotlib import pyplot as plt
import matplotlib
import time
import math
import argparse
import pickle
import VRSPADmodel
import spi_ftdi_hw_control as hw_ctrl

#specify fonts here, for use with all plotting functions
font = {'size': 9, 'fontname': 'Century Gothic'}
ticks_font = matplotlib.font_manager.FontProperties(family=font['fontname'], style='normal', size=9, weight='normal', stretch='normal')

def get_data(fname):
	#load data into namespace n
	with open(fname, 'rb') as f:
		data_dict = pickle.load(f)
	n = argparse.Namespace(**data_dict)
	return n

def potts_tsp_trial():
	hw_ctrl.FTDI_init()

	#generate random cities in 1x1 square: standard euclidean distances
	ncities = 13

	#define this stuff here so that it exists whether or not we are plotting from file
	anneal_reps = 1
	anneal_steps = 30
	anneal_time = 1.*anneal_reps

	linear_anneal = numpy.linspace(32.0, 30.0, anneal_steps)
	anneal_steps = anneal_steps*anneal_reps
	linear_anneal = numpy.concatenate(anneal_reps*[linear_anneal])
	anneal_schedule = numpy.linspace(0, anneal_time, anneal_steps)

	sx = numpy.random.random([ncities])
	sy = numpy.random.random([ncities])

	distances = numpy.zeros([ncities, ncities])
	for i in range(ncities):
		for j in range(ncities):
			distances[i,j] = ((sx[i]-sx[j])**2 + (sy[i]-sy[j])**2)**0.5
			# distances[i,j] = i
			if i==j:
				distances[i,j] = 1

	#scale distances to better map onto hardware:
	distances = distances*85

	#set inhibition to scale with distance values:
	inhib = 120#50.*numpy.min(distances)
	print('Inhibitory weights have value: %i'%inhib)

	tsp_potts = VRSPADmodel.VRSPADmodel((ncities-1)*[ncities-1])

	#===========================================================================================================
	#set up weights: (potts)

	for city_index in range(0,ncities-1):
		#for first and last columns, the connecting city (#13, index 12) is fixed, so weights become biases.
		tsp_potts.set_bias(min(2*distances[city_index, ncities-1], 127), 0, city_index) #first column
		tsp_potts.set_bias(min(2*distances[city_index, ncities-1], 127), ncities-2, city_index) #last column

	for city_order in range(0,ncities-2):
		#for all internal pairs of columns, weights need to be added.
		# This is ncities-2 pairs. For each pair, a full matrix of distances is needed
		for city_index0 in range(0, ncities-1):
			for city_index1 in range(0, ncities-1):
				tsp_potts.set_weight(distances[city_index0, city_index1], city_order, city_index0, city_order+1, city_index1)

	#finally, inhibitory connections to enforce mutual exclusion must be included.
	for city_index in range(0, ncities-1):
		#across each index (row), inhibitory connections must be made so that each city is only visited once
		for city_order0 in range(0,ncities-1):
			for city_order1 in range(0,ncities-1):
				if city_order0 == city_order1:
					tsp_potts.set_weight(0, city_order0, city_index, city_order1, city_index)
				else:
					tsp_potts.set_weight(inhib, city_order0, city_index, city_order1, city_index)


	#=======================================================================================================
	#set up hardware:

	spad_bias = 30.
	spad_illumination = 200e-6
	window_range = 0.5
	window_offset = 0.07

	minbias, maxbias = tsp_potts.set_calibration(spad_bias, spad_illumination, window_range, window_offset, 10)
	print("Calibration bias range: %i-%i"%(minbias, maxbias))
	print("temperature: %.1f"%numpy.median(tsp_potts.temps))

	tsp_potts.set_analog_parameters(spad_bias, spad_illumination, window_range, window_offset)

	tsp_potts.write_weights() #weights and biases etc have all been specified already
	#=======================================================================================================

	#record BM energies and the time they were measured.
	#there are two sets: one for direct BM states (path)
	#and one that records from the hardware's low energy checker (minpath)
	path_energies = []
	path_proposals = []
	path_times = []

	minpath_energies = []
	minpath_proposals = []
	minpath_times = []

	hw_ctrl.reset_low_energy_checker()

	tstart = time.perf_counter()

	for i, bias in enumerate(linear_anneal):

		hw_ctrl.set_SPAD_bias(bias) #effectively, temperature control
		while (time.perf_counter()-tstart < (i+1)*(anneal_time/anneal_steps)):
			path_proposal = tsp_potts.sample_state()
			path_proposal.append(12)
			path_proposals.append(path_proposal)
			path_energies.append(hw_ctrl.read_current_energy())
			path_times.append(time.perf_counter()-tstart)
		#record from the low energy checker, once per temperature step:
		minpath_proposal = tsp_potts.sample_state(mode = "lowest energy")
		minpath_proposal.append(12)
		minpath_proposals.append(minpath_proposal)
		minpath_energies.append(hw_ctrl.read_lowest_energy())
		minpath_times.append(time.perf_counter()-tstart)

	data2save = locals() #can't pickle f, so have to do this before opening file:
	with open("results/tsp_data.pkl", 'wb') as f:
		pickle.dump(data2save, f)

def tsp_annealing_graph():
	n = get_data("results/tsp_data.pkl")
	#processing and plotting results ==================================================================

	def is_valid_state(path_proposal):
		return (numpy.unique(path_proposal).shape[0] == n.ncities)

	path_valid = [is_valid_state(pp) for pp in n.path_proposals]
	path_color = ['tab:blue' if valid else 'tab:orange' for valid in path_valid]
	minpath_valid = [is_valid_state(pp) for pp in n.minpath_proposals]
	minpath_color = ['tab:blue' if valid else 'tab:orange' for valid in minpath_valid]

	plt.figure(figsize=(4.3,2.5))

	#first plot energy points on main axis:
	ax1 = plt.gca()
	ax2 = ax1.twinx()

	invalid_path_times = [n.path_times[i] for i in range(len(n.path_times)) if not is_valid_state(n.path_proposals[i])]
	invalid_path_energies = [n.path_energies[i] for i in range(len(n.path_times)) if not is_valid_state(n.path_proposals[i])]
	art1 = ax1.scatter(invalid_path_times, invalid_path_energies, c = 'lightskyblue', s=4, label='samples - invalid')

	valid_path_times = [n.path_times[i] for i in range(len(n.path_times)) if is_valid_state(n.path_proposals[i])]
	valid_path_energies = [n.path_energies[i] for i in range(len(n.path_times)) if is_valid_state(n.path_proposals[i])]
	art2 = ax1.scatter(valid_path_times, valid_path_energies, c = 'limegreen', s=4, label='samples - constraints met')

	#plot the minpaths as a bunch of individual colored line segments:
	art3, = ax1.plot(n.minpath_times, n.minpath_energies, color='tab:purple', label='best-to-date')

	#plot the annealing schedule on the second y axis:
	art4, = ax2.plot(n.anneal_schedule, n.linear_anneal, color = 'black', label='SPAD bias')


	ax1.set_ylabel("energy, FPGA units", fontdict=font)
	ax2.set_ylabel("SPAD bias, V", fontdict=font)
	ax1.set_xlabel("annealing time, seconds", fontdict=font)

	ax1.spines[['top']].set_visible(False)
	ax2.spines[['top']].set_visible(False)

	#set tick mark lengths to zero:
	ax1.tick_params(axis='both', which='both',length=0)
	ax2.tick_params(axis='both', which='both',length=0)

	ax1.legend(handles=[art1, art2, art3, art4], loc='upper right', prop=ticks_font, markerscale=2, edgecolor='white', framealpha=1)

	#scale second y axis to put temp curve in right place:
	ax2.set_ylim([29, 36])
	ax2.set_yticks([30, 31, 32])

	#set font of ticks numbers. Very annoying to have to do it like this
	for ax in [ax1, ax2]:
		for label in ax.get_xticklabels() :
		    label.set_fontproperties(ticks_font)
		for label in ax.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.tight_layout()
	plt.savefig("results/tsp_annealing.eps")
	plt.savefig("results/tsp_annealing.png")
	plt.show()

def tsp_soln_graph():
	n = get_data("results/tsp_data.pkl")

	#graph min path proposal:
	min_route = n.minpath_proposals[-1]
	# print(minpath_proposals[-1])
	# print(minpath_valid[-1])
	plt.figure(figsize=(2.8,2.8))
	plt.scatter(n.sx, n.sy, c = "black")
	for i in range(n.ncities):
		plt.plot([n.sx[min_route[i]], n.sx[min_route[(i+1)%n.ncities]]], [n.sy[min_route[i]], n.sy[min_route[(i+1)%n.ncities]]], color='black')
	plt.axis('off')

	plt.tight_layout()
	plt.savefig("results/tsp_solution.eps")
	plt.savefig("results/tsp_solution.png")
	plt.show()

def tsp_weights_graph():
	n = get_data("results/tsp_data.pkl")

	weights = n.tsp_potts.weight_matrix
	#make masked, so that white squares are not written to the figure file (but only works with pcolor, not pcolormesh)
	weights = numpy.ma.masked_equal(weights, 0)

	plt.figure(figsize=(5,5))
	nckts = 144
	pcolor_spacing = numpy.linspace(-0.5, nckts-0.5, nckts+1)
	plt.pcolor(pcolor_spacing, pcolor_spacing, -weights, shading='flat', cmap='gray')
	plt.ylim([nckts-0.5, -0.5])
	plt.xlim([-0.5, nckts-0.5])
	plt.ylabel("VRSPAD index (physical hardware)", fontdict=font)
	plt.xlabel("VRSPAD index (physical hardware)", fontdict=font)
	
	#add grid lines to mark between semantic meanings:
	for i in range(1,12):
		plt.plot([nckts-0.5, -0.5], 2*[i*12-0.5], c='skyblue', lw=0.5)
		plt.plot(2*[i*12-0.5], [nckts-0.5, -0.5], c='skyblue', lw=0.5)

	ax = plt.gca()

	ax_top = ax.twiny()
	ax_top.set_xlim([-0.5, nckts/12-0.5])
	ax_top.set_xlabel("Visited city index (semantic)", fontdict=font)

	ax_right = ax_top.twinx()
	ax_right.set_ylim([nckts/12-0.5, -0.5])
	ax_right.set_ylabel("Visited city index (semantic)", fontdict=font)

	for ax_ in [ax, ax_top, ax_right]:
		for label in ax_.get_xticklabels() :
			label.set_fontproperties(ticks_font)
		for label in ax_.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.tight_layout()
	plt.savefig("results/tsp_weights.eps")
	plt.savefig("results/tsp_weights.png")
	plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--run', action='store_true') #collect new experimental data
parser.add_argument('--annealing_plot', action='store_true')
parser.add_argument('--solution_plot', action='store_true')
parser.add_argument('--weights_plot', action='store_true')
args = parser.parse_args()

if args.run:
	potts_tsp_trial()
if args.annealing_plot:
	tsp_annealing_graph()
if args.solution_plot:
	tsp_soln_graph()
if args.weights_plot:
	tsp_weights_graph()
