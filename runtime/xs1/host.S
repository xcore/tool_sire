// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

  .text
  .globl runProcess, "f{0}(si,&(a(:ui)),si)"

/*============================================================================
  Run a process

  NOTE: a maximum of MAX_PROC_PARAMETERS arguments can be used, but this code
  must be modified manually. 

  Signature:
    void runProcess(int procIndex, unsigned int args[], int numArgs);
  
  Parameters:
    r0: int procIndex
    r1: unsigned int args[]
    r2: int numArgs

  Stack:
    sp[0]: lr
    sp[1]: arg1
    sp[2]: arg2
    sp[3]: arg3
    sp[4]: arg4
    sp[5]: arg5
    sp[6]: arg6
    sp[7]: r8
    sp[8]: r9
    sp[9]: r10
  ==========================================================================*/
  .cc_top runProcess.function, runProcess
  .align 2
runProcess:

  entsp 10
  stw r8,  sp[7]
  stw r9,  sp[8]
  stw r10, sp[9]
 
  /* Load args 5,6,7,8,9,10 into sp[1,2,3,4,5,6] */
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
  
  /* Load args 1,2,3,4 into r0,r1,r2,r3 */
  ldw r0, r11[0]
  ldw r1, r11[1]
  ldw r2, r11[2]
  ldw r3, r11[3]

  /* Load the address of the procedure and call it */
  ldaw r11, cp[0]
  ldw r10, r11[r10]
  bla r10

  ldw r8,  sp[7]
  ldw r9,  sp[8]
  ldw r10, sp[9]
  retsp 10

  .cc_bottom runProcess.function

