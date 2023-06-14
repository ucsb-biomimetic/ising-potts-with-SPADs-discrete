#
# NOTE:  typical usage would be "vivado -mode tcl -source <script name>.tcl" 
#
# STEP#0: define output directory area.
#
set outputDir ./vivado_outputs            

set partname xc7k325tffg900-2

set_part $partname

read_checkpoint $outputDir/post_route.dcp

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