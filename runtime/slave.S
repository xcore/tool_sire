#include "definitions.h"

    .extern touchRegs
    .extern initPointers
    .extern resetChannels
    .extern initSystem
    .extern _setupthread
    .extern syncCores
    .extern idle

    .globl _start
    .globl _slave, "f{0}(0)"
    .globl _sizetab, "a(:ui)"
   
    .text

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
    bl syncCores
    bu idle

    .cc_bottom _slave.function

//==========================================================
// Data
//==========================================================
	.section .dp.data, "awd", @progbits
	
    .align 4
    .set _sizetab.globound, BYTES_PER_WORD*SIZE_TABLE_SIZE

_sizetab:
    .space BYTES_PER_WORD*SIZE_TABLE_SIZE 

