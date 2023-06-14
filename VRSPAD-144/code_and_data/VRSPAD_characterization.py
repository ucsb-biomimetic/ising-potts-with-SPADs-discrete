import spi_ftdi_hw_control as hw_ctrl
import numpy
import math
from matplotlib import pyplot as plt
import matplotlib
import argparse


#iterate through SPAD biases and illuminations: (number of tests is product of list lengths!)
illums = [0e-6, 100e-6, 200e-6, 500e-6]
biases = [30.0, 30.5, 31.0, 31.5]

#short version of test: just one set of conditions
# illums = [2e-4]
# biases = [30.75]

hw_ctrl.FTDI_init()

# these settings can be tuned to change system behavior/performance.
# however we do not need to explore them.
# DAC vref and tia vref can be used to control the DAC comparator window;
# This script measures the maximum comparator span,
# and specific uses of the system use a sub-window of the characterization curves.
hw_ctrl.set_DAC_vref(2.0)
hw_ctrl.set_tia_vref(2.0)

# trades off compute speed for isolation from threshold DAC write noise
hw_ctrl.set_cycle_properties(60, 90)

# this will usually be set like this in normal operation;
# however, this script iterates through DAC high byte values in order to measure a full 2V span (which is unachievable in normal operation)
hw_ctrl.write_DAC_high_byte(3) 

########################################################################################################################
# automatically figure out which weight rows in verilog end up driving which VRSPAD channels:
# (this can obviously be inferred from the design, but easier to do it this way)
def make_weight_mapping():
	hw_ctrl.set_SPAD_bias(30)
	hw_ctrl.set_illumination_current(0) #dark rates are sufficient
	mapping = numpy.zeros([144]) #result vector, for which entry i contains which SPAD channel is fastest when bias i is set
	for channel_num in range(144):
		b = numpy.zeros([144])+255
		w = numpy.zeros([144, 144])
		b[channel_num] = 0 #set a single channel to produce pulses at a fast rate - then we measure which one is the fast one
		hw_ctrl.write_weights(b, w)
		counting_time = hw_ctrl.rate_count(0.1)
		rates = numpy.zeros([144])
		for j in range(144):
			rates[j] = hw_ctrl.read_clked_rate_count(j)/counting_time
		fastest = numpy.argmax(rates)
		mapping[channel_num] = fastest
		if channel_num < 10: #print the first ten, to see how things are going
			print(fastest)
		elif channel_num == 10:
			print("...")


	#numpy.unique can be used to make sure that the mapping algorithm worked, and -
	#to return the index which is what we actually need (need to think a little to see that it is true)
	mapping_unique, mapping = numpy.unique(mapping, return_index=True)
	#mapping should now be the inverse, i.e. of the form VRSPAD channel -> weight index
	if mapping_unique.shape[0] < 144:
		print("mapping error, not all VRSPAD channels have a corresponding weight index")
		#report which channels are missing:
		missing_channels = []
		for i in range(144):
			if numpy.sum(0==(mapping_unique-i)) != 1:
				missing_channels.append(i)
		print("missing channels are:")
		print(missing_channels)

	#if it worked, we can save:
	else:
		numpy.save("calibration/VRSPAD_to_weight_mapping", mapping)

#now, load mapping - will be either one we just measured, or an old one, depending on how the mapping process went

#############################################################################################################################

def measure_characterizations():
	mapping = numpy.load("calibration/VRSPAD_to_weight_mapping.npy")
	#calc spanning voltage ahead of time: (not used in HW, just for SW reference):
	comparator_span = numpy.linspace(0, 1.0, 512)
	numpy.save("calibration/characterization_comparator_span", comparator_span)

	for b_i, bias in enumerate(biases):
		for i_i, illum in enumerate(illums):
			hw_ctrl.set_SPAD_bias(bias)
			hw_ctrl.set_illumination_current(illum)

			#measure pulse rate vs threshold transfer fn
			rates = numpy.zeros([512, 144])
			test_order = numpy.linspace(numpy.zeros([144]), numpy.zeros([144])+255, 256) #generates 144 sequences from 0 to 255
			#in order to randomize the order in which thresholds are tested,
			#leave following line uncommented (for more realistic conditions, to check that hardware mapping is correct)
			test_order = numpy.random.permutation(test_order)
			for i in range(512):
				print("testing condition: bias %.1f V, illum %.1f uA, %i%s done"%(bias, illum*1e6, 100*i/512., '%'), end='\r', flush=True)
				i_low_byte = i%256
				i_high_byte = math.floor(i/256.)
				b = test_order[i_low_byte, :]
				w = numpy.zeros([144, 144])
				hw_ctrl.write_DAC_high_byte(3-i_high_byte)
				hw_ctrl.write_weights(b, w, cuts=numpy.zeros([145]), c2w_map = mapping)
				counting_time = hw_ctrl.rate_count(0.1)
				for j in range(144):
					threshold_int = int(256*i_high_byte+test_order[i_low_byte,j])
					rates[threshold_int, j] = hw_ctrl.read_clked_rate_count(j)/counting_time

			#save transfer functions:
			numpy.save("calibration/VRSPAD_rates_%.1fV_%.1fuA"%(bias, illum*1e6), rates)


