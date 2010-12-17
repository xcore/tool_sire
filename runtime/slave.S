#include "../include/definitions.h"

    .extern touchRegs
    .extern initPointers
    .extern initSystem
    .extern initThread
    .extern idle
    .extern migrate
    .extern syncCores
    .extern initThread

    .globl main
    .globl _start
    .globl _slave
    .globl sizeTable
   
    .text

//==========================================================
// This initilises the execution of thread 0, core i for i>0
//==========================================================
    .cc_top _slave.function, _slave
    .align 2 

main:
_start:
_slave:

    bl touchRegs
    bl initPointers
    bl initSystem
    bl initThread
    bl syncCores
    bu idle

    .cc_bottom _slave.function

//==========================================================
// Data
//==========================================================
	.section .dp.data, "awd", @progbits
	
    .align 4
    .set sizeTable.globound, BYTES_PER_WORD*SIZE_TAB_SIZE

sizeTable:
    .space BYTES_PER_WORD*SIZE_TAB_SIZE 

