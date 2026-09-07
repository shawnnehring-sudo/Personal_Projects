`timescale 1ns/1ps  //timescale for the test bench

module RegisterFile(
    output wire [63:0] BusA, //output from data of register A
    output wire [63:0] BusB, //output from data of register B
    input  wire [63:0] BusW, //input for the writing data
    input  wire [4:0]  RA,  //input register A to read
    input  wire [4:0]  RB,  //input register B to read
    input  wire [4:0]  RW,  //input register to be written
    input  wire RegWr,  //enables writing
    input  wire Clk  //clock
);
reg [63:0] registers [30:0]; //creates 32 registers of 64 bits
assign #3 BusA = (RA == 5'd31) ? 64'b0 : registers[RA];  //if the register isnt XZR then but the BusA in RA or but all 0s
assign #3 BusB = (RB == 5'd31) ? 64'b0 : registers[RB];  //if the register isnt XZR then but the BusB in RB or but all 0s

always @(posedge Clk) //trigger on positive edge of clock
begin //begins always block
    if (RegWr && (RW != 5'd31)) //if the writing is enables and the register is XZR then write the data
            registers[RW] <= BusW;  //writes the data
end //ends always block

endmodule //end module