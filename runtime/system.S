#include <xs1.h>
#include "definitions.h"

    .extern initSystem
    .extern host
    .extern setHost
    .extern spawnHost
    .extern runThread
    .extern yeild
    .extern error
    .extern idle
    .extern getThreadId
    .extern raiseException

    .globl excepHandler
    .globl idleHostHandler
    .globl busyHostHandler
    .globl touchRegs
    .globl initPointers
    .globl _setupthread, "f{0}(0)"

    .text

// NOTE: THIS MUST BE LINKED AT THE BEGINNING OF THE BINARY

//==========================================================
// Exception/interrupt handler (KEP)
//==========================================================
    
    .cc_top excepHandler.function, excepHandler
    
    // Force the KEP to align on byte 64
    //nop 
    .align 128
excepHandler:

    clre
    waiteu

    .cc_bottom excepHandler.function

//==========================================================
// Idle host handler
//==========================================================
    .cc_top idleHostHandler.function, idleHostHandler
    .align 2
idleHostHandler:
   
    kentsp 6
    
    stw spc, sp[1]
    stw ssr, sp[2]
    stw sed, sp[3]
    stw lr,  sp[5]

    // Set the host connection up with this thread
    bl setHost
    stw r0, sp[4] 
    
    // Set pc to runThread function. Adjust stored _pc so busyHostHandler
    // doesn't increment it if an interrupt occurs immediately after this.
    ldap r11, runThread
    stw r11, sp[1]
    stw r11, dp[_pc]
    ldw spc, sp[1]

    // Set lr = &idle
    ldap r11, idle
    stw r11, sp[5]
    ldw lr, sp[5]

    // Set mSpawnChan event vector = &busyHostHandler
    ldap r11, busyHostHandler
    ldw  r10, dp[mSpawnChan]
    setv res[r10], r11
    
    // Set channel mode to interrupts
    setc res[r10], XS1_SETC_IE_MODE_INTERRUPT
    
    // Enable interrupts
    ldw r11, sp[2]
    ldc r10, SR_IEBLE
    or  r11, r11, r10
    stw r11, sp[2]
    
    ldw spc, sp[1]
    ldw ssr, sp[2]
    ldw sed, sp[3]
    ldw r0,  sp[4]
    stw r0,  sp[5]

    // Return
    krestsp 6
    kret

    .cc_bottom idleHostHandler.function

//==========================================================
// Busy host handler
//==========================================================

    .cc_top busyHostHandler.function, busyHostHandler
    .align 2
busyHostHandler:
  
    kentsp 20
  
    stw spc, sp[1]
    stw ssr, sp[2]
    stw sed, sp[3]
    stw r0,  sp[4]
    stw r1,  sp[5]
    stw r2,  sp[6]
    stw r3,  sp[7]
    stw r4,  sp[8]
    stw r5,  sp[9]
    stw r6,  sp[10]
    stw r7,  sp[11]
    stw r8,  sp[12]
    stw r9,  sp[13]
    stw r10, sp[14]
    stw r11, sp[15]
    stw lr,  sp[16]
   
    // Initate connection and spawn a thread
    bl spawnHost
   
    // Renable interrupts
    ldw r11, sp[2]
    ldc r10, SR_IEBLE
    or  r11, r11, r10
    stw r11, sp[2]
   
    // Increment pc if: has changed or inst not paused

    //=========================================================================
    // Determine if spc has changed between this interrupt and possibly the last
    // and if the instruction was paused - in which case we don't want to
    // increment the spc.
    //=========================================================================

    // Check if it has changed (queued interrupts)
    ldw r11, sp[1]    // r11 = pc
    ldw r10, dp[_pc]  // r10  = _pc
    eq  r11, r11, r10 // r11 = 1 if pc not changed else 0 (pc == _pc)
    //not r11, r11      // r11 = 0 if pc changed else 1 (pc != _pc)
    
    // Check if the instruction was paused
    ldw r10, sp[2]
    ldc r9, SR_WAITING
    and r10, r10, r9
    eq  r10, r10, r9  // r10 = inst was paused

    // if (pc not changed or inst paused) then EXIT
    or  r11, r11, r10
    bt  r11, .L.BUSY.EXIT
  
    //==========================================================
    // Load the Bpw/2 MSB of the interrupted instruction at spc
    //==========================================================
    
    // Load the interrupted instruction (on a word boundary)
    ldw r11, sp[1]    // r11 = spc
    ldc r10, 0x2      // r10 = 0x2
    and r10, r11, r10 // r10 = r10 and 0x2
    eq  r10, r10, 0   // r10 = r10 == 0
    bf  r10, .L.BUSY.loadPCOffset

    // Load the spc normally (as its on a word boundary)
.L.BUSY.loadPC:
    ldw r10, r11[0]   // r10 = mem[spc]
    bu .L.BUSY.getInstLen

    // Load the spc at last word boundary and shr 16 bits
.L.BUSY.loadPCOffset:
    sub r9, r11, 2    // r9  = spc - 2
    ldw r10, r9[0]    // r10 = mem[spc-2]
    shr r10, r10, 16  // r10 = r10 >> 16

    //==========================================================
    // Determine the length of the instruction:
    //   Bpw if (inst>>28) & 0xF == 0xF else Bpw/2
    //==========================================================

    // Determine the instruction length (looking at top 4 bits of bottom 16 bits)
.L.BUSY.getInstLen:
    ldc r9, 12        // r9  = 12
    shr r10, r10, r9  // r10 = r10 >> 12
    ldc r9, 0xF       // r9  = 0xF
    eq  r10, r10, r9  // r10 = r10 == r9
    bt  r10, .L.BUSY.incPCLong
    
    // Increment spc by 2
