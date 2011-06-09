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
    asm("freer res[%0]" :: "r"(c));
    c += 0x100;
  }
}

// Initialse the system: executed once by thread 0, for all threads
#pragma unsafe arrays 
void initChanends() {
  
  // Get the migration channel and set the event vector
  // ASSERT: channel resource counter must be 0 
  mSpawnChan = GETR_CHANEND();
  asm("eeu res[%0]" :: "r"(mSpawnChan));

  // Get channels for each thread
  for(int i=0; i<MAX_THREADS; i++) 
    spawnChan[i] = GETR_CHANEND();

  // Get the remaining channels for program use
  /*for(int i=0; i<NUM_PROG_CHANS; i++)
    progChan[i] = GETR_CHANEND();*/
}

// Initialise system resource counters
void initCounters() {

  // Get locks
  _numThreadsLock = GETR_LOCK();

  // Set available threads
  _numThreads = MAX_THREADS; 
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

    /*unsigned coreId = GET_CORE_ID(mSpawnChan);
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

  /*unsigned coreId = GET_CORE_ID(mSpawnChan);
  unsigned switchCRI = GEN_CONFIG_RI(0); 
  unsigned c, v;

  // Get and set a chanend
  c = progChan[0];
  asm("setd res[%0], %1" :: "r"(c), "r"(switchCRI));

  // Otherwise wait until the value reaches coreId and write coreId+1
  while(cfgRead(c) != coreId)
    continue;
  cfgWrite(c, coreId+1);*/
   
  unsigned coreId = GET_GLOBAL_CORE_ID(mSpawnChan);
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
  asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(mSpawnChan));
  
  // Set event vector to idle handler
  asm("ldap r11, " LABEL_IDLE_HOST_HANDLER "\n\t"
    "setv res[%0], r11" :: "r"(mSpawnChan) : "r11");

  // Wait for an event on mSpawnChan
  asm("waiteu");
}

// Yeild execution of the master thread (of a slave node), and enter idle state.
void slaveMasterYeild() {
  releaseThread();
  slaveMasterIdle();
}

unsigned int getAvailThreads() {
  unsigned num;
  ACQUIRE_LOCK(_numThreadsLock);
  num = _numThreads;
  RELEASE_LOCK(_numThreadsLock);
  return num;
}

unsigned claimAsyncThread() {
  unsigned t;
  ACQUIRE_LOCK(_numThreadsLock);
  t = GET_ASYNC_THREAD();
  if(t == 0) error();
  _numThreads = _numThreads - 1;
  RELEASE_LOCK(_numThreadsLock);
  return t;
}

unsigned claimSyncThread(unsigned sync) {
  unsigned t;
  ACQUIRE_LOCK(_numThreadsLock);
  t = GET_SYNC_THREAD(sync);
  if(t == 0) error();
  _numThreads = _numThreads - 1;
  RELEASE_LOCK(_numThreadsLock);
  return t;
}

void releaseThread() {
  ACQUIRE_LOCK(_numThreadsLock);
  _numThreads = _numThreads + 1;
  RELEASE_LOCK(_numThreadsLock);
}

unsigned claimStackSlot(int threadId) {
  return _sp - (threadId * THREAD_STACK_SPACE);
}

void releaseStackSlot(int threadId) {
}

