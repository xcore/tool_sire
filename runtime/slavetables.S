#include "definitions.h"
   
    .extern _migrate
    .extern _setupthread
    .extern _connect
    
    .globl _jumptab,  "a(:ui)"
    .globl _sizetab,  "a(:ui)"
    .globl _frametab, "a(:ui)"

// cp =====================================================
    .section .cp.rodata, "ac", @progbits
	
    .align 4
    .set _jumptab.globound, BYTES_PER_WORD*JUMP_TABLE_SIZE

_jumptab:
    .word _migrate
    .word _setupthread
    .word _connect
    .space BYTES_PER_WORD*(JUMP_TABLE_SIZE-JUMP_INDEX_OFFSET)

// dp =====================================================
	.section .dp.data, "awd", @progbits

    .align 4
    .set _sizetab.globound, BYTES_PER_WORD*SIZE_TABLE_SIZE

_sizetab:
    .space BYTES_PER_WORD*SIZE_TABLE_SIZE 

    .align 4
    .set _frametab.globound, BYTES_PER_WORD*FRAME_TABLE_SIZE

_frametab:
    .space BYTES_PER_WORD*FRAME_TABLE_SIZE

