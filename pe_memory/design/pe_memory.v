// +FHDR-----------------------------------------------------------------------
// FILE NAME : pe_memory.v
// AUTHOR : Shanie Winitz
// PURPOSE :
// Clock Domains :
// Other :
// -FHDR-----------------------------------------------------------------------

module pe_memory #(
    parameter WORD_SIZE = 256,
    parameter NOF_PES = 16,
    parameter NOF_LEVELS = $clog2(NOF_PES),
    parameter GROUP_SIZE_WIDTH = NOF_LEVELS + 1
    // parameter GROUP_SIZE_WIDTH = 5
    ) (
    input                               clk,
    input                               rst,
    input       [WORD_SIZE-1:0]         input_data,
    input       [NOF_LEVELS-1:0]        src_pe_index,
    input       [NOF_LEVELS-1:0]        dest_pe_index,
    output reg  [WORD_SIZE-1:0]         output_data,
    output reg  [GROUP_SIZE_WIDTH-1:0]  output_pe_group_size
    );

    reg [GROUP_SIZE_WIDTH-1:0]     pe_group_size[0:1];

    reg [WORD_SIZE-1:0]     in_mem_data     [0:NOF_PES-1]; 
    reg [WORD_SIZE-1:0]     out_mem_data    [0:NOF_PES-1]; //random data, writen in the beginning of the test using veri.force_mem

    integer i;
    initial for (i = 0; i < NOF_PES; i = i+1) out_mem_data[i] <= #1 i+256'd10;


    always@(*) begin
        output_pe_group_size        = pe_group_size[0];
        output_data                 = out_mem_data[dest_pe_index];
        in_mem_data[src_pe_index]   = input_data;
    end
    
endmodule