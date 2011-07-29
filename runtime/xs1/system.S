// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"

  .extern host
  .extern setHost
  .extern spawnHost
  .extern runThread
  .extern controlIdle
  .extern controlYeild
  .extern releaseThread
  .extern raiseException
  .extern connHandler

  .extern spawn_master
  .extern conn_master
  .extern _sp

  .globl exceptionHandler
  .globl idleHostHandler
  .globl busyHostHandler
  .globl idleConnHandler
  .globl busyConnHandler
  .globl initPointers
  .globl touchRegs
  .globl setupTraps
  .globl initThread

  /* Set heap labels */
  .globl _bheap
  .globl _eheap
  .linkset _bheap, _edp.bss 
  .linkset _eheap, RAM_BASE+RAM_SIZE-(KERNEL_SPACE+(MAX_THREADS*THREAD_STACK_SPACE))

  .text

/*============================================================================
 * Exception/interrupt handler (KEP)
 * NOTE: THIS MUST BE LINKED AT THE BEGINNING OF THE BINARY.
 *==========================================================================*/
  .cc_top exceptionHandler.function, exceptionHandler
  
  /* Force the KEP to align on byte 64 */
  //nop 
  .align 128
exceptionHandler:

  clre
  waiteu

  .cc_bottom exceptionHandler.function

/*============================================================================
 * Idle host handler: receives an event on master spawn channel, sets the host
 * and then runs the incoming closure on this thread.
 *==========================================================================*/
  .cc_top idleHostHandler.function, idleHostHandler
  .align 2
idleHostHandler:
   
  kentsp 6
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw lr,  sp[4]

/* Spawn a new host thread and return to being idle (explicitly as this was
   an event - not saving the pc) */
  bl spawnHost
  ldap r11, controlIdle
  stw r11, sp[1] // spc = &idle
  bu .L.idle.exit

/* Run the process on (this) thead 0 and move to 'busy' state. */
.L.idle.run:
  /* NOTE: the control thread (0) is reserved so we cannot run any workers on
   * it. Raise an exception. */
  ldc r0, et_INSUFFICIENT_THREADS
  ldc r11, 0
  ecallf r11
  
  /* Set the host connection up with this thread */
  bl setHost
  stw r0, sp[5]  // r0 = senderId 
  
  /* Set pc to runThread function (r0 arg = senderId) */
  ldap r11, runThread
  stw r11, sp[1]

  /* Set lr = &controlYeild */
  ldap r11, controlYeild
  stw r11, sp[4]

  /* Set spawn_master event vector = &busyHostHandler */
  ldap r11, busyHostHandler
  ldw  r10, dp[spawn_master]
  setv res[r10], r11
  
  /* Set spawn_master channel mode to interrupts */
  setc res[r10], XS1_SETC_IE_MODE_INTERRUPT
  
  /* Set conn_master event vector = &busyConnHandler */
  ldap r11, busyConnHandler
  ldw  r10, dp[conn_master]
  setv res[r10], r11
  
  /* Set conn_master channel mode to interrupts */
  setc res[r10], XS1_SETC_IE_MODE_INTERRUPT
  
  /* Enable interrupts */
  ldw r11, sp[2]
  ldc r10, SR_IEBLE
  or  r11, r11, r10
  stw r11, sp[2]

  //bl   releaseThread /* <-- need this? */
  bu   .L.idle.exit
  
.L.idle.excep:
  /* We shouldn't be able to reach here as the busy handler will be invoked
     when all threads are busy. */
  ldc r0, et_INSUFFICIENT_THREADS
  ldc r11, 0
  ecallf r11

.L.idle.exit:
  ldw spc, sp[1]
  ldw ssr, sp[2]
  ldw sed, sp[3]
  ldw lr,  sp[4]
  ldw r0,  sp[5]

  /* Return from the kernel */
  krestsp 6
  kret

  .cc_bottom idleHostHandler.function

/*============================================================================
 * Busy host handler
 *==========================================================================*/
  .cc_top busyHostHandler.function, busyHostHandler
  .align 2
busyHostHandler:
  
  kentsp 20
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw r0,  sp[4]
  stw r1,  sp[5]
  stw r2,  sp[6]
  stw r3,  sp[7]
  stw r4,  sp[8]
  stw r5,  sp[9]
  stw r6,  sp[10]
  stw r7,  sp[11]
  stw r8,  sp[12]
  stw r9,  sp[13]
  stw r10, sp[14]
  stw r11, sp[15]
  stw lr,  sp[16]
   
  /* If we get to this point: all threads are busy! */
  ldc r0, et_INSUFFICIENT_THREADS
  ldc r11, 0
  ecallf r11

  ldw spc, sp[1]
  ldw ssr, sp[2]
  ldw sed, sp[3]
  ldw r0,  sp[4]
  ldw r1,  sp[5]
  ldw r2,  sp[6]
  ldw r3,  sp[7]
  ldw r4,  sp[8]
  ldw r5,  sp[9]
  ldw r6,  sp[10]
  ldw r7,  sp[11]
  ldw r8,  sp[12]
  ldw r9,  sp[13]
  ldw r10, sp[14]
  ldw r11, sp[15]
  ldw lr,  sp[16]
  
  /* Return */
  krestsp 20
  kret

  .cc_bottom busyHostHandler.function

