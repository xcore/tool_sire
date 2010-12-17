#include "../include/definitions.h"
   
    .extern migrate
    .extern initThread

    .section .cp.rodata, "ac", @progbits
	
    .align 4
    .globl jumpTable, "a(:ui)"
    .set jumpTable.globound, BYTES_PER_WORD*JUMP_TAB_SIZE

jumpTable:
    .word migrate
    .word initThread
    .word connect
    .space BYTES_PER_WORD*(JUMP_TAB_SIZE-JUMP_INDEX_OFFSET)
