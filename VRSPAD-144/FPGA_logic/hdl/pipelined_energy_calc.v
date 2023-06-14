module piplined_energy_calc(
	input wire cs,
	input wire mosi,
	input wire sck,
	input wire clk,
	input wire [143:0] bm_state,
	input wire [7:0] system_phase,
	input wire [1:0] sum_shift_amnt,
	output reg [11:0] energy_reg,
	output reg [7:0] DAC_reg
	);

	/////////////////////////////////////////////////////////////////////////////////
	//spi slave that writes to a Block RAM in 148-byte wide chunks
	//[addr, potts_mode, my_index, hw_bias, bias, weights]
	parameter spi_width = 149;

	reg [(8*spi_width-1):0] scan_in_bits;
    wire [7:0] addr;
    wire [(8*(spi_width-1)-1):0] data;
    assign addr = scan_in_bits[(8*spi_width-1):(8*(spi_width-1))];
    assign data = scan_in_bits[(8*(spi_width-1)-1):0];
    
    //scan chain for scan_in_bits
    always @(posedge sck)
        if (~cs) scan_in_bits <= {scan_in_bits[(8*spi_width-2):0], mosi};

    
    //should infer as block RAM - 148 byte wide, 256 word deep (only actually use 36 words)
    reg [(8*(spi_width-1)-1):0] bm_weights [255:0];

    //end-of-transfer action:
    always @(posedge cs) 
    	bm_weights[addr] <= data;


    //////////////////////////////////////////////////////////////////////////////
    //map block ram read port to weight bytes
    reg [7:0] weights[143:0];
    reg [7:0] bias, hw_bias, my_index, potts_mode;
    //for ising mode, we need to explicitly know which BM index we are summing for.
    //Depending on the node's own BM state, the sum is inverted.
    
    //add eight retiming registers - should be enough so that no more than 1 add operation needs to be completed in a clock cycle
    //add retiming registers on data read from BRAM even though it is the most #of bits - 
    //at every other stage of the pipeline, there are more than 1 parallel regs, so this is just easier to write
    reg [(8*148-1):0] retimer7, retimer6, retimer5, retimer4, retimer3, retimer2, retimer1;
    always @(posedge clk) begin
    	retimer7 <= bm_weights[system_phase];
    	retimer6 <= retimer7;
    	retimer5 <= retimer6;
    	retimer4 <= retimer5;
    	retimer3 <= retimer4;
    	retimer2 <= retimer3;
    	retimer1 <= retimer2;
    end


    //latch all variables from the BRAM to named variables on the same clock cycle:
    always @(posedge clk) bias <= retimer1[(8*145-1):(8*144)];
    always @(posedge clk) hw_bias <= retimer1[(8*146-1):(8*145)];
    always @(posedge clk) my_index <= retimer1[(8*147-1):(8*146)];
    always @(posedge clk) potts_mode <= retimer1[(8*148-1):(8*147)];
    genvar i;
    for (i=0; i<144; i=i+1)
    	always @(posedge clk) weights[i] <= retimer1[(8*i+7):(8*i)];


    ///////////////////////////////////////////////////////////////////////////////
    //pipelined summation: write as a linear sum, but then add registers at end for retiming
    wire [11:0] partial_sums [143:0];
    
    //initialize partial sums with first weight
    //also extend the MSB, so that we can do normal 2's complement addition of negative numbers
    assign partial_sums[0] = ({12{bm_state[0]}}&{{4{weights[0][7]}}, weights[0]});
    //iteratively add remaining states
    for (i=1; i<144; i=i+1) begin
        assign partial_sums[i] = bm_state[i] ? 
        						partial_sums[i-1] + {{4{weights[i][7]}}, weights[i]} : 
        						partial_sums[i-1];
    end

    //the partial sum can be shifted to control the influence of individual weights,
    //i.e., if a particular model is combinatorial and only one weight is active at a time, should not shift;
    //however if many weights are active at a time, then sum should be shifted and the top bits of the sum used
    
    //bias is added after shifting, since it needs to control the full span of the DAC anyway

    wire [11:0] final_sum;
    assign final_sum = (partial_sums[143] << sum_shift_amnt) + {{4{bias[7]}}, bias};

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // we do several things with the final sum, depending on operational modes.
    // first, there are different treatments for ising and potts modes;
    // and, there is both an energy output and a DAC output,
    // with the former used for solution checking and the latter for threshold setting.
    wire [11:0] ising, potts, potential_energy, solution_energy, DAC;

    assign potts = final_sum;

    // ising requires self-feedback mode.
    // If the state is 1, then the potential energy drives the 1 to 0 transition:
    // since the energy is calculated (sigma1*sigma2), the 0 energy is always zero.
    // When the state is zero, the potential energy needs to reflect the energy of being in the 1 state.
    // final sum can be positive or negative (negative will make the 1 state more likely (negative energy))
    assign ising = bm_state[my_index] ? 0 : final_sum;
    // switch between modes
    assign potential_energy = (potts_mode[0]) ? potts : ising;
    

    // for solution checking, if in potts mode, energy is only valid if the associated state is active:
    // assign solution_energy = (potts_mode[0]) ? (bm_state[my_index] ? potts : 0)  : ising;

    // whether or not it is an ising or potts node,
    // the final sum is the energy contribution if the node is 1, and is zero otherwise.
    // Follows the multiplicative model (sigma1*sigma2), where each sigma is zero or 1.
    assign solution_energy = bm_state[my_index] ? final_sum : 0;

    // the DAC needs to be inverted and adjusted by a hardware bias.
    // A positive hw_bias allows the potential energy to operate in the negative range 
    assign DAC = 255 - potential_energy - hw_bias;

    //clip 12-bit ising_potts value to 8 bit value:
    wire [7:0] DAC_clipped;
    assign DAC_clipped = DAC[11] ? 0 : //assume this is an overflow from the negative direction, and clip to zero
    					DAC < 256 ? DAC : 255; //otherwise, if less than 256, pass value; otherwise, clip to 255 
    

    //latch final results to module output registers
    always @(posedge clk) begin
    	energy_reg <= solution_energy;
    	DAC_reg <= DAC_clipped;
    end


endmodule