#different tasks to run: run different tasks based on cmd line input
import argparse
import numpy
from matplotlib import pyplot as plt
import matplotlib
import time
import networkx as nx
from labellines import labelLines
import pickle
import math

font = {'size': 9, 'fontname': 'Century Gothic'}
ticks_font = matplotlib.font_manager.FontProperties(family=font['fontname'], style='normal', size=9, weight='normal', stretch='normal')

def get_data(fname):
	#load data into namespace n
	with open(fname, 'rb') as f:
		data_dict = pickle.load(f)
	n = argparse.Namespace(**data_dict)
	return n

def potts_cal():
	n = get_data("results/potts_cal_data.pkl")
	bar_range = numpy.linspace(0,len(n.w_opts)-1, len(n.w_opts))
	bar_labels = ["%s"%w for w in n.w_opts]

	plt.figure(figsize=(3,2), layout='tight')
	plt.bar(bar_range, n.success_rates, 0.8)
	plt.ylabel("success rate within %.2fs"%n.tmax, fontdict=font)
	# plt.title("Potts calibration")
	plt.xlabel("graph edge weight", fontdict=font)
	plt.xticks(bar_range, bar_labels)

	for ax_ in [plt.gca()]:
		for label in ax_.get_xticklabels() :
			label.set_fontproperties(ticks_font)
		for label in ax_.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.gca().spines[['right', 'top']].set_visible(False)

	plt.savefig("results/coloring_potts_parameter_sweep.eps")
	plt.savefig("results/coloring_potts_parameter_sweep.png")	
	plt.show()

def cpuSA_cal():
	n = get_data("results/cpuSA_cal_data.pkl")
	bar_range = numpy.linspace(0,len(n.temp_opts)-1, len(n.temp_opts))
	bar_labels = ["%s"%w for w in n.temp_opts]

	plt.figure(figsize=(3,2), layout='tight')
	plt.bar(bar_range, n.success_rates, 0.8)
	plt.ylabel("success rate within %.2fs"%n.tmax, fontdict=font)
	# plt.title("Potts calibration")
	plt.xlabel("simulated annealing temperature", fontdict=font)
	plt.xticks(bar_range, bar_labels)

	for ax_ in [plt.gca()]:
		for label in ax_.get_xticklabels() :
			label.set_fontproperties(ticks_font)
		for label in ax_.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.gca().spines[['right', 'top']].set_visible(False)

	plt.savefig("results/coloring_cpuSA_parameter_sweep.eps")
	plt.savefig("results/coloring_cpuSA_parameter_sweep.png")	
	plt.show()

def ising_cal():
	n = get_data("results/ising_cal_data.pkl")
	bar_range = numpy.linspace(0,len(n.success_rates)-1, len(n.success_rates))

	#get arrays of best bias and corresponding success rates, the old fashioned way (a loop):
	best_biases = numpy.zeros([len(n.w_opts), len(n.inhib_opts)])
	best_rates =  numpy.zeros([len(n.w_opts), len(n.inhib_opts)])
	for i, w in enumerate(n.w_opts):
		for j, inhib in enumerate(n.inhib_opts):
			for k, bias in enumerate(n.bias_opts):
				rate = n.success_rates.pop(0) #since this is just a list created by appending
				if rate > best_rates[i,j]:
					best_rates[i,j] = rate
					best_biases[i,j] = bias

	plt.figure(figsize=(4,3))
	obj = plt.imshow(best_rates, aspect='auto')
	cbar = plt.colorbar(obj, shrink=0.7)
	cbar.set_label('solution success rate', rotation=90, fontdict=font)
	plt.yticks(range(len(n.w_opts)), n.w_opts)
	plt.ylabel("Connective weight options", fontdict=font)
	plt.xticks(range(len(n.inhib_opts)), n.inhib_opts)
	plt.xlabel("Inhibitory weight options", fontdict=font)
	plt.title("Annotations: best bias", fontdict=font)

	#label sites with best bias values:
	for i, w in enumerate(n.w_opts):
		for j, inhib in enumerate(n.inhib_opts):
			plt.text(j,i, str(best_biases[i,j]), fontdict=font, ha='center', va='center', c='black')

	# plt.show()


	# plt.figure(figsize=(6,2.5))
	# plt.bar(bar_range, n.success_rates, 0.8)
	# plt.ylabel("success rate within %.2fs"%n.tmax, fontdict=font)
	# # plt.title("Ising calibration")
	# plt.xlabel("weight, inhibition, bias", fontdict=font)

	# # minbar = numpy.min(n.success_rates)
	# # plt.ylim([0, minbar*3])

	# #replace newlines with spacees:
	# n.bar_labels = [s.replace('\n', ' ') for s in n.bar_labels]
	# plt.xticks(bar_range, n.bar_labels, rotation=90)

	for ax_ in [plt.gca()]:
		for label in ax_.get_xticklabels() :
			label.set_fontproperties(ticks_font)
		for label in ax_.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.tight_layout()
	plt.savefig("results/coloring_ising_parameter_sweep.eps")
	plt.savefig("results/coloring_ising_parameter_sweep.png")
	plt.show()