def curves_plot():
	#in an array of axes, plot the transfer curves of each VRSPAD
	font_small = {'size': 9, 'fontname': 'Century Gothic'}
	font_big = {'size': 11, 'fontname': 'Century Gothic'}
	ticks_font = matplotlib.font_manager.FontProperties(family='Century Gothic', style='normal', size=9, weight='normal', stretch='normal')

	plt.figure(figsize=(6,6))

	comparator_span = numpy.load("calibration/characterization_comparator_span.npy")

	for b_i, bias in enumerate(biases):
		for i_i, illum in enumerate(illums):
			#load transfer functions:
			rates = numpy.load("calibration/VRSPAD_rates_%.1fV_%.1fuA.npy"%(bias, illum*1e6))

			plt.subplot(len(illums), len(biases), (len(biases)*i_i)+b_i+1)
			for j in range(144):
				plt.plot(comparator_span, rates[:, j]/1e6, rasterized=True) #rasterize, so that EPS file isn't huge
			plt.yscale('log')
			plt.ylim([1e-5, 1e1])
			plt.xlim([0,1])

			plt.xticks([0.1,0.5,0.9])
			plt.yticks([1e-4, 1e-2, 1e0])

			#depending on where we are in the plot array, do different things for the axis garnish
			if i_i < len(illums)-1:
				#not bottom row, so should hide x ticks completely
				plt.xticks([])
			else:
				plt.xlabel("threshold, V", fontdict=font_small)

			if b_i > 0:
				#not at left row, so should hide y ticks completely
				plt.yticks([])
			else:
				plt.ylabel("pulse rate, MHz", fontdict=font_small)

			for ax_ in [plt.gca()]:
				for label in ax_.get_xticklabels() :
					label.set_fontproperties(ticks_font)
				for label in ax_.get_yticklabels() :
				    label.set_fontproperties(ticks_font)

			#get axes for top and right annotations:
			ax = plt.gca()
			ax_top = ax.twiny()
			ax_right = ax_top.twinx()

			ax.spines[['right', 'top']].set_visible(False)
			ax_top.spines[['right', 'top']].set_visible(False)
			ax_right.spines[['right', 'top']].set_visible(False)

			#never need top or right ticks (but will use top and right axis labels):
			ax_top.set_xticks([])
			ax_right.set_yticks([])

			if i_i == 0:
				#at top row, so should annotate with bias:
				ax_top.set_xlabel("Bias: %.1f"%bias, fontdict=font_big)

			if b_i == len(biases)-1:
				#at right column, annotate with illumination:
				ax_right.set_ylabel("Illum: %i uA"%(illum*1e6), fontdict=font_big)



	plt.tight_layout(pad=0.4)
	plt.savefig("calibration/rate_curves.eps")
	plt.savefig("calibration/rate_curves.png")
	plt.show() #results are plotted at the end

##########################################################################################################################
#spatially-plotted data for debugging hardware
def spatial_plot():
	#calculate rates at center value, and slopes of transfer function:
	slopes = rates[50, :]/rates[150, :] #log scale, so slope is actually a ratio

	#next, plot rate and slope values as a function of spatial position on the PCB:
	spatial_slopes = numpy.zeros([4*2, 9*2])
	spatial_mid_rates = numpy.zeros([4*2, 9*2])

	for pulse_num in range(144):
		#need to map between indices and positions. Fortunately, the pcb follows a regular structure:
		row_num = math.floor(pulse_num / 8) #16 per IC row, but each IC row is evenly split into two sub-rows of 8 units each
		col_num = (pulse_num % 4)*2
		if row_num % 2 == 0:
			if pulse_num % 8 < 4:
				col_num = col_num + 1
		else:
			if pulse_num % 8 > 3:
				col_num = col_num + 1
		spatial_slopes[col_num, 17-row_num] = slopes[pulse_num]
		spatial_mid_rates[col_num, 17-row_num] = rates[128, pulse_num]

	plt.figure()

	plt.imshow(numpy.log(1 + numpy.transpose(spatial_mid_rates)))

	#annotation:
	for i in range(8):
		for j in range(18):
			plt.text(i, j, "%.1f"%math.log10(1+spatial_mid_rates[i,j]), ha="center", va="center", color="b")

	plt.show()

#=action manager==================================================================================

parser = argparse.ArgumentParser()
parser.add_argument('--index_map', action='store_true') #collect new experimental data
parser.add_argument('--collect', action='store_true')
parser.add_argument('--curves_plot', action='store_true')
parser.add_argument('--spatial_plot', action='store_true')
args = parser.parse_args()

if args.index_map:
	make_weight_mapping()
if args.collect:
	measure_characterizations()
if args.curves_plot:
	curves_plot()
if args.spatial_plot:
	spatial_plot()