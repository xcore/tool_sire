// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <syscall.h>
#include "system/xs1/definitions.h"
#include "device.h"
#include "globals.h"
#include "system.h"

#define RUNS 1

//extern void _master();
void runMain(unsigned main); 

// Master initialisation (thread0, core0, node0)
/* NOTE: This is the 'normal' master procedure
void initMaster() {

    // Branch to main procedure
    asm("ldap r11, " MAIN_PROC "\n\t"
        "bla r11" ::: "r11");

    idle();
}*/

// Master procedure with timing.
void initMaster() {

    timer tmr;
    unsigned main, begin, end, elapsed, result;
    
    asm("ldap r11, " LABEL_MAIN "\n\t"
        "mov %0, r11" : "=r"(main) :: "r11");
   
    tmr :> begin;
    runMain(main);
    tmr :> end;
       
    // Calculate the elapsed time in 10ms units
    elapsed = (end-begin); /// 100;

    // Move the elapsed time to r11 and pause
    asm("mov r11, %0" :: "r"(elapsed));
    //asm("waiteu");

    //idle();
    _exit(0);
}

