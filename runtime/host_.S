    .globl runProcedure, "f{0}(ui,si,si,&(a(:ui)))"

    .text

//==========================================================
// Run procedure
//  r0: unsigned c
//  r1: int threadId
//  r2: int procIndex
//  r3: unsigned int args[]
//==========================================================
    .cc_top runProcedure.function, runProcedure
    .align 2
runProcedure:

    entsp 6
    stw r10, sp[1]
    
    ldaw r11, cp[0]
    ldw r10, r11[r2]
   
    mov r11, r3
    ldw r0, r11[0]
    ldw r1, r11[1]
    ldw r2, r11[2]
    ldw r3, r11[3]
    bla r10

    ldw r10, sp[1]
    retsp 6

    .cc_bottom runProcedure.function


