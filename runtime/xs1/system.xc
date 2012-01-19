// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "device.h"
#include "globals.h"
#include "util.h"
#include "worker.h"
#include "system.h"

/* 
 * Allocate all remaining channel ends then free them to ensure they are all
 * available.
 */
void resetChanends() {
  unsigned c = 1;
  unsigned c0;
  asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c0));

  // Get all remaining channels
  while(c) {
    asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
  }
   
  // Free all channels
  c = c0 & 0xFFFF00FF;
  for(int i=0; i<MAX_CHANNELS; i++) {
    FREER(c);
    c += 0x100;
  }
}

/*
 * Initialise all threads with: dp, cp, sp, zero-valued registers and TRAP
 * handler (kep).
 */
void initThreads() {
  unsigned sync;
  unsigned t;
  unsigned sp;
  GETR_SYNC(sync);
  asm("getst %0, res[%1]" : "=r"(t) : "r"(sync));
  while (t) {
    THREAD_SP(TID_MASK(t), sp);
    asm("init t[%0]:sp, %1"::"r"(t), "r"(sp));
    asm("ldaw r11, dp[0]; init t[%0]:dp, r11" :: "r"(t) : "r11");
    asm("ldaw r11, cp[0]; init t[%0]:cp, r11" :: "r"(t) : "r11");
    asm("ldap r11, initThread; init t[%0]:pc, r11" :: "r"(t) : "r11");
    asm("getst %0, res[%1]" : "=r"(t) : "r"(sync));
  }
  asm("msync res[%0]" :: "r"(sync));
  asm("mjoin res[%0]" :: "r"(sync));
  FREER(sync);
}

/*
 * Initialise master spawning and conneciton channels, and request channels
 * for each thread.
 */
#pragma unsafe arrays 
void initChanends() {
  
  // Get the migration channel and set the event vector
  // ASSERT: channel resource counter must be 0 
  GETR_CHANEND(spawn_master);
  asm("eeu res[%0]" :: "r"(spawn_master));
  
  // Allocate a channel end for setting up connections
  GETR_CHANEND(conn_master);
  asm("eeu res[%0]" :: "r"(conn_master));

  // Get channels for each thread
  for(int i=0; i<MAX_THREADS; i++)
    GETR_CHANEND(thread_chans[i]);
}

/*
 * Initialise ports: setup XMP-64 led port.
 */
void initPorts() {
  asm("setc res[%0], 8 ; setclk res[%0], %1" :: "r"(LED_PORT), "r"(6));
}

/*
 * Initialise memory: zero-initialise .bss section
 */
void initMemory() {
  unsigned begin;
  unsigned end;
  int size;

  asm("ldap r11, " LABEL_BEGIN_BSS
    "\n\tmov %0, r11" : "=r"(begin) :: "r11");
  asm("ldap r11, " LABEL_END_BSS
    "\n\tmov %0, r11" : "=r"(end) :: "r11");
  size = (end - begin) / BYTES_PER_WORD;

  for (int i=0; i<size; i++)
    asm("stw %0, %1[%2]" :: "r"(0), "r"(begin), "r"(i));
}

/* 
 * Ensure all cores are in a consistent state before completing initialisation
 * Assume that master is always core 0.
 */
void masterSync() {
#ifdef XS1_G
  if (NUM_CORES > 1) {
    unsigned v;
    write_sswitch_reg(0, SWITCH_SCRATCH_REG, 1);
    read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
    do {
      read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
    } while (v != NUM_CORES);
    /*unsigned v;
    writeSSwitchReg(0, SWITCH_SCRATCH_REG, 1);
    readSSwitchReg(0, SWITCH_SCRATCH_REG, v);
    do {
      readSSwitchReg(0, SWITCH_SCRATCH_REG, v);
    } while (v != NUM_CORES);*/
  }
#endif
}

/*
 * Ensure all cores are in a consistent state before completing initialisation.
 */
void slaveSync() {
#ifdef XS1_G
  unsigned coreId = GET_GLOBAL_CORE_ID(spawn_master);
  unsigned v;
  read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
  do {
    read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
  } while (v != coreId);
  write_sswitch_reg(0, SWITCH_SCRATCH_REG, coreId+1);
  /*readSSwitchReg(0, SWITCH_SCRATCH_REG, v);
  do {
    readSSwitchReg(0, SWITCH_SCRATCH_REG, v);
  } while (v != coreId);
  writeSSwitchReg(0, SWITCH_SCRATCH_REG, coreId+1);*/
#endif
}

/*
 * Return the processor id by allocating a channel end, extracting the node and
 * core id, then deallocating it again.
 */
int _procId() {
  unsigned c, v;
  asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
  asm("bitrev %0, %1" : "=r"(v) : "r"(c));
  v = ((v & 0xFF) * NUM_CORES_PER_NODE) + ((c >> 16) & 0xFF);
  asm("freer res[%0]" :: "r"(c));
  return v;
}

/*
 * memAlloc builtin wrapper.
 */
int _memAlloc(unsigned &p, int size) {
  p = memAlloc(size);
  return (p == 0) ? 0 : 1;
}

/*
 * memAlloc builtin wrapper.
 */
int _memFree(unsigned p) {
  memFree(p);
  return 0;
}

/*
 * Spawn a new asynchronous thread with 4 specified arguments.
 */
void newAsyncThread(unsigned pc, unsigned arg1, 
    unsigned arg2, unsigned arg3, unsigned arg4) {
  
  // Claim a thread
  unsigned t;
  GETR_ASYNC_THREAD(t);
  
  // Initialise pc, lr
  asm("init t[%0]:pc, %1" :: "r"(t), "r"(pc));
  asm("ldap r11, workerYeild" 
    "; init t[%0]:lr, r11" :: "r"(t) : "r11");
               
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

