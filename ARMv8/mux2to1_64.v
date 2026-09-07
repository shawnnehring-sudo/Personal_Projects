module mux2to1_64 (  //intialize variables and module name
   input wire [63:0] in0,  // Input 0
   input wire [63:0] in1,  // Input 1
   input wire sel,  // Select signal
   output reg [63:0] out // Output
    ); //end of variables
    always @(*)  //triggers on any change
    begin  //begins block
        case(sel) //the cases for the different states of sel
        1'b0:  //if sel is 0
            out = in0;   //sets output equal to input 0
        1'b1:  //if sel is 1
            out = in1;  //sets output equal to input 1
        endcase  //end case block
    end  //end always block
endmodule  //end module