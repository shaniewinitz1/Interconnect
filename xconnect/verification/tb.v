`timescale 1ns/1ps
module tb;
integer    cycles;   initial cycles=0;
integer    errors;   initial errors=0;
integer    wrongs;   initial wrongs=0;
integer    panics;   initial panics=0;
integer    corrects; initial corrects=0;
reg [31:0] marker;   initial marker=0;
reg [31:0] marker0;   initial marker0=0;
reg [31:0] marker1;   initial marker1=0;
reg [31:0] marker2;   initial marker2=0;
reg [31:0] marker3;   initial marker3=0;
reg [31:0] Index;   initial Index=0;
reg [31:0] ID;   initial ID=0;
parameter WORD_SIZE = 256;
parameter NOF_PES = 16;
parameter NOF_LEVELS = $clog2(NOF_PES);
parameter GROUP_SIZE_WIDTH = NOF_LEVELS + 1;

reg                                         clk;
reg                                         rst;
reg  [((WORD_SIZE * NOF_PES) - 1):0]        input_pes_data;
reg  [((GROUP_SIZE_WIDTH * NOF_PES) - 1):0] groups_sizes;
wire [((WORD_SIZE * NOF_PES) - 1):0]        output_pes_data;
wire [(NOF_LEVELS-1):0]                     xconnect_counter;
wire [((NOF_LEVELS * NOF_PES) - 1):0]       src_connectivity;
wire [((NOF_LEVELS * NOF_PES) - 1):0]       dest_connectivity;


always begin
    clk=0;
    #10;
    clk=1;
    #1;
    $python("negedge()"); // calls python
    #2
    // $python("negedge()"); // calls python
    #7;
end
initial begin
    $dumpvars(0,tb); //saves waves - iverilog creates the waves. $dumpvars(0 = all levels under tb. can select how many levels , the path)
    rst = 1;
    clk = 0;
    input_pes_data = 0;
    groups_sizes = 0;
    #100;
    rst = 0;
end
xconnect #(
    .WORD_SIZE(WORD_SIZE),
    .NOF_PES(NOF_PES),
    .NOF_LEVELS(NOF_LEVELS),
    .GROUP_SIZE_WIDTH(GROUP_SIZE_WIDTH)
    ) dut (
    .clk(clk)
    ,.rst(rst)
    ,.input_pes_data(input_pes_data[((WORD_SIZE * NOF_PES) - 1):0])
    ,.output_pes_data(output_pes_data[((WORD_SIZE * NOF_PES) - 1):0])
    ,.groups_sizes(groups_sizes[((GROUP_SIZE_WIDTH * NOF_PES) - 1):0])
    ,.src_connectivity(src_connectivity[((NOF_LEVELS * NOF_PES) - 1):0])
    ,.dest_connectivity(dest_connectivity[((NOF_LEVELS * NOF_PES) - 1):0])
);

reg [1023:0] testname;
initial begin
    if ($value$plusargs("VERILOGPY=%s",testname)) begin 
        $basemodule(testname);
    end 
    
    $display(" Starting...");
    if ($value$plusargs("LOG=%s",testname)) begin 
        $python("pymonname()",testname);
    end 


    if ($value$plusargs("SEQ=%s",testname)) begin 
         $display(" Running SEQ= %s.",testname); 
    end else begin
        testname = 0;
        $display(" default test");
    end 
    #10;
    if (testname!=0) $python("sequence()",testname);
end 
endmodule


module inout_driver ( inout io , input dflt );

reg val; initial val=0;
reg drive; initial drive=0;
assign io = drive ? val : 1'bz;
assign (pull1,pull0) io = dflt;

endmodule
