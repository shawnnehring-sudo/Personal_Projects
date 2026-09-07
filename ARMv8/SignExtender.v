`define Itype   3'b000  // These defines are not required but may be helpful.
`define Dtype    3'b001
`define CBtype   3'b010
`define Btype   3'b011
`define IMtype  3'b100


module SignExtender( //module and inputs
    output reg [63:0] SignExOut,
    input      [25:0] Instruction,
    input      [2:0]  SignOp
);
always @(*)
begin
    case(SignOp)  //the different types of sign extension
        `Itype:
            SignExOut = {52'b0,Instruction[21:10]};  //zero extend from 12 bits for I type
        `Dtype:
            SignExOut = {{55{Instruction[20]}},Instruction[20:12]}; //sign extend from 9 bits for D type
        `CBtype:
            SignExOut = {{43{Instruction[23]}},Instruction[23:5], 2'b00}; //sign extend from 19 bits for CB type
        `Btype:
            SignExOut = {{36{Instruction[25]}},Instruction[25:0], 2'b00}; //sign extend from 26 bits for B type
        `IMtype:
            case(Instruction[22:21])
            2'b00:
                SignExOut = {48'b0,Instruction[20:5]};
            2'b01:
                SignExOut = {32'b0,Instruction[20:5], 16'b0};
            2'b10:
                SignExOut = {16'b0,Instruction[20:5], 32'b0};
            2'b11:
                SignExOut = {Instruction[20:5], 48'b0};
            default:
                SignExOut = 64'b0;
            endcase
        default:
            SignExOut = 64'b0;  //default set the sign extend to 0 
    endcase //we done
end
endmodule