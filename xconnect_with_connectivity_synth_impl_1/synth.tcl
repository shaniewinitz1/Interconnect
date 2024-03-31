create_project -in_memory -part xcu250-figd2104-2-e

read_verilog -sv /home/miner/users/shanie/xconnect/ZooKing/xconnect_with_connectivity_inputs/design/xconnect.v

# -- [COMPILE] ----------------------------------------------------------------

read_xdc -mode out_of_context constraints_w_connectivity_1.xdc
synth_design -top xconnect -mode out_of_context -directive sdx_optimization_effort_high
write_checkpoint -force ./post_synth.dcp
report_utilization -file post_synth_util.txt

# -----------------------------------------------------------------------------
