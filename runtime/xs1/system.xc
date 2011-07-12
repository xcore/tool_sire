// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "device.h"
#include "globals.h"
#include "util.h"
#include "system.h"

// Return the processor id by allocating a channel end, extracting the node and
// core id, then deallocating it again.
int _procid() {
  unsigned c, v;
  asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
  asm("bitrev %0, %1" : "=r"(v) : "r"(c));
  v = ((v & 0xFF) * NUM_CORES_PER_NODE) + ((c >> 16) & 0xFF);
  asm("freer res[%0]" :: "r"(c));
  return v;
}

// Allocate all remaining channel ends then free them to ensure they are all
// available
void resetChanends() {
  
  unsigned c = 1;
  unsigned c0 = GETR_CHANEND();

  // Get all remaining channels
  while(c)
    c = GETR_CHANEND();
   
  // Free all channels
  c = c0 & 0xFFFF00FF;
  for(int i=0; i<MAX_CHANNELS; i++) {
    FREER(c);
    c += 0x100;
  }
}

// Initialse the system: executed once by thread 0, for all threads
#pragma unsafe arrays 
void initChanends() {
  
  // Get the migration channel and set the event vector
  // ASSERT: channel resource counter must be 0 
  spawn_master = GETR_CHANEND();
  asm("eeu res[%0]" :: "r"(spawn_master));
  
  // Allocate a channel end for setting up connections
  conn_master = GETR_CHANEND();

  // Get channels for each thread
  for(int i=0; i<MAX_THREADS; i++) 
    thread_chans[i] = GETR_CHANEND();
}

// Initialise system resource counters
void initCounters() {

  // Get locks
  _numthreads_lock = GETR_LOCK();

  // Set available threads
  _numthreads = MAX_THREADS; 
}

// Initialise ports
void initPorts() {
  // Setup XMP-64 led port
  asm("setc res[%0], 8 ; setclk res[%0], %1" :: "r"(LED_PORT), "r"(6));
}

// Initialise memory
void initMemory() {

  unsigned begin;
  unsigned end;
  int size;

  // Zero-initialise .bss section
  asm("ldap r11, " LABEL_BEGIN_BSS
    "\n\tmov %0, r11" : "=r"(begin) :: "r11");
  asm("ldap r11, " LABEL_END_BSS
    "\n\tmov %0, r11" : "=r"(end) :: "r11");
  size = (end - begin) / BYTES_PER_WORD;

  for (int i=0; i<size; i++) {
    asm("stw %0, %1[%2]" :: "r"(0), "r"(begin), "r"(i));
  }
}

//int read_sswitch_reg(unsigned coreid, unsigned reg, unsigned &data);
//int write_sswitch_reg(unsigned coreid, unsigned reg, unsigned data);

// Ensure all cores are in a consistent state before completing initialisation
// Assume that master is always core 0
void masterSync() {

  if (NUM_CORES > 1) {

    /*unsigned coreId = GET_CORE_ID(spawn_master);
    unsigned switchCRI = GEN_CONFIG_RI(0); 
    unsigned c, v;
    unsigned t;

    // Get and set a chanend
    c = progChan[0];
    asm("setd res[%0], %1" :: "r"(c), "r"(switchCRI));

    // If core 0 set scratch reg to 1 and wait untill it reaches NUM_CORES
    cfgWrite(c, 1);
    while(cfgRead(c) != NUM_CORES)
      continue;*/

    unsigned v;
    write_sswitch_reg(0, SWITCH_SCRATCH_REG, 1);
    read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
     // asm("waiteu");
    while (v != NUM_CORES)
      read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
  }
}

// Ensure all cores are in a consistent state before completing initialisation
void slaveSync() {

  /*unsigned coreId = GET_CORE_ID(spawn_master);
  unsigned switchCRI = GEN_CONFIG_RI(0); 
  unsigned c, v;

  // Get and set a chanend
  c = progChan[0];
  asm("setd res[%0], %1" :: "r"(c), "r"(switchCRI));

  // Otherwise wait until the value reaches coreId and write coreId+1
  while(cfgRead(c) != coreId)
    continue;
  cfgWrite(c, coreId+1);*/
   
  unsigned coreId = GET_GLOBAL_CORE_ID(spawn_master);
  unsigned v;
  read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
  //asm("waiteu");
  while (v != coreId)
    read_sswitch_reg(0, SWITCH_SCRATCH_REG, v);
  write_sswitch_reg(0, SWITCH_SCRATCH_REG, coreId+1);
}

// Idle (thread 0 only) for the next event to occur
void slaveMasterIdle() {

  // Disable interrupts and events, switch to event mode
  asm("clrsr " S(SR_IEBLE) " | " S(SR_EEBLE));
  asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(spawn_master));
  
  // Set event vector to idle handler
  asm("ldap r11, " LABEL_IDLE_HOST_HANDLER "\n\t"
    "setv res[%0], r11" :: "r"(spawn_master) : "r11");

  // Wait for an event on spawn_master
  asm("waiteu");
}

// Yeild execution of the master thread (of a slave node), and enter idle state.
void slaveMasterYeild() {
  releaseThread();
  slaveMasterIdle();
}

// Yeild execution of a slave thread (only 1-7)
void slaveYeild() {
  releaseStackSlot(GET_THREAD_ID());
  releaseThread();
  asm("freet");
}

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
  asm("init t[%0]:pc, %1" :: "r"(t), "r"(pc));
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

unsigned int getAvailThreads() {
  unsigned num;
  ACQUIRE_LOCK(_numthreads_lock);
  num = _numthreads;
  RELEASE_LOCK(_numthreads_lock);
  return num;
}

unsigned claimAsyncThread() {
  unsigned t;
  ACQUIRE_LOCK(_numthreads_lock);
  t = GET_ASYNC_THREAD();
  if(t == 0) error();
  _numthreads = _numthreads - 1;
  RELEASE_LOCK(_numthreads_lock);
  return t;
}

unsigned claimSyncThread(unsigned sync) {
  unsigned t;
  ACQUIRE_LOCK(_numthreads_lock);
  t = GET_SYNC_THREAD(sync);
  if(t == 0) error();
  _numthreads = _numthreads - 1;
  RELEASE_LOCK(_numthreads_lock);
  return t;
}

void releaseThread() {
  ACQUIRE_LOCK(_numthreads_lock);
  _numthreads = _numthreads + 1;
  RELEASE_LOCK(_numthreads_lock);
}

unsigned claimStackSlot(int threadId) {
  return _sp - (threadId * THREAD_STACK_SPACE);
}

void releaseStackSlot(int threadId) {
}

