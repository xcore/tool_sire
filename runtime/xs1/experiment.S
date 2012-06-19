// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>

  //.globl _memController, "f{0}(ui, ui, ui, ui, ui)"
  .globl _memController
 
  .text

/*
  Stack

  sp[0]
  sp[1] arg 4
  sp[2] r4
  sp[3] r5
  sp[4] r6
  sp[5] r7
  sp[6] r8
  sp[7] r9
  sp[8] r10
*/

  // r0: chanend input
  // r1: chanend begin
  // r2: chanend end
  // r3: int storage
  // sp[1]: (arg 4) unsigned base

  .cc_top _memController.function, _memController
  .align 2 
_memController:
  entsp 9 
  stw r4, sp[2]
  stw r5, sp[3]
  stw r6, sp[4]
  stw r7, sp[5]
  stw r8, sp[6]
  stw r9, sp[7]
  stw r10, sp[8]
  ldw r4, sp[1] // r4 = base
  // r6 = query
  // r7 = index
  // r8 = address
  // r9 = dest
  // r10 = value
 
  ldc r5, 1     // r5 = true
loop:
  bf r5, loopEnd

  in r6, res[r0] // input ? query
  chkct res[r0], XS1_CT_END
  outct res[r0], XS1_CT_END



loopEnd:
  ldw r4, sp[2]
  ldw r5, sp[3]
  ldw r6, sp[4]
  ldw r7, sp[5]
  ldw r8, sp[6]
  ldw r9, sp[7]
  ldw r10, sp[8]
  retsp 9
  .cc_bottom _memController.function

