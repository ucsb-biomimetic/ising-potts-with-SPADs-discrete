# ising-potts-with-SPADs-discrete
CMOS compatible Ising and Potts Annealing Using Single-photon Avalanche Diodes: Design files

The proof-of-concept for SPAD Ising and Potts CTMC (continuous-time markov chain) relies on the key files provided here.  The physical system consists of a Zedboard and custom PCBs, for which design files are included.  Software/firmware for the system lies entirely on the Zedboard; a Vivado 2020.1 project is provided, which was used to create the Zedboard FPGA configuration. The processor side of the Zedboard was configured to run linux and the PYNQ environment, so data collection and control of the proof-of-concept aparatus was done through a jupyter-notebook running locally on the zedboard (and accessed from a PC over ethernet).

Since the provided jupyter notebook runs in concert with the Zedboard FPGA and the hardware we connect to the FPGA, it cannot be run in its entirety without fully replicating the hardware as well.  However, many intermediate data are saved alongside the notebook, so one may see the interaction between code and results.  All experimental data in the paper is drawn from the data shared here.
