create_project -in_memory -part xcu250-figd2104-2-e

read_verilog -sv /home/miner/users/shanie/xconnect/ZooKing/barrel_shifter/design/barrel_shifter.v

# -- [COMPILE] ----------------------------------------------------------------

read_xdc -mode out_of_context constraints_bs_1.xdc
synth_design -top barrel_shifter -mode out_of_context -directive sdx_optimization_effort_high
write_checkpoint -force ./post_synth.dcp
report_utilization -file post_synth_util.txt

# -----------------------------------------------------------------------------