.L.BUSY.incPCShort:
    add r11, r11, 2
    bu .L.BUSY.savePC

    // Increment spc by 4
.L.BUSY.incPCLong:
    add r11, r11, 4

    // Save spc back to stack and in _pc
.L.BUSY.savePC:
    stw r11, sp[1]
    stw r11, dp[_pc]

.L.BUSY.EXIT:
    ldw spc, sp[1]
    ldw ssr, sp[2]
    ldw sed, sp[3]
    ldw r0,  sp[4]
    ldw r1,  sp[5]
    ldw r2,  sp[6]
    ldw r3,  sp[7]
    ldw r4,  sp[8]
    ldw r5,  sp[9]
    ldw r6,  sp[10]
    ldw r7,  sp[11]
    ldw r8,  sp[12]
    ldw r9,  sp[13]
    ldw r10, sp[14]
    ldw r11, sp[15]
    ldw lr,  sp[16]
    
    // Return
    krestsp 20
    kret

    .cc_bottom busyHostHandler.function

//==========================================================
// Error handler
//==========================================================
    .cc_top errHandler.function, errHandler
    .align 2 
errHandler:
    bl error
    .cc_bottom errHandler.function

//==========================================================
// Touch registers
//==========================================================
    .cc_top touchRegs.function, touchRegs
    .align 2
touchRegs:
    ldc r0,  0
    ldc r1,  0
    ldc r2,  0
    ldc r3,  0
    ldc r4,  0
    ldc r5,  0
    ldc r6,  0
    ldc r7,  0
    ldc r8,  0
    ldc r9,  0
    ldc r10, 0
    retsp 0
    .cc_bottom touchRegs.function

//==========================================================
// Init pointers: cp, dp, ksp, sp
// Written in assembly to ensure no use is made of the stack 
// before sp has been properly set
//==========================================================
    .cc_top initPointers.function, initPointers
    .align 2
initPointers:

    // Set cp, dp
    ldap r11, _cp
    set cp, r11
    ldap r11, _dp
    set dp, r11

    // Get PS_RAM_BASE and set PS_VEC_BASE
    ldc r11, 0xb
    ldc r10, 0x10b
    get r9, ps[r11]
    set ps[r10], r9

    // ksp = 2*PS_RAM_BASE-BYTES_PER_WORD
    shl r11, r9, 1
    sub r11, r11, 8
    set sp, r11
    stw r11, sp[0]
    krestsp 0

    // sp = ksp - KERNEL_SPACE
    ldc r10, KERNEL_SPACE
    sub r11, r11, r10
    set sp, r11

    // Save the sp for thread allocation
    stw r11, dp[_sp]

    retsp 0
    .cc_bottom initPointers.function

//==========================================================
// Init thread
// Written in assembly to ensure registers are preserved 
// properly
// Gets called per thread both with asynchronous thread creation by hosting
// mechanism and by synchronous thread creation with fork-join concurrent
// composition
//==========================================================
    .cc_top _setupthread.function, _setupthread
    .align 2
_setupthread:
   
    entsp 2
    stw r11, sp[0]
    stw r10, sp[1]

    // Initialise kep for exceptions
    ldap r11, excepHandler
    set kep, r11

    ldw r10, sp[1]
    ldw r11, sp[0]
    retsp 2
    
    .cc_bottom _setupthread.function

//==========================================================
// Constants
//==========================================================
//	.section .cp.rodata, "ac", @progbits
//	.align 4
	
//==========================================================
// Data
//==========================================================
    .globl mSpawnChan, "ui"
    .globl spawnChan,  "a(:ui)"
    .globl progChan,   "a(:ui)"
    .globl _fpLock,    "ui"
    .globl _spLock,    "ui"
    .globl _fp,        "ui"
    .globl _sp,        "ui"
    .globl _pc,        "ui"
	
	.section .dp.data, "awd", @progbits
    .align BYTES_PER_WORD

/* TODO: move these declarations into XC? */

// Master/migrate 
mSpawnChan:
    .space BYTES_PER_WORD
    .globl mSpawnChan.globound
    .set mSpawnChan.globound, BYTES_PER_WORD

// Channel array storing identifiers for each thread
spawnChan:
    .space MAX_THREADS*BYTES_PER_WORD
    .globl spawnChan.globound
    .set spawnChan.globound, MAX_THREADS*BYTES_PER_WORD

// Channel array storing identifiers for each thread
progChan:
    .space NUM_PROG_CHANS*BYTES_PER_WORD
    .globl progChan.globound
    .set progChan.globound, NUM_PROG_CHANS*BYTES_PER_WORD

// _fp lock identifier
_fpLock:
    .space BYTES_PER_WORD
    //.globl _fpLock.globound
    .set _fpLock.globound, BYTES_PER_WORD

// _sp lock identifier
_spLock:
    .space BYTES_PER_WORD
    //.globl _spLock.globound
    .set _spLock.globound, BYTES_PER_WORD

// Function pointer (for loading functions into memory)
_fp:
    .space BYTES_PER_WORD
    //.globl _fp.globound
    .set _fp.globound, BYTES_PER_WORD

// Stack pointer pointer (for allocating new threads)
_sp:
    .space BYTES_PER_WORD
    //.globl _sp.globound
    .set _sp.globound, BYTES_PER_WORD

// For storing the pc on interrupts 
_pc:
    .space BYTES_PER_WORD
    //.globl _pc.globound
    .set _pc.globound, BYTES_PER_WORD

