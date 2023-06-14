#
# NOTE:  typical usage would be "vivado -mode tcl -source <script name>.tcl" 
#
# STEP#0: define output directory area.
#
set outputDir ./vivado_outputs            

set partname xc7k325tffg900-2

set_part $partname

#
# STEP#1: setup design sources and constraints
#
read_verilog  [ glob ./hdl/*.v ]
read_xdc ./VRSPAD-144-genesys2.xdc

#
# STEP#2: run synthesis, report utilization and timing estimates, write checkpoint design
#
#directive: was having congestion issues (even though utilization is not high) so added 
#-directive runtimeoptimized (try this sometime maybe)
synth_design -top ising_or_potts -part $partname -retiming -directive runtimeoptimized
write_checkpoint -force $outputDir/post_synth
report_utilization -file $outputDir/synth_util.rpt -hierarchical

# start_gui
# show_schematic [concat [get_cells] [get_ports]]
# write_schematic -format pdf $outputDir/top_synth_rtl_schematic.pdf -orientation landscape
# exit

report_timing_summary -file $outputDir/post_synth_timing_summary.rpt
report_power -file $outputDir/post_synth_power.rpt
#
# STEP#3: run placement and logic optimzation, report utilization and timing estimates, write checkpoint design
#
opt_design -directive RuntimeOptimized
place_design -directive AltSpreadLogic_high
phys_opt_design -directive RuntimeOptimized
write_checkpoint -force $outputDir/post_place
report_timing_summary -file $outputDir/post_place_timing_summary.rpt
#
# STEP#4: run router, report actual utilization and timing, write checkpoint design, run drc, write verilog and xdc out
#
route_design -directive  RuntimeOptimized
write_checkpoint -force $outputDir/post_route
report_timing_summary -file $outputDir/post_route_timing_summary.rpt
report_timing -sort_by group -max_paths 100 -path_type summary -file $outputDir/post_route_timing.rpt
report_clock_utilization -file $outputDir/clock_util.rpt
report_utilization -file $outputDir/post_route_util.rpt
report_power -file $outputDir/post_route_power.rpt
report_drc -file $outputDir/post_imp_drc.rpt
write_verilog -force $outputDir/bft_impl_netlist.v
write_xdc -no_fixed_only -force $outputDir/VRSPAD-144-genesys2_impl.xdc
#
# STEP#5: generate a bitstream
# 
write_bitstream -force $outputDir/VRSPAD-144-genesys2.bit
#
# STEP#6: open vivado HW manager, and load bitstream to genesys2 board
#
# Connect to the Digilent Cable on localhost:3121
open_hw_manager
connect_hw_server -url localhost:3121
# assume there is only one connected target - use that
current_hw_target [get_hw_targets *]
open_hw_target

# Program and Refresh the XC7K325T Device
set Device [lindex [get_hw_devices] 0]
current_hw_device $Device
refresh_hw_device -update_hw_probes false $Device
set_property PROGRAM.FILE $outputDir/VRSPAD-144-genesys2.bit $Device
program_hw_devices $Device
refresh_hw_device $Device

exit