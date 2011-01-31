#include "../include/definitions.h"
   
    .extern _migrate
    .extern _setupthread
    .extern _connect

    .section .cp.rodata, "ac", @progbits
	
    .align 4
    .globl _jumptab, "a(:ui)"
    .set _jumptab.globound, BYTES_PER_WORD*JUMP_TABLE_SIZE

_jumptab:
    .word _migrate
    .word _setupthread
    .word _connect
    .space BYTES_PER_WORD*(JUMP_TABLE_SIZE-JUMP_INDEX_OFFSET)
