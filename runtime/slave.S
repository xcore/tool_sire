#include "definitions.h"

    .extern touchRegs
    .extern initPointers
    .extern resetChannels
    .extern initSystem
    .extern _setupthread
    .extern slaveSync
    .extern idle

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

    bl touchRegs
    bl initPointers
    bl resetChannels
    bl initSystem
    bl _setupthread
    bl slaveSync
    bu idle

    .cc_bottom _slave.function

