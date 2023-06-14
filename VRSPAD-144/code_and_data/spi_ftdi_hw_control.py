import math
import time
from pyftdi.spi import SpiController
from pyftdi.ftdi import Ftdi
import numpy


#
#organization: this file contains small functions for interfacing with the hardware.
#One of the main goals is to abstract the hardware mapping, i.e. replace all magic indices with meaningful function names.
#
#Where multiple control actions are always used together to perform a task, these actions are merged as a single function.
#

#================================================================================ftdi spi interfaces
def FTDI_init():
	#make most of these variables global;
	#don't do this on module load, since code that references this module may be run when HW system is not connected

	spi = SpiController(cs_count=5)
	#chip select pin indices are hardcoded to pins in the following order: 0->D3, 1->D4, 2->D5, 3->D6, 4->D7 (5 Chip selects max)

	# Configure the first interface (IF/1) of the first FTDI device as a
	# SPI master
	Ftdi.PRODUCT_IDS = {1027:{'232h':24596,'ft232h':24596}} #only look for ft232 devices
	spi.configure('ftdi://::/1')

	# good to only use one frequency for all SPI interfaces, because:
	# changing freq seems to take a lot of time when switching between different SPI interfaces,
	# and adds a bunch of delay to scripts that ought to run fast
	freq = 2E6

	# Get 'port' to a specific device, and specify parameters (cs pin, bus frequency, and SPI mode)
	global dac_spi
	dac_spi = spi.get_port(cs=0, freq=freq, mode=2)

	#sets global logic configurations, such as starting and halting computation
	global global_cfg_spi
	global_cfg_spi = spi.get_port(cs=1, freq=freq, mode=0)

	#sets the weights and biases
	global weights_spi
	weights_spi = spi.get_port(cs=2, freq=freq, mode=0)

	#latches and scans out a snapshot of the BM state
	global read_states_spi
	read_states_spi = spi.get_port(cs=3, freq=freq, mode=0)

	#TBD: one last SPI available, not currently used
	# tbd_spi = spi.get_port(cs=4, freq=1E6, mode=0)


#==================================================================================DAC stuff
def AD5676_DAC_exchange(address, cmd, data):
	data = bytearray([address+cmd*16, math.floor(data/256), data%256])
	return dac_spi.exchange(data, duplex=True)

def AD5676_DAC_read_val(channel):
	address = channel
	cmd = 0b1001
	AD5676_DAC_exchange(address, cmd, 0)
	data = AD5676_DAC_exchange(0, 0, 0)
	val = data[1]*2**8+data[2]
	return val

def AD5676_DAC_set_voltage(channel, voltage, ref_voltage=3.3):
	data = int(voltage/ref_voltage*(2**16))
	address = channel
	cmd = 0b0011
	AD5676_DAC_exchange(address, cmd, data)
	rb = AD5676_DAC_read_val(channel)
	if  rb != data:
		print("Write to DAC channel %i failed, intended %i, read back %i"%(channel, data, rb))

#shorthand functions for setting the systemwide analog control variables
def set_tia_vref(v):
	AD5676_DAC_set_voltage(4, v)

def set_DAC_vref(v):
	AD5676_DAC_set_voltage(3, v)

def set_SPAD_bias(v):
	vdac = v/11.
	AD5676_DAC_set_voltage(5, vdac)

def set_illumination_current(I): #current in amps
	rset = 1.8e3
	vdac = I*rset
	AD5676_DAC_set_voltage(2, vdac)


#============================================================================logic config stuff
def global_cfg_exchange(cmd, addr, data,signed=False):
	data = bytearray([cmd, addr, data, 0])
	data = global_cfg_spi.exchange(data, duplex=True)
	unsigned = int(data[3] + data[2]*(2**8) + data[1]*(2**16) + data[0]*(2**24))
	if signed and unsigned > 2**31: #interpret returned 4 bytes as a signed 32 bit value
		return unsigned-2**32
	else: #interpret returned 4 bytes as an unsigned 32 bit value
		return unsigned

def set_cfg_byte(addr, data):
	global_cfg_exchange(1, addr, data)
	data_check = read_cfg_byte(addr)
	if data_check != data:
		print("Config write failed - tried writing %i, read value %i"%(data, data_check))

def read_cfg_byte(addr):
	global_cfg_exchange(2, addr, 0)
	return global_cfg_exchange(0, 0, 0)

def read_clked_rate_count(indx):
	global_cfg_exchange(3, indx, 0)
	return global_cfg_exchange(0, 0, 0)

def set_genesys_led(value): #sets the leds on the genesys fpga board - entirely cosmetic
	set_cfg_byte(2, value)

