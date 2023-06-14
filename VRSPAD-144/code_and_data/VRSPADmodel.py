# a collection of functions pertaining to manipulating ising and potts models.
# some functions are specific to the hw architecture, but none concern the specific hw implementation
# (that is dont in spi_ftdi_hw_control)

import numpy
import math
import spi_ftdi_hw_control as hw_ctrl

#an object for holding and creating model details, specific to the variable-rate SPAD architecture
class VRSPADmodel():
	def __init__(self, node_sizes):
		#initialize weights and biases - it is intended that they be indirectly filled out peacemeal by the user
		self.weight_matrix = numpy.zeros([144, 144])
		self.biases = numpy.zeros([144])
		self.cal_biases = numpy.zeros([144])

		#VRSPAD partitioning.
		#HW can be configured for any combination of ising and variously-sized potts nodes;
		#this configuration can be defined in many ways.
		#here, a list of node sizes is the root definition, and several other forms are derived from the supplied definition.
		self.node_sizes = node_sizes

		#indices at the boundaries of the nodes
		self.cut_indices = numpy.cumsum([0]+node_sizes)

		#cuts is a populated-vector form of cut indicies, and is 145 long (matches size in hardware)
		self.cuts = numpy.zeros([145], dtype=bool)
		self.cuts[self.cut_indices] = True

		#get DAC write mapping:
		self.c2wmap = numpy.load("calibration/VRSPAD_to_weight_mapping.npy")

		#a few settings that need to be set but are not nominally adjustable:
		hw_ctrl.set_cycle_properties(60, 65)
		hw_ctrl.write_DAC_high_byte(3)


	def set_weight(self, weight, node1, q1, node2, q2):
		#for potts, weight is an energy penalty if node1 is in state q1 at the same time node2 is in state q2.
		#for ising, more or less the same meaning, weight is the energy contributed when node1 and node2 are in the same state.
		#note that this may be opposite to the sign notation you are accustomed to.

		#purpose of this function is to map weights from computational graphs to the hardware graph
		index1 = self.cut_indices[node1] + q1
		index2 = self.cut_indices[node2] + q2
		self.weight_matrix[index1, index2] = weight
		self.weight_matrix[index2, index1] = weight

	def set_bias(self, bias, node, q):
		index = self.cut_indices[node] + q
		self.biases[index] = bias

	def write_weights(self):
		#uses internal object data to write weights
		#biases need to be adjusted, according to calibration:
		hw_biases = numpy.zeros([144])
		# for i in range(144):
			# if self.cuts[i] and self.cuts[i+1]:
				#then this is an ising node, and calibration should not be used:
				# hw_biases[i] = 0
			# else:
				#calibration is needed for potts mode:
				# hw_biases[i] = self.cal_biases[i]

		hw_ctrl.write_latch_cut(self.cuts)
		hw_ctrl.write_weights(self.cal_biases, self.biases, self.weight_matrix, self.cuts, self.c2wmap)

	def set_analog_parameters(self, spad_bias, spad_illumination, window_range, window_offset):
		#does not use object state.  Just a wrapper around hw_ctrl for a little convienience
		hw_ctrl.set_DAC_vref(window_range*4)
		hw_ctrl.set_tia_vref(window_range*4+window_offset)
		hw_ctrl.set_SPAD_bias(spad_bias)
		hw_ctrl.set_illumination_current(spad_illumination)

	def sample_state(self, mode=None):
		#reads raw bm_state from hardware, and interprets it based upon the model's node partitioning
		raw_state = hw_ctrl.read_bm_spi(mode)

		#create list of  views, each view is a range of the raw state that represents a single ising or potts node
		node_onehots = numpy.split(raw_state, self.cut_indices[1:-1])

		#make sure that nodes are actually one-hot; otherwise you have a problem:
		for oh in node_onehots:
			if numpy.sum(oh) == 0:
				print("Warning: a node has no active latches")
			if numpy.sum(oh) > 1:
				print("Warning: a node has more than one active latch")

		# onehot_check = [0 if numpy.sum(oh) == 1 else 1 for oh in node_onehots]
		# if numpy.sum(onehot_check) > 0:
		# 	print("Warning: a stretch of VRSPADs that are expected to be onehot are not")

		#list comprehension to extract the active indices from each range of one-hot encoding
		node_values = [numpy.argmax(oh) if oh.shape[0] > 1 else oh[0] for oh in node_onehots]
		# print(node_values)
		# node_values = [(q-v-1) for q , v in zip(self.node_sizes, node_values)]
		# print(node_values)
		return node_values

	def is_valid_state(self, mode=None):
		#reads raw bm_state from hardware, and interprets it based upon the model's node partitioning
		raw_state = hw_ctrl.read_bm_spi(mode)

		#create list of  views, each view is a range of the raw state that represents a single ising or potts node
		node_onehots = numpy.split(raw_state, self.cut_indices[1:-1])

		#make sure that nodes are actually one-hot; otherwise you have a problem:
		for oh in node_onehots:
			if numpy.sum(oh) == 0:
				print("Warning: a node has no active latches")
				return False
			if numpy.sum(oh) > 1:
				print("Warning: a node has more than one active latch")
				return False

		return True

	def set_calibration(self, spad_bias, spad_illumination, window_range, window_offset, center_code):
		#kind of ugly, but: this function is built around assumptions of the calibration data format

		#if bias is not a half-volt multiple, interpolate the two closest calibration points together:
		# if not math.floor(spad_bias*2)/2. == spad_bias:
		# 	spad_bias_low = math.floor(spad_bias*2)/2.
		# 	spad_bias_high = math.ceil(spad_bias*2)/2.
		# 	self.set_calibration(spad_bias_low, spad_illumination, window_range, window_offset, center_code)
		# 	temps_low = self.temps
		# 	self.set_calibration(spad_bias_high, spad_illumination, window_range, window_offset, center_code)
		# 	temps_high = self.temps
		# 	print("Interpolating between calibration curves: low/actual/high: %.2f/%.2f/%.2f"%(spad_bias_low, spad_bias, spad_bias_high))
		# 	amnt = spad_bias*2 - math.floor(spad_bias*2)
		# 	self.temps = amnt*temps_high + (1-amnt)*temps_low
		# 	return (numpy.min(self.cal_biases), numpy.max(self.cal_biases))



		xfer_curves = numpy.load("calibration/VRSPAD_rates_%.1fV_%.1fuA.npy"%(spad_bias, spad_illumination*1e6))
		xfer_base = numpy.load("calibration/characterization_comparator_span.npy")

		#calibration data is on a voltage scale, but for setting biases, we need to convert it to a code scale:
		#converting voltages: range and offset are given parameters, since these are what are used when setting the DAC parameters
		vmin = window_offset
		vstep = window_range/256.
		vcenter = vmin + vstep*center_code

		#look up code in data table by finding nearest voltage on calibration axis
		data_center_index = numpy.argmin((xfer_base-vcenter)**2)

		#find the VRSPAD with the minimum rate.  This will be the anchor point.
		#all other spads will have positive biases to bring their center pulse rates in line with the minimum rate.
		VRSPAD_rates = xfer_curves[data_center_index,:]
		minSPADrate = numpy.min(VRSPAD_rates)

		#using the min SPAD rate as a target, find the calibration code that yields this rate for each target.
		cal_codes = numpy.argmin((xfer_curves-minSPADrate)**2, axis=0)
		cal_voltages = xfer_base[cal_codes]

		#finally, convert calibration voltages back to a code in the specified window:
		self.cal_biases = (cal_voltages-vmin)/vstep
		self.cal_biases = self.cal_biases.astype(numpy.uint8)

		#Also: calculate the computational temperature based on the slopes in the cal data
		#use the calibration points as one point in the slope calculation.
		#Then use calibration rates 100 (calibrated) DAC units higher as the second point
		temp_range = 100
		slope1_points = self.cal_biases
		slope2_points = self.cal_biases+temp_range

		slope1_volts = cal_voltages
		slope2_volts = vmin + vstep*slope2_points

		#now, need to go backwards and find the rate at the given voltage:
		slope1_cal_codes = cal_codes
		#want to do an outer-product broadcast, then arguement reduction, to get 144 indices at the end:
		squared_diffs = (numpy.expand_dims(xfer_base, axis=0)-numpy.expand_dims(slope2_volts, axis=1))**2
		slope2_cal_codes = numpy.argmin(squared_diffs, axis=1)

		#index into the calibration curve data to get the rates at the slope calibration points:
		order_index = numpy.linspace(0, 143, 144, dtype=numpy.uint8)
		slope1_rates = xfer_curves[slope1_cal_codes, order_index]
		slope2_rates = xfer_curves[slope2_cal_codes, order_index]

		#calculate (log) slopes:
		slope_ratios = slope1_rates/slope2_rates
		self.temps = (temp_range+1.)/numpy.log(slope_ratios)


		#return the min and max, to check that we have a roughly correct result:
		return (numpy.min(self.cal_biases), numpy.max(self.cal_biases))
