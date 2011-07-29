// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"

  .extern touchRegs
  .extern initMemory
  .extern initPointers
  .extern resetChanends
  .extern initThreads
  .extern initChanends
  .extern initPorts
  .extern initConnections
  .extern masterSync
  .extern initMaster
  .extern busyHostHandler
  .extern busyConnHandler
  .extern controlIdle
  
  .extern spawn_master
  .extern conn_master

  .globl main
  .globl _start
  .globl _master,       "f{0}(0)"
  .globl setInterrupts, "f{0}(0)"
  .globl runMain,       "f{0}(ui)"

  .text

/*============================================================================
 * This initialises the execution of thread 0, core 0
 *==========================================================================*/
  .cc_top _master.function, _master 
  .align 2 

main:
_start:
_master:
  
  bl touchRegs
  bl initMemory
  bl initPointers
  bl setupTraps
  bl resetChanends
  bl initThreads
  bl initChanends
  bl initPorts
  bl initConnections
  bl __alloc_libc_hwlock
  bl setInterrupts
  bl masterSync
  
  bl initMain
  bu controlIdle

  .cc_bottom _master.function

/*===========================================================================
 * Set interrupts for the master control thread (thread 0, core 0). This is 
 * for both the spawn channel and the connection channel. Thread 0 on core 0 
 * will always be busy so it will always be interrupted and never in an idle 
 * state.
 *==========================================================================*/
  .cc_top setInterrupts.function, setInterrupts
  .align 2 
   
setInterrupts:
  entsp 2
  stw r11, sp[0]
  stw r10, sp[1]

  /* Set spawn_master event vector = &busyHostHandler
  and Set spawn_master channel mode to interrupts. */
  ldap r11, busyHostHandler
  ldw  r10, dp[spawn_master]
  setv res[r10], r11
  setc res[r10], XS1_SETC_IE_MODE_INTERRUPT
  
  /* Set conn_master event vector = &busyConnHandler
  and Set conn_master channel mode to interrupts. */
  ldap r11, busyConnHandler
  ldw  r10, dp[conn_master]
  setv res[r10], r11
  setc res[r10], XS1_SETC_IE_MODE_INTERRUPT
  
  /* Enable interrupts */
  setsr SR_IEBLE
  
  ldw r11, sp[0]
  ldw r10, sp[1]
  retsp 2

  .cc_bottom setInterrupts.function

/*===========================================================================
 * A wrapper to run the program main so that r0-r3 are preserved properly
 *==========================================================================*/
  .cc_top runMain.function, runMain
  .align 2 
   
runMain:
  entsp 1
  bla r0
  retsp 1

  .cc_bottom runMain.function

