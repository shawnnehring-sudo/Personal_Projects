module NextPClogic( //module and inputs
    output reg [63:0] NextPC,
    input  [63:0] CurrentPC,
    input  [63:0] SignExtImm64,
    input         Branch,
    input         ALUZero,
    input         Uncondbranch
);
    always @(*) //trigger on all
    begin
        if((ALUZero & Branch) | Uncondbranch) //if branch or gate outputs 1
            NextPC = CurrentPC + SignExtImm64; //do the branch
        else
            NextPC = CurrentPC + 64'h4; //otherwise just add 4 to the next instruction
    end
endmodule