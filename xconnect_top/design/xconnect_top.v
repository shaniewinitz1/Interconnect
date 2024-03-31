// +FHDR-----------------------------------------------------------------------
// FILE NAME : xconnect_top.v
// AUTHOR : Shanie Winitz
// PURPOSE :
// Clock Domains :
// Other :
// -FHDR-----------------------------------------------------------------------

`include "/home/miner/users/shanie/xconnect/ZooKing/xconnect_with_connectivity_inputs/design/xconnect.v"
`include "../../pe_memory/design/pe_memory.v"
module xconnect_top #(
    parameter   WORD_SIZE = 256,
    parameter   NOF_PES = 16
    ) (
    input                               clk,
    input                               rst
    );
    
    localparam  NOF_LEVELS = $clog2(NOF_PES);
    localparam  GROUP_SIZE_WIDTH = NOF_LEVELS + 1;

    wire [WORD_SIZE-1:0]         pe2xconnect_data                [NOF_PES - 1:0];
    wire [GROUP_SIZE_WIDTH-1:0]  pe2xconnect_groups_sizes        [NOF_PES - 1:0];
    reg  [WORD_SIZE-1:0]         xconnect2pe_data                [NOF_PES - 1:0];
    reg  [NOF_LEVELS-1:0]        xconnect2pe_src_connectivity    [NOF_PES - 1:0];
    reg  [NOF_LEVELS-1:0]        xconnect2pe_dest_connectivity   [NOF_PES - 1:0];
    
    reg   [WORD_SIZE * NOF_PES - 1:0]         pe2xconnect_data_bus;
    reg   [GROUP_SIZE_WIDTH * NOF_PES - 1:0]  pe2xconnect_groups_sizes_bus;
    wire  [WORD_SIZE * NOF_PES - 1:0]         xconnect2pe_data_bus;
    wire  [NOF_LEVELS * NOF_PES - 1:0]        xconnect2pe_src_connectivity_bus;
    wire  [NOF_LEVELS * NOF_PES - 1:0]        xconnect2pe_dest_connectivity_bus;



    //connect pe's interfaces to the bus
    integer pe_idx;
    always @(*) begin
        for (pe_idx=0; pe_idx<NOF_PES; pe_idx = pe_idx + 1) begin
            pe2xconnect_data_bus[WORD_SIZE * pe_idx +:WORD_SIZE] = pe2xconnect_data[NOF_PES-1-pe_idx];
            pe2xconnect_groups_sizes_bus[GROUP_SIZE_WIDTH * pe_idx +:GROUP_SIZE_WIDTH] = pe2xconnect_groups_sizes[NOF_PES-1-pe_idx];
            xconnect2pe_data[NOF_PES-1-pe_idx] = xconnect2pe_data_bus[WORD_SIZE * pe_idx +:WORD_SIZE];
            xconnect2pe_src_connectivity[NOF_PES-1-pe_idx] = xconnect2pe_src_connectivity_bus[NOF_LEVELS * pe_idx +:NOF_LEVELS];
            xconnect2pe_dest_connectivity[NOF_PES-1-pe_idx] = xconnect2pe_dest_connectivity_bus[NOF_LEVELS * pe_idx +:NOF_LEVELS];
        end
    end

    genvar i;

    generate
        for (i=0; i<NOF_PES; i = i+1) begin: pe_memory_i
            pe_memory pe_memory_i(
                    .clk(clk),
                    .rst(rst),
                    .input_data(xconnect2pe_data[i]),
                    .output_data(pe2xconnect_data[i]),
                    .src_pe_index(xconnect2pe_src_connectivity[i]),     //input
                    .dest_pe_index(xconnect2pe_dest_connectivity[i]),   //input
                    .output_pe_group_size(pe2xconnect_groups_sizes[i])  //output
            );
        end
    endgenerate

    xconnect xconnect_i( 
                        .clk(clk),
                        .rst(rst),
                        .input_pes_data(pe2xconnect_data_bus),
                        .groups_sizes(pe2xconnect_groups_sizes_bus),
                        .output_pes_data(xconnect2pe_data_bus),
                        .src_connectivity(xconnect2pe_src_connectivity_bus),
                        .dest_connectivity(xconnect2pe_dest_connectivity_bus)
                        );

    endmodule


