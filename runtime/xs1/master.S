// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "system/xs1/definitions.h"

  .extern touchRegs
  .extern initPointers
  .extern resetChanends
  .extern initChanends
  .extern initCounters
  .extern initPorts
  .extern initMemory
  .extern masterSync
  .extern initMaster
  .extern _initthread

  .globl main
  .globl _start
  .globl _master, "f{0}(0)"
  .globl runMain, "f{0}(ui)"

  .text

//==========================================================
// This initialises the execution of thread 0, core 0
//==========================================================
  .cc_top _master.function, _master 
  .align 2 

main:
_start:
_master:
  
  // Initialisation
  bl touchRegs
  bl initPointers
  bl resetChanends
  bl initChanends
  bl initCounters
  bl initPorts
  bl initMemory
  bl __alloc_libc_hwlock
  bl _initthread
  bl masterSync
 
  // Initialise and run master program
  bu initMaster

  .cc_bottom _master.function

//==========================================================
// A wrapper to run the program main so that r0-r3 are preserved properly
//==========================================================
  .cc_top runMain.function, runMain
  .align 2 
   
runMain:
  entsp 1
  bla r0
  retsp 1

  .cc_bottom runMain.function