def rate_count(duration=0.1):
	set_cfg_byte(0, 2)#asserts reset and disabled counting, setting all counters to zero
	set_cfg_byte(0, 1)#deasserts reset and starts counting
	time.sleep(duration)
	set_cfg_byte(0, 0)#deasserts reset and count enable.  counts are stored and can be read using other functions
	#return the FPGA's measurement of the counting period:
	global_cfg_exchange(5, 0, 0)
	counting_clocks = global_cfg_exchange(0, 0, 0)
	clk_freq = 50e6
	return counting_clocks / clk_freq

def set_cycle_properties(disable_period, cycle_period):
	set_cfg_byte(6, cycle_period)
	set_cfg_byte(7, disable_period)

def write_DAC_high_byte(hb):
	set_cfg_byte(4, hb)
	set_cfg_byte(5, 1) #sets logic to write high byte instead of low byte
	time.sleep(0.01)
	set_cfg_byte(5, 0) #return to regular mode (writing low bytes to DACs)

def reset_low_energy_checker():
	set_cfg_byte(10,1) #assert reset bit
	# time.sleep(0.001)
	set_cfg_byte(10,0) #deassert reset bit

def read_energy_sums(addr, c2w_map=None):
	pipeline_delay = 9
	if c2w_map is None:
		addr = addr
	else:
		addr = c2w_map[addr]+pipeline_delay
	global_cfg_exchange(6, addr, 0)
	return global_cfg_exchange(0, 0, 0)

def read_dac_sums(addr, c2w_map=None):
	pipeline_delay = 9
	if c2w_map is None:
		addr = addr
	else:
		addr = c2w_map[addr]+pipeline_delay
	global_cfg_exchange(7, addr, 0)
	return global_cfg_exchange(0, 0, 0)

def read_lowest_energy():
	global_cfg_exchange(8,0,0)
	return global_cfg_exchange(0,0,0,signed=True)

def read_current_energy():
	global_cfg_exchange(9,0,0)
	return global_cfg_exchange(0,0,0,signed=True)

def write_weight_row(addr, potts_mode, self_index, hw_bias, alg_bias, weights):
	#addr and bias are single integers, weights should be a list of 144 integers:
	if len(weights) != 144:
		print("exactly 144 weights must be provided")

	data = bytearray([addr, potts_mode, self_index, hw_bias, alg_bias] + weights)
	data = weights_spi.exchange(data, duplex=True)

def write_weights(hw_biases, biases, weight_matrix, cuts, c2w_map=None):
	#expect biases to be a 1x144 numpy array, weights a 144x144 array
	#cuts is used to infer which rows should be written as ising nodes or as elements of a potts node
	#c2w_map (channel to weight mapping) tells which weight address to write to in order to program the given VRSPAD channel
	
	#weights preprocessing: if negative, roll over to large positive sum
	#positive values are unneffected; negative values are shifted up by 256
	weight_matrix = numpy.mod((weight_matrix + 256), 256)
	biases = numpy.mod((biases + 256), 256)
	hw_biases = numpy.mod((hw_biases + 256), 256)

	for i in range(144):
		if c2w_map is None:
			addr = i
		else:
			addr = c2w_map[i]

		bias = biases[i]
		hw_bias = hw_biases[i]
		weights = numpy.flip(weight_matrix[i,:]) #flip! arrag
		#if cut on both sides, need to do ising mode; in this case, the weight row needs to know which bm_state to multiply by
		if cuts[i] and cuts[i+1]:
			potts_mode = 0 
		else:
			potts_mode = 1 #code for performing regular potts mode

		weights = [int(w) for w in weights]
		write_weight_row(addr=int(addr), potts_mode=potts_mode, self_index=i, hw_bias=int(hw_bias), alg_bias=int(bias), weights=weights)

def write_latch_cut(cuts):
	#cuts should be a 145-long boolean numpy array
	packed = numpy.packbits(cuts[1:], bitorder='little') #first bit is automatically set to 1 in HW, so that only 9 cfg bytes are needed
	if packed.shape[0] != 18:
		print("wrong number of latch cuts, latch cuts will not be written")
		return
	# print(packed)
	for i in range(18):
		set_cfg_byte(100+i, packed[i])

#most direct access to bm state readout.
def read_bm_spi(mode=None):
	#mode specifies if one of the BM SPI's other functions should be used.
	#default is to read the BM state, assuming the default config is set, to save time
	if mode == ("lowest energy"):
		set_cfg_byte(9, 1)
	elif (mode == "cuts"):
		set_cfg_byte(9, 2)

	data = read_states_spi.exchange(18*[0], duplex=True)

	if mode is not None:
		set_cfg_byte(9, 0)

	data = numpy.array(data) #byte array to numpy uint8 array
	data = numpy.unpackbits(data)
	data = numpy.flip(data)
	# print(data)
	return data

#===========================================================================weights config stuff


#===========================================================================BM state snapshot




#test functionality: sets voltages on DAC, checks that FPGA scan chains return proper values
if __name__ == '__main__':
	for i in range(8):
		AD5676_DAC_set_voltage(i, 0.125*i)
	
	set_cfg_byte(2, 255)
	print(read_cfg_byte(2))