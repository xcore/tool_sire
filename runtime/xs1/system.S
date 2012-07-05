// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"

  .extern spawnHost
  .extern controlIdle
  .extern controlYeild
  .extern releaseThread
  .extern raiseException
  .extern serveConnReq

  .extern spawn_master
  .extern conn_master
  .extern _spValue

  .globl exepHandler
  .globl hostHandler
  .globl connHandler
  .globl initPointers
  .globl touchRegs
  .globl setupTraps
  .globl initThread
  
  .globl _jumpTable

  /* Set heap labels for malloc */
  .globl _bheap
  .globl _eheap
  .linkset _bheap, _edp.bss 
  .linkset _eheap, RAM_BASE+RAM_SIZE-(KERNEL_SPACE+(MAX_THREADS*THREAD_STACK_SPACE))

  .text

/*============================================================================
 * Exception/interrupt handler (KEP)
 * NOTE: THIS MUST BE LINKED AT THE BEGINNING OF THE BINARY.
 *==========================================================================*/
  .cc_top exepHandler.function, exepHandler
  
  /* Force the KEP to align on byte 64 */
  //nop 
  .align 128
exepHandler:

  clre
  waiteu

  .cc_bottom exepHandler.function

/*============================================================================
 * Host handler: receives an event on master spawn channel, sets the host
 * and then runs the incoming closure on a new asynchronous thread.
 *==========================================================================*/
  .cc_top hostHandler.function, hostHandler
  .align 2
hostHandler:
   
  kentsp 6
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw lr,  sp[4]

  bl spawnHost
  ldap r11, controlIdle
  stw r11, sp[1] // spc = &idle

  ldw spc, sp[1]
  ldw ssr, sp[2]
  ldw sed, sp[3]
  ldw lr,  sp[4]
  ldw r0,  sp[5]

  /* Return from the kernel */
  krestsp 6
  kret

  .cc_bottom hostHandler.function

/*============================================================================
 * Connection handler
 *==========================================================================*/
  .cc_top connHandler.function, connHandler
  .align 2
connHandler:
   
  kentsp 6
  
  stw spc, sp[1]
  stw ssr, sp[2]
  stw sed, sp[3]
  stw lr,  sp[4]

  /* Run the connection handler */
  bl serveConnReq
  
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

  .cc_bottom connHandler.function

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
  stw r11, dp[_spValue]

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
  ldap r11, exepHandler
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

/*==============================================================
 * cp
 *============================================================*/
  .section .cp.rodata, "ac", @progbits
  .align 4

  .set _jumpTable.globound, BYTES_PER_WORD*JUMP_TABLE_SIZE
_jumpTable:
  .word _createProcess
	.word _procId
  .word _connectMaster
  .word _connectSlave
  .word _connectServer
  .word _connectClient
  .word _memAlloc
  .word _memFree
  .word _pointerUnsigned
  .word _pointerInt
  .word _sp
  .space BYTES_PER_WORD*(JUMP_TABLE_SIZE-JUMP_INDEX_OFFSET), 0

