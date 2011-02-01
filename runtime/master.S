    .extern touchRegs
    .extern initPointers
    .extern resetChannels
    .extern initSystem
    .extern _setupthread
    .extern syncCores
    .extern initMaster
  
    .globl main
    .globl _start
    .globl _master, "f{0}(0)"
    .globl runMain, "f{0}(ui)"

    .text

//==========================================================
// This initialises the execution of thread 0, core 0
//==========================================================
    .cc_top _master.function, _master 
    .align 2 

main:
_start:
_master:
    
    bl touchRegs
    bl initPointers
    bl resetChannels
    bl initSystem
    bl _setupthread
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

