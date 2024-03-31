////////////////////////////////////////
///Cyclic Barrel Shifter
///////////////////////////////////////

// +FHDR-----------------------------------------------------------------------
// FILE NAME : barrel_shifter.v
// AUTHOR : Shanie Winitz
// PURPOSE : Cyclic Barrel Shifter.
// Clock Domains :
// Other :
// -FHDR-----------------------------------------------------------------------


module barrel_shifter #(
    parameter WORD_SIZE = 256,
    parameter NOF_PES = 16,
    parameter NOF_LEVELS = $clog2(NOF_PES) // localparam NOF_LEVELS = $clog2(NOF_PES);
    )(
    input                                   clk,
    input                                   rst,
    input       [WORD_SIZE * NOF_PES -1:0]  in,
    output      [WORD_SIZE * NOF_PES -1:0]  out

    );

    reg [NOF_LEVELS-1:0]            counter;
    wire [2 * WORD_SIZE * NOF_PES -1:0]  temp;


    //generate counter
    always @(posedge clk) begin
        counter <= rst ? 0 : counter + 1;
    end

    assign temp = {in,in};
    assign out = temp[counter * WORD_SIZE +: NOF_PES * WORD_SIZE];

endmodule

