`define OPCODE_ANDREG 11'b10001010000
`define OPCODE_ORRREG 11'b10101010000
`define OPCODE_ADDREG 11'b10001011000
`define OPCODE_SUBREG 11'b11001011000

`define OPCODE_ADDIMM 11'b1001000100?
`define OPCODE_SUBIMM 11'b1101000100?

`define OPCODE_MOVZ   11'b110100101??

`define OPCODE_B      11'b000101?????
`define OPCODE_CBZ    11'b10110100???

`define OPCODE_LDUR   11'b11111000010
`define OPCODE_STUR   11'b11111000000

module SC_Control(
    output reg       Reg2Loc,
    output reg       ALUSrc,
    output reg       MemtoReg,
    output reg       RegWrite,
    output reg       MemRead,
    output reg       MemWrite,
    output reg       Branch,
    output reg       Uncondbranch,
    output reg [3:0] ALUOp,
    output reg [2:0] SignOp,
    input [10:0]     opcode
    );
    
    always @(*)
    begin
        casez(opcode)
        `OPCODE_ANDREG:
            begin
            SignOp = 3'bxxx;
            Reg2Loc = 1'b0;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0000;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b1;
            end


        `OPCODE_ORRREG:
            begin
            SignOp = 3'bxxx;
            Reg2Loc = 1'b0;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0001;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b1;
            end


        `OPCODE_ADDREG:
            begin
            SignOp = 3'bxxx;
            Reg2Loc = 1'b0;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0010;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b1;
            end


        `OPCODE_SUBREG:
            begin
            SignOp = 3'bxxx;
            Reg2Loc = 1'b0;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0110;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b1;
            end


        `OPCODE_ADDIMM:
            begin
            SignOp = 3'b000;
            Reg2Loc = 1'bx;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0010;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b1;
            RegWrite = 1'b1;
            end


        `OPCODE_SUBIMM:
            begin
            SignOp = 3'b000;
            Reg2Loc = 1'bx;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0110;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b1;
            RegWrite = 1'b1;
            end


        `OPCODE_MOVZ: 
            begin
            SignOp = 3'b100;
            Reg2Loc = 1'bx;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0111;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b1;
            RegWrite = 1'b1;
            end


        `OPCODE_B:
            begin
            SignOp = 3'b011;
            Reg2Loc = 1'bx;
            Branch = 1'bx;
            Uncondbranch = 1'b1;
            MemRead = 1'b0;
            ALUOp = 4'bxxxx;
            MemtoReg = 1'bx;
            MemWrite = 1'b0;
            ALUSrc = 1'bx;
            RegWrite = 1'b0;
            end


        `OPCODE_CBZ:
            begin
            SignOp = 3'b010;
            Reg2Loc = 1'b1;
            Branch = 1'b1;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0111;
            MemtoReg = 1'bx;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b0;
            end


        `OPCODE_LDUR:
            begin
            SignOp = 3'b001;
            Reg2Loc = 1'bx;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b1;
            ALUOp = 4'b0010;
            MemtoReg = 1'b1;
            MemWrite = 1'b0;
            ALUSrc = 1'b1;
            RegWrite = 1'b1;
            end


        `OPCODE_STUR:
            begin
            SignOp = 3'b001;
            Reg2Loc = 1'b1;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0010;
            MemtoReg = 1'bx;
            MemWrite = 1'b1;
            ALUSrc = 1'b1;
            RegWrite = 1'b0;
            end
        

        default:
            begin
            SignOp = 3'b000;
            Reg2Loc = 1'b0;
            Branch = 1'b0;
            Uncondbranch = 1'b0;
            MemRead = 1'b0;
            ALUOp = 4'b0000;
            MemtoReg = 1'b0;
            MemWrite = 1'b0;
            ALUSrc = 1'b0;
            RegWrite = 1'b0;
            end
        endcase
    end
endmodule