/*============================================================================
 * Idle connection handler
 *==========================================================================*/
  .cc_top idleConnHandler.function, idleConnHandler
  .align 2
idleConnHandler:
   
  kentsp 6
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw lr,  sp[4]

  /* Run the connection handler */
  bl connHandler
  
  /* Set spc = &controlIdle */
  ldap r11, controlIdle
  stw r11, sp[1] // spc = &idle
  
  ldw spc, sp[1]
  ldw ssr, sp[2]
  ldw sed, sp[3]
  ldw lr,  sp[4]
  ldw r0,  sp[5]

  /* Return */
  krestsp 6
  kret

  .cc_bottom idleConnHandler.function

/*============================================================================
 * Busy connection handler
 *==========================================================================*/
  .cc_top busyConnHandler.function, busyConnHandler
  .align 2
busyConnHandler:
  
  kentsp 20
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw r0,  sp[4]
  stw r1,  sp[5]
  stw r2,  sp[6]
  stw r3,  sp[7]
  stw r4,  sp[8]
  stw r5,  sp[9]
  stw r6,  sp[10]
  stw r7,  sp[11]
  stw r8,  sp[12]
  stw r9,  sp[13]
  stw r10, sp[14]
  stw r11, sp[15]
  stw lr,  sp[16]
  
  /* Run the connection handler */
  bl connHandler
  
  /* Reenable interrupts */
  ldw r11, sp[2]
  ldc r10, SR_IEBLE
  or  r11, r11, r10
  stw r11, sp[2]

  ldw spc, sp[1]
  ldw ssr, sp[2]
  ldw sed, sp[3]
  ldw r0,  sp[4]
  ldw r1,  sp[5]
  ldw r2,  sp[6]
  ldw r3,  sp[7]
  ldw r4,  sp[8]
  ldw r5,  sp[9]
  ldw r6,  sp[10]
  ldw r7,  sp[11]
  ldw r8,  sp[12]
  ldw r9,  sp[13]
  ldw r10, sp[14]
  ldw r11, sp[15]
  ldw lr,  sp[16]
  
  /* Return */
  krestsp 20
  kret

  .cc_bottom busyConnHandler.function

/*============================================================================
 * Error handler
 *==========================================================================*/
/*  .cc_top exceptionHandler.function, exceptionHandler
  .align 2 
exceptionHandler:
  waiteu
  .cc_bottom exceptionHandler.function
*/

/*============================================================================
 * Init pointers: cp, dp, ksp, sp
 * Written in assembly to ensure no use is made of the stack 
 * before sp has been properly set
 *==========================================================================*/
  .cc_top initPointers.function, initPointers
  .align 2
initPointers:

  /* Set cp, dp */
  ldap r11, _cp
  set cp, r11
  ldap r11, _dp
  set dp, r11

  /* Get PS_RAM_BASE and set PS_VEC_BASE */
  ldc r11, 0xb
  ldc r10, 0x10b
  get r9, ps[r11]
  set ps[r10], r9

  /* ksp = 2*PS_RAM_BASE-BYTES_PER_WORD */
  shl r11, r9, 1
  sub r11, r11, 8
  set sp, r11
  stw r11, sp[0]
  krestsp 0

  /* sp = ksp - KERNEL_SPACE */
  ldc r10, KERNEL_SPACE
  sub r11, r11, r10
  set sp, r11

  /* Save the sp for thread allocation */
  stw r11, dp[_sp]

  retsp 0
  .cc_bottom initPointers.function

/*============================================================================
 * Touch registers
 *==========================================================================*/
  .cc_top touchRegs.function, touchRegs
  .align 2
touchRegs:
  ldc r0,  0
  ldc r1,  0
  ldc r2,  0
  ldc r3,  0
  ldc r4,  0
  ldc r5,  0
  ldc r6,  0
  ldc r7,  0
  ldc r8,  0
  ldc r9,  0
  ldc r10, 0
  retsp 0
  .cc_bottom touchRegs.function

/*============================================================================
 * Initialise kep for exceptions
 *==========================================================================*/
  .cc_top setupTraps.function, setupTraps
  .align 2
setupTraps:
  ldap r11, exceptionHandler
  set kep, r11
  retsp 0
  .cc_bottom setupTraps.function

/*============================================================================
 * Init thread. Written in assembly to ensure registers are preserved 
 * properly. Gets called per thread both with asynchronous thread creation by 
 * hosting mechanism and by synchronous thread creation with fork-join 
 * concurrent composition.
 *==========================================================================*/
  .cc_top initThread.function, initThread
  .align 2
initThread:
  bl touchRegs
  bl setupTraps
  ssync
  .cc_bottom initThread.function

