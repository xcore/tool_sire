// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "system/xs1/definitions.h"
   
  .extern _createProcess
  .extern _procId
  .extern _connectMaster
  .extern _connectSlave
  
  .globl _sizetab,  "a(:ui)"
  .globl _frametab, "a(:ui)"

// cp =====================================================
  .section .cp.rodata, "ac", @progbits
	
  .align 4
  .set _jumptab.globound, BYTES_PER_WORD*JUMP_TABLE_SIZE

_jumptab:
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
  .space BYTES_PER_WORD*(JUMP_TABLE_SIZE-JUMP_INDEX_OFFSET)

// dp =====================================================
	.section .dp.data, "awd", @progbits

  .align 4
  .set _sizetab.globound, BYTES_PER_WORD*SIZE_TABLE_SIZE
  
_sizetab:
  .space BYTES_PER_WORD*SIZE_TABLE_SIZE, 0 

