module SingleCycleProc(
		   input	     reset, //Active High
		   input [63:0]	     startpc,
		   output reg [63:0] currentpc,
		   output [63:0]     MemtoRegOut, // this should be
						   // attached to the
						   // output of the
						   // MemtoReg Mux
		   input	     CLK
		   );

   // Next PC connections
   wire [63:0] 			     nextpc;       // The next PC, to be updated on clock cycle

   // Instruction Memory connections
   wire [31:0] 			     instruction;  // The current instruction

   // Parts of instruction
   wire [4:0] 			     rd;            // The destination register
   wire [4:0] 			     rm;            // Operand 1
   wire [4:0] 			     rn;            // Operand 2
   wire [10:0] 			     opcode;

   // Control wires
   wire 			     Reg2Loc;
   wire 			     ALUSrc;
   wire 			     MemtoReg;
   wire 			     RegWrite;
   wire 			     MemRead;
   wire 			     MemWrite;
   wire 			     Branch;
   wire 			     Uncondbranch;
   wire [3:0] 			     ALUop;
   wire [2:0] 			     SignOp;

   // Register file connections
   wire [63:0] 			     regoutA;     // Output A
   wire [63:0] 			     regoutB;     // Output B

   // ALU connections
   wire [63:0] 			     aluout;
   wire 			     zero;

   // Sign Extender connections
   wire [63:0] 			     extimm;

   // ALU input
   wire [63:0]           aluinput;

   //MemtoReg connections
   wire [63:0]           ReadData;

   // PC update logic
   always @(posedge CLK)
     begin
        if (reset)
          currentpc <= #3 startpc;
        else
          currentpc <= #3 nextpc;
     end

   // Parts of instruction
   assign rd = instruction[4:0];
   assign rm = instruction[9:5];
   assign rn = Reg2Loc ? instruction[4:0] : instruction[20:16];
   assign opcode = instruction[31:21];


   InstructionMemory imem(
			  .Data(instruction),
			  .Address(currentpc)
			  );

   SC_Control SingleCycleControl(
		   .Reg2Loc(Reg2Loc),
		   .ALUSrc(ALUSrc),
		   .MemtoReg(MemtoReg),
		   .RegWrite(RegWrite),
		   .MemRead(MemRead),
		   .MemWrite(MemWrite),
		   .Branch(Branch),
		   .Uncondbranch(Uncondbranch),
		   .ALUOp(ALUop),
		   .SignOp(SignOp),
		   .opcode(opcode)
		   );
   
   RegisterFile rf(
       .BusA(regoutA),
       .BusB(regoutB), 
       .BusW(MemtoRegOut), 
       .RA(rm), 
       .RB(rn), 
       .RW(rd), 
       .RegWr(RegWrite), 
       .Clk(CLK) 
        );

   SignExtender se(
       .SignExOut(extimm),
       .Instruction(instruction[25:0]),
       .SignOp(SignOp)
       );

   NextPClogic NPC(
       .NextPC(nextpc),
       .CurrentPC(currentpc),
       .SignExtImm64(extimm),
       .Branch(Branch),
       .ALUZero(zero),
       .Uncondbranch(Uncondbranch)
       );
    
   mux2to1_64 alu_mux(
       .in0(regoutB),
       .in1(extimm),
       .sel(ALUSrc),
       .out(aluinput) 
       );

   ALU alu(
       .BusW(aluout),
       .BusA(regoutA),
       .BusB(aluinput),
       .ALUCtrl(ALUop),
       .Zero(zero)
       );
   
   DataMemory dmem(
       .WriteData(regoutB), 
       .Address(aluout),
       .Clock(CLK),
       .MemoryRead(MemRead),
       .MemoryWrite(MemWrite),
       .ReadData(ReadData)
       ); 
   
   mux2to1_64 RegOut_mux( 
       .in0(aluout),
       .in1(ReadData),
       .sel(MemtoReg),
       .out(MemtoRegOut)
       );




endmodule

