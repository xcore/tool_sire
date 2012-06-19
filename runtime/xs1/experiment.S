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
  sp[9] r11
*/

  // r0: chanend input
  // r1: chanend begin
  // r2: chanend end
  // r3: int leafStorage
  // sp[1]: (arg 4) unsigned base

  .cc_top _memController.function, _memController
  .align 2 
_memController:
  entsp 10
  stw r4, sp[2]
  stw r5, sp[3]
  stw r6, sp[4]
  stw r7, sp[5]
  stw r8, sp[6]
  stw r9, sp[7]
  stw r10, sp[8]
  stw r11, sp[9]
  ldw r4, sp[1] // r4 = base
  // r5 = [unused]
  // r6 = query
  // r7 = index
  // r8 = dest
  // r9 = address
  // r10 = value
  // r11 = scratch
 
loop:
  in r6, res[r0] // input ? query
  chkct res[r0], XS1_CT_END
  outct res[r0], XS1_CT_END

  // Get query and index
  shr 
  ldc r11, 0xC
  shl r11, r11, 30 // r11 (INDEX_MASK) = 0xC << 30
  and r7, r6, r11  // r7 (index) = query & INDEX_MASK
  shr r6, r6, 30   // r6 (query) = query >> 30

  // Compute destination and address
  div r8, r7, r3   // r8 (dest) = index / leafStorage
  add r8, r8, 1    // r8 (dest) = dest + 1
  rem r9, r7, r3   // r9 (address) = index % leafStorage
  shl r9, r9, 2    // r9 (address) = address << 2
  add r9, r9, r4   // r9 (address) = address + base

  // Perform read, write or halt
  eq r11, r6, 1
  bt r11, read
  eq r11, r6, 2
  bt r11, write
  eq r11, r6, 3
  bt r11, halt
  b  exit

write:
  // Receive value to write
  in r10, res[r0]
  // Remote write
  // Construct channel id: 
  //   (dest<<16 | CHAN_ID_MEM_ACCESS<<8 | XS1_RES_TYPE_CHANEND)
  shl   r8, r8, 16
  ldc   r11, CHAN_ID_MEM_ACCESS // r11 = CHAN_ID_MEM_ACCESS
  shr   r11, r11, 8             // r11 = r11 << 8
  or    r8, r8, r11             // r8 (dest) = dest | r11
  or    r8, r8, XS1_RES_TYPE_CHANEND // r8 (dest) = dest | XS1_TYPE_CHANEND
  ldw   r11, dp[chan_mem_access]
  setd  res[r11], r8
  outct res[r11], XS1_CT_WRITE4
  out   r11, res[r11]
  out   r9, res[r11]
  out   r10, res[r11]
  outct res[r11], XS1_CT_END
  chkct res[r11], XS1_CT_END
  
  // Return value and close channel
  out r10, res[r0]
  outct res[r0], XS1_CT_END
  chkct res[r0], XS1_CT_END
  b loopEnd

read:
  // Remote read
  // Construct channel id: 
  //   (dest<<16 | CHAN_ID_MEM_ACCESS<<8 | XS1_RES_TYPE_CHANEND)
  shl   r8, r8, 16
  ldc   r11, CHAN_ID_MEM_ACCESS // r11 = CHAN_ID_MEM_ACCESS
  shr   r11, r11, 8             // r11 = r11 << 8
  or    r8, r8, r11             // r8 (dest) = dest | r11
  or    r8, r8, XS1_RES_TYPE_CHANEND // r8 (dest) = dest | XS1_TYPE_CHANEND
  ldw   r11, dp[chan_mem_access]
  setd  res[r11], r8
  outct res[r11], XS1_CT_WRITE4
  out   r11, res[r11]
  out   r9, res[r11]
  outct res[r11], XS1_CT_END
  in    r10, res[r11] 
  chkct res[r11], XS1_CT_END
  
  // Return value and close channel
  out   r10, res[r0]
  outct res[r0], XS1_CT_END
  chkct res[r0], XS1_CT_END
  b loopEnd

halt:
  // begin ! HALT
  outct res[r0], XS1_CT_END
  chkct res[r0], XS1_CT_END
  ldc   r11, 2
  out   r11, res[r0]
  outct res[r0], XS1_CT_END
  chkct res[r0], XS1_CT_END
  // end ? value
  chkct res[r0], XS1_CT_END
  outct res[r0], XS1_CT_END
  in    r11, res[r0]
  chkct res[r0], XS1_CT_END
  outct res[r0], XS1_CT_END
  // running = false
  b exit

loopEnd:
  b loop

exit:
  ldw r4, sp[2]
  ldw r5, sp[3]
  ldw r6, sp[4]
  ldw r7, sp[5]
  ldw r8, sp[6]
  ldw r9, sp[7]
  ldw r10, sp[8]
  ldw r11, sp[9]
  retsp 10
  .cc_bottom _memController.function

