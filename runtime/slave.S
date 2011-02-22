#include "definitions.h"

    .extern touchRegs
    .extern initPointers
    .extern resetChanends
    .extern initChanends
    .extern initCounters
    .extern initPorts
    .extern initMemory
    .extern slaveSync
    .extern slaveMasterIdle
    .extern _initThread

    .globl _start
    .globl _slave, "f{0}(0)"
   
    .text

// Set the _DoSyscall symbol to an inaccessable pc because it persists between
// loadables for mulit-node simulations cauising a retsp to be executed. Slave
// nodes should never use this symbol
    .set _DoSyscall, 0

//==========================================================
// This initilises the execution of thread 0, core i for i>0
//==========================================================
    .cc_top _slave.function, _slave
    .align 2 

_start:
_slave:

    // Initialisation
    bl touchRegs
    bl initPointers
    bl resetChanends
    bl initChanends
    bl initCounters
    bl initPorts
    bl initMemory
    bl __alloc_libc_hwlock
    bl _initThread
    bl slaveSync
    
    // Idle 
    bu slaveMasterIdle

    .cc_bottom _slave.function

