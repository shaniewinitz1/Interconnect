// +FHDR-----------------------------------------------------------------------
// FILE NAME : xconnect.v
// AUTHOR : Shanie Winitz
// PURPOSE : interconnect.
// Clock Domains :
// Other :
// -FHDR-----------------------------------------------------------------------

module xconnect #(
    parameter WORD_SIZE = 256,
    parameter NOF_PES = 16,
    parameter NOF_LEVELS = $clog2(NOF_PES), // localparam NOF_LEVELS = $clog2(NOF_PES);
    parameter GROUP_SIZE_WIDTH = NOF_LEVELS + 1
    ) (
    input                                           clk,
    input                                           rst,
    input       [WORD_SIZE * NOF_PES - 1:0]         input_pes_data,
    input       [GROUP_SIZE_WIDTH * NOF_PES - 1:0]  groups_sizes,
    output reg  [WORD_SIZE * NOF_PES - 1:0]         output_pes_data
    );    
    reg [WORD_SIZE-1:0]         levels_input_data   [NOF_LEVELS:0][NOF_PES - 1:0];
    reg [GROUP_SIZE_WIDTH-1:0]  group_size          [0:NOF_PES-1];
    reg [NOF_LEVELS-1:0]        in_out_counter;
    reg [NOF_LEVELS-1:0]        in_out_reverse_counter;
    reg [NOF_LEVELS-1:0]        levels_mask         [0:NOF_PES-1];

    //generate counter
    always @(posedge clk) begin
        in_out_counter <= rst ?  NOF_PES - 1 : in_out_counter + 1;
    end

    //generate input, reversed counter
    integer pe_idx;
    integer level_idx;
    always @(*) begin
        for (pe_idx=0; pe_idx<NOF_PES; pe_idx = pe_idx + 1) begin
            levels_input_data[0][NOF_PES-1-pe_idx] = input_pes_data[WORD_SIZE * pe_idx +:WORD_SIZE];
            group_size[NOF_PES-1-pe_idx] = groups_sizes[GROUP_SIZE_WIDTH * pe_idx +:GROUP_SIZE_WIDTH];
            levels_mask[pe_idx] = ~((NOF_PES/group_size[pe_idx])-1);
        end
        for (level_idx = 0; level_idx < NOF_LEVELS; level_idx = level_idx+1) begin
            in_out_reverse_counter[level_idx] = in_out_counter[NOF_LEVELS-1-level_idx];

        end
    end

    //swaps
    integer slice_idx;
    reg [NOF_PES-1:0] in_out_swap;
    reg [NOF_LEVELS:0] swap_size;
    reg [NOF_PES-1:0] swap_forward;
    always @(*) begin
        for (level_idx=0; level_idx<NOF_LEVELS; level_idx = level_idx+1) begin
            swap_size = (1 << level_idx);
            for (slice_idx = 0; slice_idx < NOF_PES; slice_idx = slice_idx + 1) begin 
                in_out_swap[slice_idx] = ((in_out_reverse_counter &(levels_mask[slice_idx])) >> level_idx) & 1'h1;
                swap_forward[slice_idx] = ((slice_idx % (1 << (level_idx + 1))) < swap_size);
                levels_input_data[level_idx+1][slice_idx] = in_out_swap[slice_idx] ? (swap_forward[slice_idx] ? levels_input_data[level_idx][slice_idx + swap_size]:levels_input_data[level_idx][slice_idx - swap_size] )
                                                            : levels_input_data[level_idx][slice_idx];
            end
        end
    end

    //output
    always @(posedge clk) begin
        for (pe_idx=0; pe_idx<NOF_PES; pe_idx = pe_idx + 1) begin
            output_pes_data[WORD_SIZE * pe_idx +:WORD_SIZE] <= levels_input_data[NOF_LEVELS][NOF_PES-1-pe_idx];
        end
    end

endmodule