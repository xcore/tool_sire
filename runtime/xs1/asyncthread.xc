// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "system/xs1/definitions.h"
#include "system/definitions.h"
#include "asyncthread.h"

// Spawn a new asynchronous thread
void newAsyncThread(unsigned pc, unsigned arg1, 
    unsigned arg2, unsigned arg3, unsigned arg4) {
  
  // Claim a thread
  unsigned t = claimAsyncThread();
  
  // Claim a stack slot
  unsigned sp = claimStackSlot(THREAD_ID(t));
  
  // Initialise cp, dp, sp, pc, lr
  asm("ldaw r11, cp[0] "
    "; init t[%0]:cp, r11" ::"r"(t) : "r11");
  asm("ldaw r11, dp[0] "
    "; init t[%0]:dp, r11" :: "r"(t) : "r11");
  asm("init t[%0]:sp, %1" :: "r"(t), "r"(sp));
  asm("init t[%0]:pc, r11" :: "r"(t), "r"(pc));
  asm("ldap r11, slaveYeild" 
    " ; init t[%0]:lr, r11" :: "r"(t) : "r11");
               
  // Set register arguments
  asm("set t[%0]:r0, %1"  :: "r"(t), "r"(arg1));
  asm("set t[%0]:r1, %1"  :: "r"(t), "r"(arg2));
  asm("set t[%0]:r2, %1"  :: "r"(t), "r"(arg3));
  asm("set t[%0]:r3, %1"  :: "r"(t), "r"(arg4));

  // Touch remaining GPRs
  asm("set t[%0]:r4, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r5, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r6, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r7, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r8, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r9, %1"  :: "r"(t), "r"(0));
  asm("set t[%0]:r10, %1" :: "r"(t), "r"(0));

  // Start the thread
  asm("start t[%0]" :: "r"(t));
}

// Yeild execution of a slave thread (only 1-7)
void slaveYeild() {
  releaseStackSlot(GET_THREAD_ID());
  releaseThread();
  asm("freet");
}


