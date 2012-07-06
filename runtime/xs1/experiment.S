// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"

  .extern chan_mem_access

  .globl _memController, "f{0}(ui,ui,ui,ui)"
 
  .text

/*
  Stack
  sp[0] lr
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
  // r1: int leafStorage
  // r2: unsigned base0
  // r3: unsigned base

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
  // r4 = chan_mem_access
  // r5 = [scratch]
  // r6 = query
  // r7 = index
  // r8 = dest
  // r9 = address
  // r10 = value
  // r11 = [scratch]

  ldw   r4, dp[chan_mem_access] // r4 = chan_mem_access
 
loop:
  inct  r6, res[r0]  // input ? query
  in    r7, res[r0]  // input ? index
  //chkct res[r0], XS1_CT_END
  //outct res[r0], XS1_CT_END

  // Get query and index
  //ldc   r5, 30
  //ldc   r11, 0x3
  //shl   r11, r11, r5 // r11 (INDEX_MASK) = 0x3 << 30
  //not   r11, r11     // r11 (INDEX_MASK) = not(0x3 << 30) 
  //and   r7, r6, r11  // r7 (index) = query & INDEX_MASK
  //shr   r6, r6, r5   // r6 (query) = query >> 30

  // Compute destination and address
  divs  r8, r7, r1   // r8 (dest) = index / leafStorage
  rems  r9, r7, r1   // r9 (address) = index % leafStorage
  shl   r9, r9, 2    // r9 (address) = address << 2
  eq    r11, r8, 0
  bf    r11, notBase0
  add   r9, r9, r2   // r9 (address) = address + base0
  bu    endAddBase
notBase0:
  add   r9, r9, r3   // r9 (address) = address + base
endAddBase:
  
  // Construct channel id: 
  //   (dest<<16 | CHAN_ID_MEM_ACCESS<<8 | XS1_RES_TYPE_CHANEND)
  shl   r8, r8, 16
  ldc   r11, CHAN_ID_MEM_ACCESS // r11 = CHAN_ID_MEM_ACCESS
  shl   r11, r11, 8             // r11 = r11 << 8
  or    r8, r8, r11             // r8 (dest) = dest | r11
  ldc   r11, XS1_RES_TYPE_CHANEND 
  or    r8, r8, r11             // r8 (dest) = dest | XS1_TYPE_CHANEND

  // Perform read, write or halt
  eq    r11, r6, 3
  bt    r11, read
  eq    r11, r6, 4
  bt    r11, write
  eq    r11, r6, 1
  bt    r11, halt
  bu    exit

read:
  // Remote read
  ldc   r5, XS1_CT_READ4 
  setd  res[r4], r8             // setd(r4, dest)
  outct res[r4], r5             // outct(r4, READ4)
  out   res[r4], r4             // out(r4, r4)
  out   res[r4], r9             // out(r4, address)
  outct res[r4], XS1_CT_END     // outct(r4, CT_END)
  in    r10, res[r4]            // in(r4, value)
  chkct res[r4], XS1_CT_END     // chkct(r4, CT_END)
  
  // Return value and close channel
  out   res[r0], r10             // out(input, value)
  //outct res[r0], XS1_CT_END      // outct(input, CT_END)
  //chkct res[r0], XS1_CT_END      // chkct(input, CT_END)
  bu loopEnd

write:
  // Receive value to write
  in r10, res[r0]
  // Remote write
  ldc   r5, XS1_CT_WRITE4 
  setd  res[r4], r8            // setd(r4, dest)
  outct res[r4], r5            // outct(r4, WRITE4)
  out   res[r4], r4            // out(r4, r4)
  out   res[r4], r9            // out(r4, address)
  out   res[r4], r10           // out(r4, value)
  outct res[r4], XS1_CT_END    // outct(r4, CT_END)
  chkct res[r4], XS1_CT_END    // chkct(r4, CT_END)
  
  // Synchronise with writer and close channel
  outct res[r0], XS1_CT_END     // outct(input, CT_END)
  //chkct res[r0], XS1_CT_END     // chkct(input, CT_END)
  bu loopEnd

halt:
  bu exit

loopEnd:
  bu loop

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

