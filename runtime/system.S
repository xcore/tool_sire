#include <xs1.h>
#include "definitions.h"

    .extern initSystem
    .extern host
    .extern setHost
    .extern spawnHost
    .extern runThread
    .extern yeild
    .extern error
    .extern masterIdle
    .extern getThreadId
    .extern getAvailThreads
    .extern decrementAvailThreads
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
// Idle host handler: receives an event on master spawn channel, sets the host
// and then runs the incoming closure on this thread.
//==========================================================
    .cc_top idleHostHandler.function, idleHostHandler
    .align 2
idleHostHandler:
   
    kentsp 6
    
    stw spc, sp[1]
    stw ssr, sp[2]
    stw sed, sp[3]
    stw lr,  sp[4]

    bl getAvailThreads
    eq  r11, r0, 1 
    bt  r11, .L.idle.run   // if _numThreads == 1 then run
    eq  r11, r0, 0
    bt  r11, .L.idle.excep // if _numThreads == 0 then error
                           // else spawn

.L.idle.spawn:
    bl   spawnHost
    ldap r11, masterIdle
    stw  r11, sp[1] // spc = &idle
    bl   decrementAvailThreads
    bu   .L.idle.exit

.L.idle.run:
    // Set the host connection up with this thread
    bl setHost
    stw r0, sp[5]  // r0 = senderId 
    
    // Set pc to runThread function (r0 arg = senderId) 
    ldap r11, runThread
    stw r11, sp[1]

    // Set lr = &masterYeild
    ldap r11, masterYeild
    stw r11, sp[4]

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
   
    bl   decrementAvailThreads
    bu   .L.idle.exit
    
.L.idle.excep:
    // We shouldn't be able to reach here as the busy handler will be invoked
    // when all threads are busy.
    waiteu

.L.idle.exit:
    ldw spc, sp[1]
    ldw ssr, sp[2]
    ldw sed, sp[3]
    ldw lr,  sp[4]
    ldw r0,  sp[5]

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
   
    /*// Initate connection and spawn a thread
    bl spawnHost
   
    // Renable interrupts
    ldw r11, sp[2]
    ldc r10, SR_IEBLE
    or  r11, r11, r10
    stw r11, sp[2]*/
    
    // All threads are busy!
    waiteu

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
    .globl mSpawnChan,      "ui"
    .globl spawnChan,       "a(:ui)"
    .globl progChan,        "a(:ui)"
    .globl _fpLock,         "ui"
    .globl _spLock,         "ui"
    .globl _numThreadsLock, "ui"
    .globl _fp,             "ui"
    .globl _sp,             "ui"
    .globl _numThreads,     "ui"
	
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

// _numThreads lock identifier
_numThreadsLock:
    .space BYTES_PER_WORD
    //.globl _numThreadsLock.globound
    .set _numThreadsLock.globound, BYTES_PER_WORD

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

// Record the number of available threads. 
_numThreads:
    .space BYTES_PER_WORD
    //.globl _numThreads.globound
    .set _numThreads.globound, BYTES_PER_WORD

