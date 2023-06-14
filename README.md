# ising-potts-with-SPADs-discrete
CMOS compatible Ising and Potts Annealing Using Single-photon Avalanche Diodes: Design files

The proof-of-concept for SPAD Ising and Potts CTMC (continuous-time markov chain) relies on the key files provided here.  There are two sets of files for 16-circuit and 144-circuit implementations of variable rate SPADs; the 144-circuit version was created second, to enable demonstrations of combinatorial problem solving.

For each implementation, there are three groups of files: one for PCB design, one for FPGA logic, and one for data and code. The code runs tests on the physical system specified by the PCB and FPGA design, and saves data results.

For the 16-circuit version, both the code and the FPGA configuration for the system lies entirely on the Zedboard; a Vivado 2020.1 project is provided, which was used to create the Zedboard FPGA configuration. The processor side of the Zedboard was configured to run linux and the PYNQ environment, so data collection and control of the proof-of-concept aparatus was done through a jupyter-notebook running locally on the zedboard (and accessed from a PC over ethernet).

Since the provided jupyter notebook runs in concert with the Zedboard FPGA and the hardware we connect to the FPGA, it cannot be run in its entirety without fully replicating the hardware as well.  However, many intermediate data are saved alongside the notebook, so one may see the interaction between code and results.  

For the 144-circuit version, the FPGA logic was redesigned to expose a SPI interface that could be accessed over a USB connection. Thus the Python code ran directly on a PC.  In addition, the FPGA board (A Digilent Genesys 2) was configured using Vivado 2020.1 in non-project mode, so rather than a Vivado project, regular verilog files and a Vivado TCL script provided.

While many of the scripts still require a connection to the hardware to run correctly, some scripts that only perform data plotting can be run without the hardware.

All experimental data in the paper is drawn from one of the two experimental systems specified here.