//latching system for ising/potts annealer using VRSPADs.

module latch_chain(
	input wire clk,
	input wire enable,
	input wire [143:0] pulse,
	input wire [144:0] cuts,
	output reg [143:0] state
	);

	/////////////////////////////////////////////////////////////////////////////////////////////////////
	// creat inhibition passing chains
	// there are 144 states, so only 143 cuts are used here.
	// cuts is 145 long however; there is an extra cut on each end to indicate
	// if the ends should be ising or not - just an organizational convenience
	wire [143:0] inhib_increasing, inhib_decreasing;
	assign inhib_increasing = {(inhib_increasing[142:0]|pulse[142:0])&~cuts[143:1], 1'b0};
	assign inhib_decreasing = {1'b0, (inhib_decreasing[143:1]|pulse[143:1])&~cuts[143:1]};


	// instead of directly implementing an asynchronous latch
	// - which logic tools do not like - 
	// here is an equivalent clocked version
	genvar i;
	for (i=0; i<144; i=i+1) begin
		always @(posedge clk) begin
			if (enable) begin
				//cuts on both sides indicates ising mode should be used:
				if (cuts[i] && cuts[i+1] && pulse[i]) state[i] <= ~state[i];
				//otherwise, potts latch behavior:
				else if (pulse[i]) state[i] <= 1; //latch set
				else if ( (inhib_decreasing[i] | inhib_increasing[i]) && ~pulse[i]) state[i] <= 0; //latch reset
			end
		end
	end

endmodule