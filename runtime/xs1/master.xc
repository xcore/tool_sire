// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <syscall.h>
#include "system/xs1/definitions.h"
#include "device.h"
#include "globals.h"
#include "util.h"
#include "system.h"
#include "control.h"

#define RUNS 1

//void runMain(unsigned main); 

// Master initialisation (thread0, core0, node0)
/* NOTE: This is the 'normal' master procedure
void initMaster() {

  // Branch to main procedure
  asm volatile("ldap r11, " MAIN_PROC "\n\t"
    "bla r11" ::: "r11");

  idle();
}*/

/* 
 * Start the main function on a new asynchronous thread with the link regiser
 * set to yeildMaster which will halt execution.
 */
void initMain() {
  
  // Claim a thread
  unsigned t;
  GETR_ASYNC_THREAD(t);
  
  // Load the address of '_main'
  asm volatile("ldap r11, " LABEL_MAIN "; init t[%0]:pc, r11" :: "r"(t) : "r11");
  asm volatile("ldap r11, masterYeild ; init t[%0]:lr, r11" :: "r"(t) : "r11");
  
  // Touch GPRs
  asm volatile("set t[%0]:r0, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r1, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r2, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r3, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r4, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r5, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r6, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r7, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r8, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r9, %1"  :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r10, %1" :: "r"(t), "r"(0));
  asm volatile("set t[%0]:r11, %1" :: "r"(t), "r"(0));
  
  // Start the thread
  asm volatile("start t[%0]" :: "r"(t));

  /*
  timer tmr;
  unsigned begin, end, elapsed, result;
  tmr :> begin;
  runMain(main);
  tmr :> end;
   
  // Calculate the elapsed time in 10ms units
  elapsed = (end-begin); /// 100;

  // Move the elapsed time to r11 and pause
  asm volatile("mov r11, %0" :: "r"(elapsed));
  //asm volatile("waiteu");
  
  //idle();
  _exit(0);
  */
}

/*
 * This is called when the (original) master program thread has finished
 * executing indicating the program has halted.
 */
void masterYeild() {
  _exit(0);
}

