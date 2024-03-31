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
reg  clk;
reg  rst;
reg rst_n;

always begin
    clk=0;
    #10;
    clk=1;
    #3;
    $python("negedge()");
    #7;
end
initial begin
    $dumpvars(0,tb);
    clk = 0;
    rst = 1;
    #100;
    rst = 0;

end
xconnect_top dut (
     .clk(clk)
    ,.rst(rst)
);

reg [1023:0] testname;
initial begin
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