def dist_graph():
	n = get_data("results/dist_graph_data.pkl")

	n.potts_times.sort()
	n.ising_times.sort()
	n.cpuSA_times.sort()
	n.dsatur_times.sort()

	ntrials = len(n.potts_times)

	 #used for all - y data points
	cum_prob = numpy.linspace(0,1,ntrials)

	plt.figure(figsize=(4., 2.5))
	ax = plt.gca()
	
	integration_gain = 100.

	#subtract out usb latency:
	latency = numpy.min(n.potts_times) - 1e-4 #latency is roughly equal to the minimum time (assume fastest instance was solved instantly)
	n.potts_times = n.potts_times-latency
	n.ising_times = n.ising_times-latency

	plt.plot(n.dsatur_times, cum_prob, label='DSATUR', c='limegreen')
	plt.plot([t/integration_gain if t < n.tmax else 2 for t in n.potts_times], cum_prob, label='Potts\n(predicted)', c='dodgerblue')
	plt.plot(n.cpuSA_times, cum_prob, label='CPU', c='steelblue')
	plt.plot(n.potts_times, cum_prob, label='Potts', c='darkslateblue')
	plt.plot(n.ising_times, cum_prob, label='Ising', c='black')

	#add labeled arrow from Potts to Potts (predicted):
	#first, need to pick a horizontal line level, then determine start and end points on x axis
	lvl = 0.13
	xstart = n.potts_times[int(lvl*ntrials)]
	xend = xstart / integration_gain

	# plt.arrow(xstart, lvl, (xend-xstart), 0, length_includes_head=True)
	plt.plot([xend, xstart], [lvl, lvl], color='darkolivegreen', label='CMOS\nintegration')
	plt.scatter(xend*1.2, lvl, marker="<", color='darkolivegreen')

	lbl_lvl = 0.3
	xvals = [0.4,
			 n.potts_times[int(lbl_lvl*ntrials*1.1)]/integration_gain,
			 n.cpuSA_times[int(lbl_lvl*ntrials*0.9)],
			 n.potts_times[int(lbl_lvl*ntrials*1.1)],
			 n.ising_times[int(lbl_lvl*ntrials*0.9)],
			 xstart/(integration_gain**0.5)]

	#set parameters for background box, so that lines do not peep through middle of text labels:
	bbox = {'pad': 0.5, 'fc': 'w', 'ec': 'w'}
	#nvmd: outline_width can do this instead
	labelLines(plt.gca().get_lines(), align=False, fontsize=font['size'], fontname=font['fontname'], outline_width=6, xvals=xvals)


	plt.xlim([0.00001, n.tmax])
	plt.xscale('log')
	plt.xlabel("execution time, s", fontdict=font)
	plt.ylim([0,0.45])
	plt.ylabel("solution probability", fontdict=font)
	ax.spines[['right', 'top']].set_visible(False)
	#change font on ticks
	for label in ax.get_xticklabels() :
		label.set_fontproperties(ticks_font)
	for label in ax.get_yticklabels() :
	    label.set_fontproperties(ticks_font)

	#remove 'both' major and minor ticks on y only - keep on x, since x is a log scale
	ax.tick_params(axis='y', which='both',length=0)
	plt.tight_layout()
	plt.savefig("results/coloring_soln_dist.eps")
	plt.savefig("results/coloring_soln_dist.png")
	plt.show()

def soln_graph():
	n = get_data("results/graph_data.pkl")
	#map solution indices to colors for plotting:
	colors = ['tab:red', 'tab:green', 'tab:blue']
	coloring = [colors[c] for c in n.coloring]

	plt.figure(figsize=(7, 7))
	nx.draw_kamada_kawai(n.G, node_color=coloring)
	plt.savefig("results/coloring_soln_vis.eps")
	plt.savefig("results/coloring_soln_vis.png")
	plt.show()

