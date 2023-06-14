//main logic module for VRSPAD-144 demo system.
//includes:
//4 banks of pipelined adders feeding directly into the DAC writeback channels (setting thresholds on the PCB);
//counters to measure VRSPAD transfer characteristics;
//low-energy checking module to keep track of the best-solution-so-far;
//several slave SPI interfaces for configuring and sending data to a host computer via an FTDI chip:
//  one 4-byte interface for setting general configuration values and reading some performance results,
//  one 18-byte (144 bit) interface for reading the boltzmann machine state,
//  one 146-byte interface for writing boltzmann machine weights into block memory for use by the pipelined adders 

//Author: William Whitehead
//Date: April 2023

module ising_or_potts(
        //200 MHz input clock - recieved differentially
        input sysclk_n,
        input sysclk_p,

        //connected to reset pin on genesys 2 fpga board
        input cpu_resetn,

        //inputs from VRSPAD circuits
        input wire [144:1] pulse_in,
        
        //threshold DAC outputs
        output reg [7:0] BUS1,
        output reg [7:0] BUS2,
        output reg [7:0] BUS3,
        output reg [7:0] BUS4,
        output reg [1:0] A,
        output reg [9:1] WR,
        output reg HBEN,

        //LED, for basic functionality checking
        output wire [7:0] led,
        
        //SPI interface to FTDI chip for interfacing configration and results to a PC:
        input wire sck,
        input wire mosi,
        output reg miso,
        input wire cs2,
        input wire cs3,
        input wire cs4,
        input wire cs5
    );
    genvar i, k;
    integer j;

    wire clk200;
    reg clk100, clk;
    IBUFDS buf1(.I(sysclk_p), .IB(sysclk_n), .O(clk200));  //differential to single-ended
    
    always @(posedge clk200) clk100 <= ~clk100;
    always @(posedge clk100) clk <= ~clk;

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //pre-process SPAD signals ==============================================================================================================
    reg [143:0] edge_reg_1, spad_pulse_sync, spad_pulse_sync_gated;
        
    // edge-detecting registers for processing SPAD inputs:   
    for (i=0; i<144; i=i+1) begin
        always @(posedge clk) begin
            edge_reg_1[i] <= pulse_in[i+1];
            spad_pulse_sync[i] <= (pulse_in[i+1] & ~edge_reg_1[i]); //async to sync
            spad_pulse_sync_gated[i] = 0;//(DAC_pointer > update_delay) & (pulse_in[i+1] & ~edge_reg_1[i]);
        end
    end
    
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //phase pointer: controls when threshold DACs are written to, and when to halt reception of the VRSPAD pulses

    reg [7:0] phase_pointer; //a counter that controls when everything happens
    wire [7:0] cycle_period; //a config input; determines when to reset the phase pointer
    wire [7:0] pulse_disable_period; //a config input; determines when to ignore VRSPAD pulses
    // (since DAC update introduces noise etc, want to ignore pulses during that time)

    always @(posedge clk) begin
        //incrimenting the phase pointer
        if (phase_pointer == cycle_period) phase_pointer <= 0;
        else 
        phase_pointer <= phase_pointer + 1;

    end


    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //SPAD frequency counters ==========================================================================================================
    wire count_enable; // a cfg input, manually toggled in code
    wire count_reset; //a cfg input, manually toggled in code
    wire count_active;
    assign count_active = count_enable & (phase_pointer > pulse_disable_period);

    reg [31:0] raw_counters[143:0];
    reg [31:0] clked_counters[143:0];
    reg [31:0] count_timer;

    // reg [31:0] flip_counters[143:0];
    // reg [143:0] last_bm_state;

    always @(posedge clk) begin
        if (count_reset) count_timer <= 0;
        else if (count_active) count_timer <= count_timer + 1;
    end
    
    for (i=0; i<144; i=i+1) begin
        always @(posedge clk) begin
            if (count_reset) clked_counters[i] <= 0;
            else if (count_active && spad_pulse_sync[i]) clked_counters[i] <= clked_counters[i] + 1;
        end
        always @(posedge pulse_in[i+1]) begin
            if (count_reset) raw_counters[i] <= 0;
            else if (count_active) raw_counters[i] <= raw_counters[i] + 1; //incriment counter - we get one 8-bit random number on each positive edge
        end    
        // always @(posedge clk) begin
            // if (man_rst) flip_counters[i] <= 0;
            // else if (count_enable && (bm_state[i]^last_bm_state[i])) flip_counters[i] <= flip_counters[i] + 1; //incriment counter - we get one 8-bit random number on each positive edge
        // end    
    end


    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //main BM instantiation:
    //-latches
    //-energy sums
    //-DAC writing
    //all snchronized/controlled by a master phase pointer which indicates when each sum is calculated and sent to the DACs



    //latch parts
    wire [143:0] bm_state;
    wire BM_enable;
    assign BM_enable = (phase_pointer > pulse_disable_period);

    //mostly just settings from the config interface, padded with an extra 1'b1 bit:
    wire [144:0] cuts;

    latch_chain latches(clk, BM_enable, spad_pulse_sync, cuts, bm_state);

    //summation parts - there are 4 pipelined summation units, drawing off of banks of block RAM.
    //the BRAM is written to using a SPI interface that does 147-byte long transfers (one address, one self-index, one bias, and 144 weights)
    wire signed [11:0] group1energy, group2energy, group3energy, group4energy; //outputs for solution checking
    wire [7:0] group1dac, group2dac, group3dac, group4dac; //outputs for threshold writing
    wire [1:0] sum_shift_amnt;
    piplined_energy_calc group1(cs3, mosi, sck, clk, bm_state, phase_pointer, sum_shift_amnt, group1energy, group1dac);
    piplined_energy_calc group2(cs3, mosi, sck, clk, bm_state, phase_pointer+36, sum_shift_amnt, group2energy, group2dac);
    piplined_energy_calc group3(cs3, mosi, sck, clk, bm_state, phase_pointer+72, sum_shift_amnt, group3energy, group3dac);
    piplined_energy_calc group4(cs3, mosi, sck, clk, bm_state, phase_pointer+108, sum_shift_amnt, group4energy, group4dac);

    //not used to program the delay, but just to indicate the pipeline depth for other RTL that needs to be synchronized
    parameter sum_delay = 8; 

    //save energy calcs to a BRAM that can be read by config SPI for diagnostics
    reg [11:0] energy_store[255:0];
    reg [9:0] dac_store[255:0];
    //only save the one.  However, cycle time may be adjusted so that all 144 are eventually written
    always @(posedge clk) energy_store[phase_pointer] <= group1energy;
    always @(posedge clk) dac_store[phase_pointer] <= group1dac; 


    //there are 144 DAC channels to write.  They are split into 4 parallel interfaces, so a full update takes ~36 clock cycles.

    //the sequence of when each DAC channel is programmed is controlled by these program sequence registers:
    reg [36:0] A0_prog, A1_prog, WR_prog;

    //config values - from config SPI
    wire [7:0] DAC_high_byte;
    wire DAC_HBEN;

    //double-buffering registers
    reg [7:0] BUS1_buf, BUS2_buf, BUS3_buf, BUS4_buf;
    reg [1:0] A_buf;


    always @(posedge clk) begin
        //since BM is frozen at phase 0, first valid energy calc starts at phase 1;
        //the calc pipeline delay is 8, so first sum is ready at phase 9.
        //thus, the DAC writing sequence should be initialized at phase 8, so the first transfer to the output regs can happen at phase 9:

        //when DAC counter is set to 0, the program sequences are re-loaded.
        //The program sequences are shifted to the left at each clock cycle, setting new values on the control lines.
        //first write occurs at DAC_counter = 3: WR0 goes low starting at DAC_counter = 1, and stays low for two cycles.
        if (phase_pointer == (sum_delay-1)) begin
            A0_prog <= 37'b0000000000111111111000000000111111111;
            A1_prog <= 37'b0000000000000000000111111111111111111;
            //two zeros in a row means that each WR line will be low for two cycles
            WR_prog <= 37'b1111111100111111100111111100111111100; 
            //synchronously copy config setting to output.  config setting will be manually strobed by code on host computer
            HBEN <= DAC_HBEN;
        end
        else begin 
            //first action of new program initiation reaches output pins at DAC_counter = 1
            A_buf <= {A1_prog[36], A0_prog[36]}; //double buffered to 200 MHz falling edge to provide hold time
            WR <= WR_prog[36:28];

            //program sequences are just shift registers.  Written manually so that 1, not 0, is shifted in
            A0_prog <= {A0_prog[35:0], 1'b1};
            A1_prog <= {A1_prog[35:0], 1'b1};
            WR_prog <= {WR_prog[35:0], 1'b1};
        end

        //setting data bus values.  Only start setting up when DAC_counter = 2 (hence minus 2 offset),
        //since first write stobe (WR rising edge) is at DAC_counter = 3

        //write to BUS buffers; actual write out will be on clk200 negative edge, so that they have a 2.5ns hold time
        if (phase_pointer > (sum_delay) && phase_pointer < sum_delay+36+1 && HBEN == 0) begin
            BUS1_buf <= group1dac;
            BUS2_buf <= group2dac;
            BUS3_buf <= group3dac;
            BUS4_buf <= group4dac; 
        end
        else if (phase_pointer > (sum_delay) && phase_pointer < sum_delay+36+1 && HBEN == 1) begin
            BUS1_buf <= DAC_high_byte;
            BUS2_buf <= DAC_high_byte;
            BUS3_buf <= DAC_high_byte;
            BUS4_buf <= DAC_high_byte;
        end

    end

    always @(negedge clk200) begin
        BUS1 <= BUS1_buf;
        BUS2 <= BUS2_buf;
        BUS3 <= BUS3_buf;
        BUS4 <= BUS4_buf;
        A <= A_buf;
    end

    ///////////////////////////////////////////////////////////////////////////////////////////////////////
    //low-energy checker.
    //records lowest energy and associated state, and periodically freezes the BM to check if current state is new low
    //uses energy sum values to check

    //data used in checker function
    reg [143:0] lowest_energy_state, most_recent_state;
    reg signed [31:0] lowest_energy, current_energy, most_recent_energy;
    reg signed [31:0] current_energy; //since these are signed, we should be able to correctly track negative low energies
    wire rst_low_energy;

    //summation of total energy: is sum of all energy sums where the corresponding BM bit is active.
    //Not exactly the energy (double counts connections)
    //but is monotonic with actual energy, so is a sufficient statistic.

    always @(posedge clk) begin
        //initialize cumulative sum to zero
        if (phase_pointer == (sum_delay-1))
            current_energy <= 0; 
        //36 rounds of accumulation
        else if (phase_pointer > (sum_delay) && phase_pointer < (sum_delay+1+36))
            current_energy <= current_energy + group1energy + group2energy + group3energy + group4energy;
        //checking against current best energy:
        else if (phase_pointer == sum_delay+1+36 && current_energy < lowest_energy) begin
            lowest_energy <= current_energy;
            lowest_energy_state <= bm_state;
        end
        //reset lowest energy marker if a config bit is set:
        else if (phase_pointer == sum_delay+2+36 && rst_low_energy)
            lowest_energy <= {1'b0, {31{1'b1}}};
        else if (phase_pointer == sum_delay+3+36) begin
            most_recent_energy <= current_energy;
            most_recent_state <= bm_state;
        end

    end


    ///////////////////////////////////////////////////////////////////////////////////////////////
    //bolzmann machine state readout SPI
    reg [143:0] bm_state_scan_copy;
    wire [1:0] bm_read_mode; //set in config SPI.  A 0 reads current state, a 1 reads lowest energy state, and
    // 2 returns the cuts setting (for testing readout functionality)
    
    //pointer state for serialization
    reg [7:0] bm_miso_bit_counter;
    always @(posedge sck, posedge cs4) begin
        if (cs4) bm_miso_bit_counter <= 143; //reset to highest bit
        else bm_miso_bit_counter <= bm_miso_bit_counter-1; //MSB is shifted out first; so bit counter decrements
    end

    wire bm_state_miso;
    assign bm_state_miso = bm_state_scan_copy[bm_miso_bit_counter];

    always @(negedge cs4) begin
        case (bm_read_mode)
            2'b00: bm_state_scan_copy <= most_recent_state;
            2'b01: bm_state_scan_copy <= lowest_energy_state;
            2'b10: bm_state_scan_copy <= cuts[144:1]; //for testing
            2'b11: bm_state_scan_copy <= {{72{1'b1}}, {72{1'b0}}}; //also just for testing
        endcase
    end

    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //multifunction SPI interface: all transfers are 4 bytes ===============================================================================
    //input register:  one byte not used
    reg [31:0] scan_in_bits;
    wire [7:0] cmd;
    wire [7:0] addr;
    wire [7:0] data;
    assign cmd = scan_in_bits[31:24];
    assign addr = scan_in_bits[23:16];
    assign data = scan_in_bits[15:8];
    
    //scan chain for scan_in_bits
    //syntax note:  line ends only at semicolon; no begin / end are needed since there is only one action inside each block
    always @(posedge sck)
        if (~cs2) scan_in_bits <= {scan_in_bits[30:0], mosi};//scan_in_bits[0] <= mosi;



    //output register:  content of output reg set at the end of the preceding transfer.
    reg [31:0] out_bits;
    reg [5:0] miso_bit_counter;
    wire multifunction_miso;
    assign multifunction_miso = out_bits[miso_bit_counter];

    //pointer state for serialization
    always @(posedge sck, posedge cs2) begin
        if (cs2) miso_bit_counter <= 31; //reset to highest bit
        else miso_bit_counter <= miso_bit_counter-1; //MSB is shifted out first; so bit counter decrements
    end

    
    //256 8-bit config registers
    reg [7:0] cfg_regs [255:0];

    //end-of-transfer action:
    always @(posedge cs2) begin
        case (cmd)
            1: cfg_regs[addr] <= data; //writes to configuration bytes
            2: out_bits <= {{24{1'b0}},cfg_regs[addr]}; //read a configuration byte
            3: out_bits <= clked_counters[addr]; //returns rate counter info on next transfer
            4: out_bits <= raw_counters[addr];
            5: out_bits <= count_timer;
            6: out_bits <= {{20{1'b0}}, energy_store[addr]}; //reads calculated sums.  must be mapped - addr is not VRSPAD channel #
            7: out_bits <= {{24{1'b0}}, dac_store[addr]}; //reads calculated sums.  must be mapped - addr is not VRSPAD channel #
            8: out_bits <= lowest_energy;
            9: out_bits <= most_recent_energy;
        endcase
        // if (cmd == 1) cfg_regs[addr] <= data; //writes to configuration bytes
        // if (cmd == 2) out_bits <= {{24{1'b0}},cfg_regs[addr]}; //read a configuration byte
        // if (cmd == 3) out_bits <= clked_counters[addr]; //returns rate counter info on next transfer
        // if (cmd == 4) out_bits <= raw_counters[addr];
        // if (cmd == 5) out_bits <= count_timer;
        // if (cmd == 6) out_bits <= {{20{1'b0}}, energy_store[addr]}; //reads calculated sums.  must be mapped - addr is not VRSPAD channel #
        // if (cmd == 7) out_bits <= {{24{1'b0}}, dac_store[addr]}; //reads calculated sums.  must be mapped - addr is not VRSPAD channel #
        // if (cmd == 8) out_bits <= lowest_energy;
        // if (cmd == 9) out_bits <= current_energy;
    end

    //assign config bits to more descriptive names
    assign count_enable = cfg_regs[0][0]; //when high, the SPAD rate counters are functioning
    assign count_reset = cfg_regs[0][1]; //when high, the SPAD rate counters are reset to zero
    assign led = cfg_regs[2]; //output to genesys2 leds - does not do anything, simple visual check that slave SPI is working
    assign DAC_high_byte = cfg_regs[4]; //used to program offset from ground for comparator thresholds. values of 0, 1, 2, or 3
    assign DAC_HBEN = cfg_regs[5][0]; //pulsed briefly to write DAC high byte to all DACs
    assign cycle_period = cfg_regs[6]; //controls the amount of time between DAC update cycles
    assign pulse_disable_period = cfg_regs[7]; //controls when the input pulses are gated (to avoid DAC write noise)
    assign sum_shift_amnt = cfg_regs[8][1:0]; //controls magnitude adjustment during energy sum calculation
    assign bm_read_mode = cfg_regs[9][1:0]; //sets what gets read out when the BM SPI is used.  Sort of like a fixed cmd byte for another SPI
    assign rst_low_energy = cfg_regs[10][0]; //when set, the low energy sum is set to its maximum value
    //latch cut: specifies whether or not adjacent VRSPADs combine in a mutually exclusive latch or not
    assign cuts = { cfg_regs[117],
                    cfg_regs[116],
                    cfg_regs[115],
                    cfg_regs[114],
                    cfg_regs[113],
                    cfg_regs[112],
                    cfg_regs[111],
                    cfg_regs[110],
                    cfg_regs[109],
                    cfg_regs[108],
                    cfg_regs[107], 
                    cfg_regs[106], 
                    cfg_regs[105], 
                    cfg_regs[104], 
                    cfg_regs[103], 
                    cfg_regs[102], 
                    cfg_regs[101], 
                    cfg_regs[100], 
                    1'b1};

    
    ////////////////////////////////////////////////////////////////////////////////
    //switch between MISO sources depending on chip select:
    always @(*) begin
        case({cs2, cs3, cs4, cs5})
            4'b0111: miso = multifunction_miso;
            // 4'b1011: miso = weights_miso;
            4'b1101: miso = bm_state_miso;
            default: miso = 1'bz;
        endcase
    end

endmodule