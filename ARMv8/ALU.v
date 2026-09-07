`define AND   4'b0000  // These defines are not required but may be helpful.
`define OR    4'b0001
`define ADD   4'b0010
`define SUB   4'b0110
`define PassB 4'b0111


module ALU(  //module and inputs
    output reg [63:0] BusW,
    input      [63:0] BusA,
    input      [63:0] BusB,
    input      [3:0]  ALUCtrl,
    output            Zero
);
    always @(*)  //triggers on any change
    begin
        case(ALUCtrl) //depending on the ALUCtrl
            `AND:
                BusW = BusA & BusB; //if 0000 then you and
            `OR:
                BusW = BusA | BusB; //if 0001 then you or
            `ADD:
                BusW = BusA + BusB; //if 0010 then you add
            `SUB:
                BusW = BusA - BusB; //if 0110 then you subtract
            `PassB:
                BusW = BusB; //if 0111 then you just pass BusB
            default:
                BusW = 64'b0; // if it is none of the above it just passes 0
        endcase
    end
    assign Zero = (BusW == 64'b0); //if the output is 0 then you set Zero to 1
endmodule