def weights_vis():
	n = get_data("results/coloring_weight_vis.pkl")

	# data prep ============================================================================================
	nckts = 144
	weights = n.ising_coloring_model.weight_matrix

	#create an index-colored representation of the weight matrix:
	weight_img = numpy.zeros(weights.shape+(3,)) #adds a size-3 dimension at the end
	for i, j in numpy.ndindex(weights.shape):
		#recolor by weight type:
		if weights[i,j] == n.w_ising:
			weight_img[i,j,:] = [0,0,0]
		elif weights[i,j] == n.inhib:
			weight_img[i,j,:] = [1,0,0]
		elif ((math.floor(i/3.)+math.floor(j/3.))%2)==0:
			weight_img[i,j,:] = [1,1,1]
		else:
			weight_img[i,j,:] = [0.95,0.95,1]

	#create 

	#actual plotting code ==============================================================================
	plt.figure(figsize=(5,5), layout='tight')

	#actual drawing / plotting:
	pcolor_spacing = numpy.linspace(-0.5, nckts-0.5, nckts+1)
	plt.pcolormesh(pcolor_spacing, pcolor_spacing, weight_img, shading='flat')
	
	plt.ylabel("VRSPAD index (physical hardware)", fontdict=font)
	plt.xlabel("VRSPAD index (physical hardware)", fontdict=font)
	plt.ylim([nckts-0.5, -0.5])
	plt.xlim([-0.5, nckts-0.5])

	ax = plt.gca()

	ax_top = ax.twiny() #twin axis, not for plotting, but for labeling top of weight matrix
	ax_top.set_xlabel("coloring graph node (semantic)", fontdict=font)
	ax_top.set_xlim([-0.5, (nckts/3)-0.5])

	ax_right = ax_top.twinx()
	ax_right.set_ylabel("coloring graph node (semantic)", fontdict=font)
	ax_right.set_ylim([(nckts/3)-0.5, -0.5])

	for ax_ in [ax, ax_top, ax_right]:
		for label in ax_.get_xticklabels() :
			label.set_fontproperties(ticks_font)
		for label in ax_.get_yticklabels() :
		    label.set_fontproperties(ticks_font)

	plt.savefig("results/coloring_potts_weights.eps")
	plt.savefig("results/coloring_potts_weights.png")
	plt.show()

	# # data prep ============================================================================================
	# #take subselection of weights for visualization (a graph coloring problem with fewer nodes):
	# nckts = 3*48 #must be a multiple of 3 to make sense!
	# suborigin = 3*0 #must be multiple of 3 for plot to make sense!
	# weights = n.ising_coloring_model.weight_matrix[suborigin:(suborigin+nckts), suborigin:(suborigin+nckts)]

	# #create state and state interpretation vectors:
	# BM_states = numpy.zeros([nckts])
	# for i in range(int(nckts/3)):
	# 	active = numpy.random.randint(0,3)
	# 	BM_states[i*3+active] = 1

	# states_img = numpy.zeros([nckts,1,3])
	# for i in range(nckts):
	# 	states_img[i,0,i%3] = 1 #iterates color thru R, G, B
	# 	if BM_states[i] == 0:
	# 		states_img[i,0,:] = states_img[i,0,:] + 1 #fade out inactive state bits
	# states_img  =numpy.clip(states_img, 0, 1)

	# # create threshold values (fixed value is biases):
	# thresholds = numpy.matmul(weights, BM_states)
	# thresholds = numpy.expand_dims(thresholds, 1)
	# thresholds = thresholds-numpy.min(thresholds) #scale to range 0,1
	# thresholds = thresholds/numpy.max(thresholds) #scale to range 0,1

	# #create an index-colored representation of the weight matrix:
	# weight_img = numpy.zeros(weights.shape+(3,)) #adds a size-3 dimension at the end
	# for i, j in numpy.ndindex(weights.shape):
	# 	#recolor by weight type:
	# 	if weights[i,j] == n.w_ising:
	# 		weight_img[i,j,:] = [0,0,0]
	# 	elif weights[i,j] == n.inhib:
	# 		weight_img[i,j,:] = [1,0,0]
	# 	elif ((math.floor(i/3.)+math.floor(j/3.))%2)==0:
	# 		weight_img[i,j,:] = [1,1,1]
	# 	else:
	# 		weight_img[i,j,:] = [0.95,0.95,1]

	# #create biases vector: all are the same
	# biases_img = numpy.zeros([nckts,1,3])
	# biases_img[:,:,0] = 1
	# biases_img[:,:,1] = 1 #makes color yellow. Just a visualization thing

	# #actual plotting code ==============================================================================
	# grid_cols = nckts
	# plt.figure(figsize=(6,5), layout='constrained')
	# ax_threshold = plt.subplot2grid((1, grid_cols), (0, 0), 1, 1)
	# ax = plt.subplot2grid((1, grid_cols), (0, 1), 1, grid_cols-2)
	# ax_state = plt.subplot2grid((1, grid_cols), (0, grid_cols-1), 1, 1)

	# #actual drawing / plotting:
	# pcolor_spacing = numpy.linspace(-0.5, nckts-0.5, nckts+1)
	# ax.pcolormesh(pcolor_spacing, pcolor_spacing, weight_img, shading='flat')
	# # ax_bias.imshow(biases_img, aspect='auto')
	# ax_state.pcolormesh([-0.5, 0.5], pcolor_spacing, states_img, shading='flat')
	# ax_threshold.pcolormesh([-0.5, 0.5], pcolor_spacing, thresholds, shading='flat', cmap='gray')
	# for i in range(int(nckts/3)): 	#draw boxes around color sets:
	# 	rect = matplotlib.patches.Rectangle((-0.5, i*3-0.5), 1, 3, linewidth=1, edgecolor='black', facecolor='none')
	# 	ax_state.add_patch(rect)


	# #axes garnish:
	# # ax_bias.set_xlabel("Biases", fontdict=font, rotation=90)
	# # ax_bias.set_ylabel()
	# # ax_bias.set_xticks([])
	# # ax_bias.set_yticks([12*i for i in range(12)])

	# ax_threshold.set_xlabel("VRSPAD\nthresholds", fontdict=font, rotation=90)
	# ax_threshold.set_ylabel("VRSPAD index (physical hardware)", fontdict=font)
	# ax_threshold.set_xticks([])
	# ax_threshold.set_ylim([nckts-0.5, -0.5])

	# ax.set_yticks([])
	# ax.set_ylabel("=", rotation=0)
	# ax.set_xlabel("VRSPAD index (physical hardware)\nweights", fontdict=font)
	# ax.set_ylim([nckts-0.5, -0.5])
	# ax.set_xlim([-0.5, nckts-0.5])

	# ax_top = ax.twiny() #twin axis, not for plotting, but for labeling top of weight matrix
	# ax_top.set_xlabel("coloring graph node (semantic)", fontdict=font)
	# ax_top.set_xlim([-0.5, (nckts/3)-0.5])

	# # ax_state.spines[['top', 'bottom', 'left', 'right']].set_visible(False)

	# ax_state.set_xlabel("Potts\nstate", fontdict=font, rotation=90)
	# ax_state.set_ylabel("*", rotation=0)
	# ax_state.set_xticks([])
	# ax_state.set_yticks([])

	# ax_right = ax_state.twinx()
	# ax_right.set_ylabel("coloring graph node (semantic)", fontdict=font)
	# ax_right.set_ylim([(nckts/3)-0.5, -0.5])

	# for ax_ in [ax, ax_state, ax_threshold, ax_top, ax_right]:
	# 	for label in ax_.get_xticklabels() :
	# 		label.set_fontproperties(ticks_font)
	# 	for label in ax_.get_yticklabels() :
	# 	    label.set_fontproperties(ticks_font)

	# plt.savefig("results/coloring_potts_weights.eps")
	# plt.savefig("results/coloring_potts_weights.png")
	# plt.show()

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--potts_cal', action='store_true') #scans weight param to find optimal potts weight
	parser.add_argument('--cpuSA_cal', action='store_true')
	parser.add_argument('--ising_cal', action='store_true') #scans ising parameters
	parser.add_argument('--dist_graph', action='store_true') #using fixed parameters, measures statistics of ising and potts solutions
	parser.add_argument('--soln_graph', action='store_true') #plots an instance of a solved graph
	parser.add_argument('--weights_vis', action='store_true') #visualize the graph coloring weight matrix
	args = parser.parse_args()

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
		weights_vis()