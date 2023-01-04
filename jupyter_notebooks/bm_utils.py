import numpy
np = numpy

#utility functions for working with boltzmann models in the software domain:
#generate a random model for testing
#convert between different model and weight formats 
#translate between state indices and state representation vectors

def eight_bit_ising():
    nbits = 8
    weights = np.zeros([nbits, nbits])
    biases = np.zeros([nbits])
    for i in range(nbits):
        for j in range(i-1):
            weights[i,j] = np.random.randint(-6,6)
            weights[j,i] = weights[i,j]
        biases[i] = np.random.randint(-12,12)

    #directly calc energy of each state:
    state_energy = np.zeros([2**nbits])
    state_vectors = index2ising(np.arange(2**nbits))
    for i in range(2**nbits):
        state = (state_vectors[i]*2)-1 #convert to +- 1 scale
        #print(state)
        E_t = 0.5*numpy.matmul(numpy.transpose(state), numpy.matmul(weights, state))+numpy.matmul(state,biases)
        state_energy[i] = E_t
    
    return weights, biases, state_energy


def ising2potts(weights, biases):
    #converts 8 bit ising model to a 4x4 bit potts model:
    #they have the exact same states and energies, but the weights and model update dynamics are different
    potts_weights = np.zeros([4,4,4,4])
    potts_biases = np.zeros([4,4])
    
    #convert weights! qubits, since they are quaternary bits...
    #each single potts weight encodes part of the interaction between four separate bits in the ising model:
    sign_0_lookup = [-1, 1, -1, 1]
    sign_1_lookup = [-1, -1, 1, 1]
    for s_qubit in range(4): #source potts bit - controls activity of weight
        s_pbit_0 = s_qubit*2
        s_pbit_1 = s_qubit*2+1 
        for s_pos in range(4): #source position within source qubit
            s_pbit_0_sign = sign_0_lookup[s_pos]
            s_pbit_1_sign = sign_1_lookup[s_pos]
            for d_qubit in range(4): #destination potts bit - bit controlled by weight
                d_pbit_0 = d_qubit*2
                d_pbit_1 = d_qubit*2+1
                for d_pos in range(4): #destination position within destination qubit
                    d_pbit_0_sign = sign_0_lookup[d_pos]
                    d_pbit_1_sign = sign_1_lookup[d_pos]
                    w = 0
                    w = w + s_pbit_0_sign*d_pbit_0_sign*weights[s_pbit_0, d_pbit_0]
                    w = w + s_pbit_1_sign*d_pbit_0_sign*weights[s_pbit_1, d_pbit_0]
                    w = w + s_pbit_0_sign*d_pbit_1_sign*weights[s_pbit_0, d_pbit_1]
                    w = w + s_pbit_1_sign*d_pbit_1_sign*weights[s_pbit_1, d_pbit_1]
                    potts_weights[s_qubit, s_pos, d_qubit, d_pos] = w
            b = s_pbit_0_sign*biases[s_pbit_0] + s_pbit_1_sign*biases[s_pbit_1]
            potts_biases[s_qubit, s_pos] = b
                    
                    #the potts weight is the sum of partial sums that would be active on the two equivalent destination ising bits if the two equivalent ising source bits were in the particular configuration
    
    return potts_weights, potts_biases

def ising2hardware(weights, biases):
    #maps between 8x8 weight matrix and the 16x16 weight matrix implimented in the FPGA
    
    #set up weights and biases for differential operation: i.e. for a positive energy sum, 
    #the positive state SPAD triggers more often and the negative state SPAD sees an equal but negative energy sum and triggers less often
    
    #in dedicated ising hardware there would be one set of weights for both positive and negative SPADs,
    #however since the FPGA is configured for either ising or potts models,
    #the positive and negative SPADs in the ising configuration are driven by different weights
    
    hw_weights = np.zeros([16, 16])
    hw_biases = np.zeros([16])
    for i in range(8):
        #eight biases: positive (odd) nodes get same-sign bias, negative (even) nodes get negated bias
        hw_biases[i*2] = -biases[i] 
        #negative values not supported in HW, with however SPAD calibration offset will make actual bias value positive
        hw_biases[i*2+1] = biases[i]
        
        for j in range(8):
            #weight between i and j: 
            #if positive, there are positive values in the positive-to-positive and the negative-to-negative weights;
            #if negative, there are positive values in the negative-to-positive and the postive-to-negative weight positions
            
            #to replicate full swing of a negative to a positive state multiplication,
            #weights are doubled and subtracted from the bias of each SPAD
            
            w = weights[i,j]
            if w > 0:
                hw_weights[i*2, j*2] = 2*w
                hw_biases[i*2] = hw_biases[i*2] - w
                hw_weights[i*2+1, j*2+1] = 2*w
                hw_biases[i*2+1] = hw_biases[i*2+1] - w
            else:
                hw_weights[i*2+1, j*2] = -2*w
                hw_biases[i*2+1] = hw_biases[i*2+1] + w
                hw_weights[i*2, j*2+1] = -2*w
                hw_biases[i*2] = hw_biases[i*2] + w
                
    return hw_weights, hw_biases

    
def potts2hardware(weights, biases):
    hw_weights = np.zeros([16, 16])
    hw_biases = np.zeros([16])
    
    for s_qubit in range(4): #source potts bit - controls activity of weight
        for s_pos in range(4): #source position within source qubit
            hw_biases[s_qubit*4+s_pos] = biases[s_qubit, s_pos]
            for d_qubit in range(4): #destination potts bit - bit controlled by weight
                for d_pos in range(4): #destination position within destination qubit
                    hw_weights[s_qubit*4+s_pos,d_qubit*4+d_pos] = weights[s_qubit, s_pos, d_qubit, d_pos]
                    
    return hw_weights, hw_biases
    
def index2ising(indicies):
    return (((indicies[:,None] & (1 << np.arange(8)))) > 0).astype(int)

def ising2index(ising_form):
    index_form = np.zeros([ising_form.shape[0]])
    for i in range(8):
        index_form = index_form + 2**i * ising_form[:,i]
    return index_form.astype(int)

def index2potts(indices):
    pass

def potts2index(potts_form):
    index_form = np.zeros([potts_form.shape[0]])
    for qubit in range(4):
        index_form = index_form + 4**qubit*potts_form[:,qubit]
    return index_form.astype(int) 

def raw2ising(raw_states):
    #converts n x 16 state representation into a n x 8 representation
    ising_states = numpy.zeros([raw_states.shape[0],8])
    for pbit in range(8):
        ising_states[:,pbit] = raw_states[:,pbit*2+1]
    return ising_states #0, 1 format

def raw2potts(raw_states):
    potts_states = numpy.zeros([raw_states.shape[0],4])
    for qubit in range(4):
        #essentially, convert from locally one-hot to locally indexed
        potts_states[:,qubit] = 1*raw_states[:,qubit*4+1] + 2*raw_states[:,qubit*4+2] + 3*raw_states[:,qubit*4+3]
    return potts_states
