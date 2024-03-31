create_project -in_memory -part xcu250-figd2104-2-e
set_property source_mgmt_mode All [current_project]

open_checkpoint ./post_synth.dcp
# read_checkpoint -cell user_partition ./post_synth.dcp

# read_xdc ${script_path}/floorplan.xdc

opt_design -directive Explore
report_utilization -hierarchical -file post_opt_util.txt
report_timing_summary -max_paths 10 -file post_opt_timing.txt
place_design -directive Auto_1
phys_opt_design -directive Explore
write_checkpoint -force post_place.dcp
report_utilization -hierarchical -file post_place_util.txt
report_timing_summary -max_paths 10 -file post_place_timing.txt
route_design -directive AggressiveExplore
phys_opt_design -directive Explore
write_checkpoint -force post_route.dcp
report_utilization -hierarchical  -file post_route_util.txt
report_timing_summary -max_paths 10 -file post_route_timing.txt
report_power -file post_route_power.txt
write_debug_probes -force debug.ltx
# write_bitstream -cell user_partition -bin_file -force user.bit
