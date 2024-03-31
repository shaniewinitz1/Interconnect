create_project -in_memory -part xcu250-figd2104-2-e

read_verilog -sv /home/miner/users/shanie/xconnect/ZooKing/xconnect_top/design/xconnect_top.v

# -- [COMPILE] ----------------------------------------------------------------

read_xdc -mode out_of_context constraints_top_1.xdc
synth_design -top xconnect_top -mode out_of_context -directive sdx_optimization_effort_high
write_checkpoint -force ./post_synth.dcp
report_utilization -file post_synth_util.txt

# -----------------------------------------------------------------------------
