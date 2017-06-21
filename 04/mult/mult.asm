// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

    @R2     // init R2 = 0
    M=0

    @R0     // if R0=0 then R0*R1=0
    D=M
    @END
    D;JEQ

    @R1     // if R1=0 then R0*R1=0
    D=M
    @END
    D;JEQ

    @R1     // avoid to change the value of R1
    D=M
    @i
    M=D

(LOOP)

    @R0     // D=R0
    D=M

    @R2     // R2=R0+ ... (R1 times)
    M=M+D

    @i     // decrease R1 value
    D=M-1   // could've written M=M-1
    M=D

    @END    // break loop
    D;JEQ

    @LOOP
    0;JEQ

(END)
    @END
    0;JMP // unconditional loop to terminate
