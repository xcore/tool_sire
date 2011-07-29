// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "system/xs1/definitions.h"

  .extern touchRegs
  .extern initMemory
  .extern initPointers
  .extern setupTraps
  .extern resetChanends
  .extern initThreads
  .extern initChanends
  .extern initPorts
  .extern initConnections
  .extern slaveSync
  .extern controlIdle

  .globl _start
  .globl _slave, "f{0}(0)"
 
  .text

// set the _dosyscall symbol to an inaccessable pc because it persists between
// loadables for mulit-node simulations cauising a retsp to be executed. slave
// nodes should never use this symbol
  //.set _DoSyscall, 0 // This causes problems with 11.2.0 release (not 10.4.2)
  .set _DoSyscall, RAM_BASE+RAM_SIZE 

//==========================================================
// This initilises the execution of thread 0, core i for i>0
//==========================================================
  .cc_top _slave.function, _slave
  .align 2 

_start:
_slave:

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
  bl slaveSync
  
  bu controlIdle

  .cc_bottom _slave.function

