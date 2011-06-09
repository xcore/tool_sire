// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

  .globl runProcedure, "f{0}(si,&(a(:ui)),si)"

  .text

//==========================================================
// Run procedure
//  r0: int procIndex
//  r1: unsigned int args[]
//  r2: int numArgs
//==========================================================
  .cc_top runProcedure.function, runProcedure
  .align 2
runProcedure:

// NOTE: maximum of 8 arguments can be used

  entsp 8 
  stw r8,  sp[5]
  stw r9,  sp[6]
  stw r10, sp[7]
 
  // Load args 5-n into sp[1]...sp[n]
  ldc r10, 4        // i = 4
  lss r9, r10, r2   // r9 = i < numArgs
  bf  r9, .LrunProc // if (i >= numArgs) runProc
  ldaw r3, sp[0]    // r3 = sp
.LbeginLoop:
  eq r9, r10, r2    // r9 = i == numArgs
  bt r9, .LrunProc  // if (i == numArgs) runProc

  ldw r9, r1[r10]   // r9 = args[i]
  sub r8, r10, 3    // r8 = i - 3
  stw r9, r3[r8]    // sp[i-3] = args[i]
  
  add r10, r10, 1   // i = i + 1
  bu .LbeginLoop

.LrunProc:
  mov r10, r0       // r10 = procIndex
  mov r11, r1       // r11 = args[]
  
  // Load args 1-4 into r0-r3
  ldw r0, r11[0]
  ldw r1, r11[1]
  ldw r2, r11[2]
  ldw r3, r11[3]

  // Load the address of the procedure
  ldaw r11, cp[0]
  ldw r10, r11[r10]
 
  // Branch and link to the procedure
  bla r10

  ldw r8,  sp[5]
  ldw r9,  sp[6]
  ldw r10, sp[7]
  retsp 8

  .cc_bottom runProcedure.function


