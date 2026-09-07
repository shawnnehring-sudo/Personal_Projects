`timescale 1ns/1ps

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

module SC_Control_tb;  //start of module
    wire Reg2Loc;
    wire ALUSrc;
    wire MemtoReg;
    wire RegWrite;
    wire MemRead;
    wire MemWrite;
    wire Branch;
    wire Uncondbranch;
    wire [3:0] ALUOp;
    wire [1:0] SignOp;
    reg [10:0] opcode;
    reg e_Reg2Loc;
    reg e_ALUSrc;
    reg e_MemtoReg;
    reg e_RegWrite;
    reg e_MemRead;
    reg e_MemWrite;
    reg e_Branch;
    reg e_Uncondbranch;
    reg [3:0] e_ALUOp;
    reg [1:0] e_SignOp;
    integer errors;
    integer i;
    integer iter;


    SC_Control DUT (  //code to test
        .Reg2Loc(Reg2Loc),
        .ALUSrc(ALUSrc),
        .MemtoReg(MemtoReg),
        .RegWrite(RegWrite),
        .MemRead(MemRead),
        .MemWrite(MemWrite),
        .Branch(Branch),
        .Uncondbranch(Uncondbranch),
        .ALUOp(ALUOp),
        .SignOp(SignOp),
        .opcode(opcode));
    
    function present; //sees if the random is a none seen expression
        input [10:0] opcode;
        begin
            casez(opcode)
                `OPCODE_ANDREG, `OPCODE_ORRREG, `OPCODE_ADDREG, `OPCODE_SUBREG,
                `OPCODE_ADDIMM, `OPCODE_SUBIMM, `OPCODE_MOVZ, `OPCODE_B,
                `OPCODE_CBZ, `OPCODE_LDUR, `OPCODE_STUR: present = 1'b0;
                default: present = 1'b1;
            endcase
        end
    endfunction


    task out_check; //checks outputs
        input e_Reg2Loc;
        input e_ALUSrc;
        input e_MemtoReg;
        input e_RegWrite;
        input e_MemRead;
        input e_MemWrite;
        input e_Branch;
        input e_Uncondbranch;
        input [3:0] e_ALUOp;
        input [1:0] e_SignOp;
    begin
        #1;
        if(e_Reg2Loc !== Reg2Loc) begin
            $display("FAIL: Reg2Loc expected to be %h got %h", e_Reg2Loc, Reg2Loc);
            errors = errors+1;
            end
        if(e_ALUSrc !== ALUSrc) begin
            $display("FAIL: ALUSrc expected to be %h got %h", e_ALUSrc, ALUSrc);
            errors = errors+1;
            end
        if(e_MemtoReg !== MemtoReg) begin
            $display("FAIL: MemtoReg expected to be %h got %h", e_MemtoReg, MemtoReg);
            errors = errors+1;
            end
        if(e_RegWrite !== RegWrite) begin
            $display("FAIL: RegWrite expected to be %h got %h", e_RegWrite, RegWrite);
            errors = errors+1;
            end
        if(e_MemRead !== MemRead) begin
            $display("FAIL: MemRead expected to be %h got %h", e_MemRead, MemRead);
            errors = errors+1;
            end
        if(e_MemWrite !== MemWrite) begin
            $display("FAIL: MemWrite expected to be %h got %h", e_MemWrite, MemWrite);
            errors = errors+1;
            end
        if(e_Branch !== Branch) begin
            $display("FAIL: Branch expected to be %h got %h", e_Branch, Branch);
            errors = errors+1;
            end
        if(e_Uncondbranch !== Uncondbranch) begin
            $display("FAIL: Uncondbranch expected to be %h got %h", e_Uncondbranch, Uncondbranch);
            errors = errors+1;
            end
        if(e_ALUOp !== ALUOp) begin
            $display("FAIL: ALUOp expected to be %h got %h", e_ALUOp, ALUOp);
            errors = errors+1;
            end
        if(e_SignOp !== SignOp) begin
            $display("FAIL: SignOp expected to be %h got %h", e_SignOp, SignOp);
            errors = errors+1;
            end
    end
    endtask

    initial begin  //begins block

        $dumpfile("SC_Control.vcd");  //creates VCD file
        $dumpvars(0, SC_Control_tb);  //what to put in file
        errors = 0;

        opcode = `OPCODE_ANDREG; //AND
        e_SignOp = 2'bxx;
        e_Reg2Loc = 1'b0;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b0;
        e_ALUOp = 4'b0000;
        e_MemtoReg = 1'b0;
        e_MemWrite = 1'b0;
        e_ALUSrc = 1'b0;
        e_RegWrite = 1'b1;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);


        opcode = `OPCODE_ORRREG;  //ORR
        e_SignOp = 2'bxx;
        e_Reg2Loc = 1'b0;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b0;
        e_ALUOp = 4'b0001;
        e_MemtoReg = 1'b0;
        e_MemWrite = 1'b0;
        e_ALUSrc = 1'b0;
        e_RegWrite = 1'b1;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);



        opcode = `OPCODE_ADDREG;  //ADDR
        e_SignOp = 2'bxx;
        e_Reg2Loc = 1'b0;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b0;
        e_ALUOp = 4'b0010;
        e_MemtoReg = 1'b0;
        e_MemWrite = 1'b0;
        e_ALUSrc = 1'b0;
        e_RegWrite = 1'b1;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);



        opcode = `OPCODE_SUBREG;  //SUBR
        e_SignOp = 2'bxx;
        e_Reg2Loc = 1'b0;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b0;
        e_ALUOp = 4'b0110;
        e_MemtoReg = 1'b0;
        e_MemWrite = 1'b0;
        e_ALUSrc = 1'b0;
        e_RegWrite = 1'b1;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);


        for (i = 0; i < 2; i = i + 1)begin
            opcode = {10'b1001000100,i[0]};  //ADDI
            e_SignOp = 2'b00;
            e_Reg2Loc = 1'bx;
            e_Branch = 1'b0;
            e_Uncondbranch = 1'b0;
            e_MemRead = 1'b0;
            e_ALUOp = 4'b0010;
            e_MemtoReg = 1'b0;
            e_MemWrite = 1'b0;
            e_ALUSrc = 1'b1;
            e_RegWrite = 1'b1;
            out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
        end


        for (i = 0; i < 2; i = i + 1)begin
            opcode = {10'b1101000100,i[0]};  //SUBI
            e_SignOp = 2'b00;
            e_Reg2Loc = 1'bx;
            e_Branch = 1'b0;
            e_Uncondbranch = 1'b0;
            e_MemRead = 1'b0;
            e_ALUOp = 4'b0110;
            e_MemtoReg = 1'b0;
            e_MemWrite = 1'b0;
            e_ALUSrc = 1'b1;
            e_RegWrite = 1'b1;
            out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
        end


        for (i = 0; i < 4; i = i + 1)begin
            opcode = {9'b110100101,i[1:0]};  //MOVZ
            e_SignOp = 2'b00;
            e_Reg2Loc = 1'bx;
            e_Branch = 1'b0;
            e_Uncondbranch = 1'b0;
            e_MemRead = 1'b0;
            e_ALUOp = 4'b0111;
            e_MemtoReg = 1'b0;
            e_MemWrite = 1'b0;
            e_ALUSrc = 1'b1;
            e_RegWrite = 1'b1;
            out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
        end


        for (i = 0; i < 32; i = i + 1)begin
            opcode = {6'b000101,i[4:0]}; //Branch
            e_SignOp = 2'b11;
            e_Reg2Loc = 1'bx;
            e_Branch = 1'bx;
            e_Uncondbranch = 1'b1;
            e_MemRead = 1'b0;
            e_ALUOp = 4'bxxxx;
            e_MemtoReg = 1'bx;
            e_MemWrite = 1'b0;
            e_ALUSrc = 1'bx;
            e_RegWrite = 1'b0;
            out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
        end


        for (i = 0; i < 8; i = i + 1)begin
            opcode = {8'b10110100,i[2:0]};  //CBZ
            e_SignOp = 2'b10;
            e_Reg2Loc = 1'b1;
            e_Branch = 1'b1;
            e_Uncondbranch = 1'b0;
            e_MemRead = 1'b0;
            e_ALUOp = 4'b0111;
            e_MemtoReg = 1'bx;
            e_MemWrite = 1'b0;
            e_ALUSrc = 1'b0;
            e_RegWrite = 1'b0;
            out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
        end


        opcode = `OPCODE_LDUR;  //LDUR
        e_SignOp = 2'b01;
        e_Reg2Loc = 1'bx;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b1;
        e_ALUOp = 4'b0010;
        e_MemtoReg = 1'b1;
        e_MemWrite = 1'b0;
        e_ALUSrc = 1'b1;
        e_RegWrite = 1'b1;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);



        opcode = `OPCODE_STUR;  //STUR
        e_SignOp = 2'b01;
        e_Reg2Loc = 1'b1;
        e_Branch = 1'b0;
        e_Uncondbranch = 1'b0;
        e_MemRead = 1'b0;
        e_ALUOp = 4'b0010;
        e_MemtoReg = 1'bx;
        e_MemWrite = 1'b1;
        e_ALUSrc = 1'b1;
        e_RegWrite = 1'b0;
        out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);

        iter = 0;
        while(iter < 10) begin
            opcode = {$random};
            if (present(opcode)) begin
                e_SignOp = 2'b00;
                e_Reg2Loc = 1'b0;
                e_Branch = 1'b0;
                e_Uncondbranch = 1'b0;
                e_MemRead = 1'b0;
                e_ALUOp = 4'b0000;
                e_MemtoReg = 1'b0;
                e_MemWrite = 1'b0;
                e_ALUSrc = 1'b0;
                e_RegWrite = 1'b0;
                out_check(e_Reg2Loc, e_ALUSrc, e_MemtoReg, e_RegWrite, e_MemRead, e_MemWrite, e_Branch, e_Uncondbranch, e_ALUOp, e_SignOp);
                iter = iter+1;
            end
        end
        if (errors == 0) //if no errors
            $display("ALL TESTS PASSED");
        else //if errors
            $display("%0d TESTS FAILED", errors);
        $finish;
    end
endmodule


