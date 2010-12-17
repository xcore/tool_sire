    .extern touchRegs
    .extern initPointers
    .extern initSystem
    .extern initThread
    .extern syncCores
    .extern initMaster
  
    .globl _start
    .globl _master, "f{0}(0)"
    .globl runMain, "f{0}(ui)"

    .text

//==========================================================
// This initialises the execution of thread 0, core 0
//==========================================================
    .cc_top _master.function, _master 
    .align 2 

_start:
_master:
    
    bl touchRegs
    bl initPointers
    bl initSystem
    bl initThread
    
/*    ldc r11, 2
    shl r11, r11, 24

// Pause for a bit until the other cores are ready to synchronise??
.Lstart:
    eq  r10, r11, 0
    bt  r10, .Lexit
    sub r11, r11, 1
    bu .Lstart

.Lexit:*/
    bl syncCores
    bu initMaster

    .cc_bottom _master.function

//==========================================================
// A wrapper to run the program main so that r0-r3 are preserved properly
//==========================================================
    .cc_top runMain.function, runMain
    .align 2 
   
runMain:
    entsp 1
    bla r0
    retsp 1

    .cc_bottom runMain.function

