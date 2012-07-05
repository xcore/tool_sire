// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef UTIL_H
#define UTIL_H

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "device.h"

typedef char bool;
#define true (1)
#define false (0)

// String wrapper
#define WRAPPER(x) #x
#define S(x) WRAPPER(x)

// Raise a runtime exception
#define EXCEPTION(value) \
do { \
  asm("add r0, r0, %0" :: "r"(value)); \
  asm("ldc r11, 0 ; ecallf r11" ::: "r11"); \
} while(0)

// Assert a value is true (!=0)
#define ASSERT(value) \
do { \
  asm("ecallf %0" :: "r"(value)); \
} while(0)

// Set channel destination
#define SETD(c, destID) \
do { \
  asm("setd res[%0], %1" :: "r"(c), "r"(destID)); \
} while(0)

// OUTCT
#define OUTCT(c, value) \
do { \
  asm("outct res[%0], %1" :: "r"(c), "r"(value)); \
} while(0)

// CHKCT
#define CHKCT(c, value) \
do { \
  asm("chkct res[%0], %1" :: "r"(c), "r"(value)); \
} while(0)

// OUTCT CT_END
#define OUTCT_END(c) \
do { \
  asm("outct res[%0], " S(XS1_CT_END) :: "r"(c)); \
} while(0)

// CHKCT CT_END
#define CHKCT_END(c) \
do { \
  asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c)); \
} while(0)

// OUTCT CT_ACK
#define OUTCT_ACK(c) \
do { \
  asm("outct res[%0], " S(XS1_CT_ACK) :: "r"(c)); \
} while(0)

// CHKCT CT_ACK
#define CHKCT_ACK(c) \
do { \
  asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c)); \
} while(0)

// Asynchronous out
#define OUT(c, value) \
do { \
  asm("out res[%0], %1" :: "r"(c), "r"(value)); \
} while(0)

// Asynchronous in
#define IN(c, value) \
do { \
  asm("in %0, res[%1]" : "=r"(value) : "r"(c)); \
} while(0)

// Synchronised out
#define OUTS(c, value) \
do { \
  asm("outct res[%0], " S(XS1_CT_END) ";" \
      "chkct res[%0], " S(XS1_CT_END) ";" \
      "out   res[%0], %1;" \
      "outct res[%0], " S(XS1_CT_END) ";" \
      "chkct res[%0], " S(XS1_CT_END) ";" \
      :: "r"(c), "r"(value)); \
} while(0)

// Synchronised in
#define INS(c, value) \
do {\
  asm("chkct  res[%1], " S(XS1_CT_END) ";" \
      "outct  res[%1], " S(XS1_CT_END) ";" \
      "in %0, res[%1];" \
      : "=r"(value) : "r"(c)); \
  asm("chkct  res[%0], " S(XS1_CT_END) ";" \
      "outct  res[%0], " S(XS1_CT_END) ";" \
      :: "r"(c)); \
} while(0)

// Server out
#define SERVER_OUT(c, value) \
do { \
  unsigned _clientCRI; \
  asm("in %0, res[%1];" \
      "setd res[%1], %0" : "=&r"(_clientCRI) : "r"(c)); \
  asm("out   res[%0], %1;" \
      "outct res[%0]," S(XS1_CT_END) ";" \
      "chkct res[%0]," S(XS1_CT_END) \
      :: "r"(c), "r"(value)); \
} while(0)

// Server in
#define SERVER_IN(c, value) \
do { \
  unsigned _clientCRI; \
  asm("in %0, res[%1];" \
      "setd res[%1], %0" : "=&r"(_clientCRI) : "r"(c)); \
  asm("outct res[%1]," S(XS1_CT_END) ";" \
      "in    %0, res[%1];" : "=r"(value) : "r"(c)); \
  asm("chkct res[%0]," S(XS1_CT_END) ";" \
      "outct res[%0]," S(XS1_CT_END) \
      :: "r"(c)); \
} while(0)

// Client out
#define CLIENT_OUT(c, value) \
do { \
asm("out   res[%0], %0;" \
    "chkct res[%0]," S(XS1_CT_END) ";" \
    "out   res[%0], %1;" \
    "outct res[%0]," S(XS1_CT_END) ";" \
    "chkct res[%0]," S(XS1_CT_END) \
    :: "r"(c), "r"(value)); \
} while(0)
          
// Client in
#define CLIENT_IN(c, value) \
do { \
asm("out   res[%1], %1;" \
    "in    %0, res[%1];" : "=r"(value) : "r"(c)); \
asm("chkct res[%0]," S(XS1_CT_END) ";" \
    "outct res[%0]," S(XS1_CT_END) \
    :: "r"(c)); \
} while(0)

/*// Server out
#define SERVER_OUT(c, value) \
do { \
  unsigned _clientCRI; \
  asm("in %0, res[%1];" \
      "setd res[%1], %0" : "=&r"(_clientCRI) : "r"(c)); \
  asm("outct res[%0]," S(XS1_CT_END) ";" \
      "chkct res[%0]," S(XS1_CT_END) ";" \
      "out   res[%0], %1;" \
      "outct res[%0]," S(XS1_CT_END) ";" \
      "chkct res[%0]," S(XS1_CT_END) \
      :: "r"(c), "r"(value)); \
} while(0)

// Server in
#define SERVER_IN(c, value) \
do { \
  unsigned _clientCRI; \
  asm("in %0, res[%1];" \
      "setd res[%1], %0" : "=&r"(_clientCRI) : "r"(c)); \
  asm("chkct res[%1]," S(XS1_CT_END) ";" \
      "outct res[%1]," S(XS1_CT_END) ";" \
      "in    %0, res[%1];" : "=r"(value) : "r"(c)); \
  asm("chkct res[%0]," S(XS1_CT_END) ";" \
      "outct res[%0]," S(XS1_CT_END) \
      :: "r"(c)); \
} while(0)

// Client out
#define CLIENT_OUT(c, value) \
do { \
asm("out   res[%0], %0;" \
    "outct res[%0]," S(XS1_CT_END) ";" \
    "chkct res[%0]," S(XS1_CT_END) ";" \
    "out   res[%0], %1;" \
    "outct res[%0]," S(XS1_CT_END) ";" \
    "chkct res[%0]," S(XS1_CT_END) \
    :: "r"(c), "r"(value)); \
} while(0)
          
// Client in
#define CLIENT_IN(c, value) \
do { \
asm("out   res[%1], %1;" \
    "outct res[%1]," S(XS1_CT_END) ";" \
    "chkct res[%1]," S(XS1_CT_END) ";" \
    "in    %0, res[%1];" : "=r"(value) : "r"(c)); \
asm("chkct res[%0]," S(XS1_CT_END) ";" \
    "outct res[%0]," S(XS1_CT_END) \
    :: "r"(c)); \
} while(0)*/

// Get a chanend
#define GETR_CHANEND(resID) \
do { \
  asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(resID)); \
  if (resID == 0) { \
    EXCEPTION(et_INSUFFICIENT_CHANNELS); \
  } \
} while(0)

#define GETR_TIMER(resID) \
do { \
  asm("getr %0, " S(XS1_RES_TYPE_TIMER) : "=r"(resID)); \
  if (resID == 0) { \
    EXCEPTION(et_INSUFFICIENT_TIMERS); \
  } \
} while(0)

// Get a synchroniser
#define GETR_SYNC(resID) \
do { \
  asm("getr %0, " S(XS1_RES_TYPE_SYNC) : "=r"(resID)); \
  if (resID == 0) { \
    EXCEPTION(et_INSUFFICIENT_SYNCS); \
  } \
} while(0)

// Get an asynchronous thread
#define GETR_ASYNC_THREAD(resID) \
do { \
  asm("getr %0, " S(XS1_RES_TYPE_THREAD) : "=r"(resID)); \
  if (resID == 0) { \
    EXCEPTION(et_INSUFFICIENT_THREADS); \
  } \
} while(0)

// Get a synchronous thread
#define GETR_SYNC_THREAD(sync, resID) \
do { \
  asm("getst %0, res[%1]" : "=r"(resID) : "r"(sync)); \
  if (resID == 0) { \
    EXCEPTION(et_INSUFFICIENT_THREADS); \
  } \
} while(0)

// Free a resource
#define FREER(resID) \
do { \
  asm("freer res[%0]" :: "r"(resID)); \
} while(0)

// Create the channel identifier (for channel 0) for a given destination
// The node bits are written in MSB first, so need to be reversed
#if defined(XS1_G)
#define CHAN_RI_0(destID, resID) \
do { \
  unsigned __n = destID / NUM_CORES_PER_NODE; \
  asm("bitrev %0, %1" : "=r"(__n) : "r"(__n)); \
  resID = __n | (destID % NUM_CORES_PER_NODE) << 16 | XS1_RES_TYPE_CHANEND; \
} while(0)
#elif defined(XS1_L)
#define CHAN_RI_0(destID, resID) \
do { \
  resID = destID << 16 | XS1_RES_TYPE_CHANEND; \
} while(0)
#endif

// Create a channel resource identifier with a particular count
#define CHAN_RI(chanID, counter, resID) \
do { \
  CHAN_RI_0(chanID, resID); \
  resID |= counter << 8; \
} while(0)

// Generate a configuration resource identifier
#define CONFIG_RI(nodeID) \
  (nodeID << 24 | XS1_CT_SSCTRL << 8 | 12)

// Get a thread id from a resource identifier
#define TID_MASK(resID) \
  ((resID >> 8) & 0xFF)

// Get the current thread id
#define THREAD_ID(threadID) \
do { \
   asm("get r11, id ; mov %0, r11" : "=r"(threadID) :: "r11"); \
} while(0)

// Return the stack pointer for a specific thread given a thread resource
// identifier to extract the thread id from and the base stack pointer.
// NOTE: only to be called by code resident on a core otherwise the _sp dp
// offset may be wrong.
//#define THREAD_SP(threadID, threadSP) \
//do { \
//  unsigned __sp; \
//  asm("ldw %0, dp[_sp]" : "=r"(__sp)); \
//  threadSP = __sp - (threadID * THREAD_STACK_SPACE); \
//} while(0)

// Given a resource id, return the node identifer
#if defined(XS1_G)
#define GET_NODE_ID(resID, nodeID) \
do { \
  unsigned int __n; \
  asm("bitrev %0, %1" : "=r"(__n) : "r"(resID)); \
  nodeID = __n & 0xFF; \
} while(0)
#elif defined(XS1_L)
#define GET_NODE_ID(resID, nodeID) \
do { \
  nodeID = (resID >> 16 & 0xFFFF) / NUM_CORES_PER_NODE; \
} while(0)
#endif

// Given a resource id, return the core identifier
#if defined(XS1_G)
#define GET_CORE_ID(resID, coreID) \
do { \
  coreID = (resID >> 16) & 0xFF; \
} while(0)
#elif defined(XS1_L)
#define GET_CORE_ID(resID, coreID) \
do { \
  coreID = (resID >> 16 & 0xFFFF) % NUM_CORES_PER_NODE; \
} while(0)
#endif

// Given a resource id, return the global core label.
#if defined(XS1_G)
#define GET_GLOBAL_CORE_ID(resID, coreID) \
do { \
  coreID = (GET_NODE_ID(resID) * NUM_CORES_PER_NODE) + GET_CORE_ID(resID); \
} while(0)
#elif defined(XS1_L)
#define GET_GLOBAL_CORE_ID(resID, coreID) \
do { \
  coreID = resID >> 16 & 0xFFFF; \
} while(0)
#endif

// Disable interrupts
#define DISABLE_INTERRUPTS() \
do { \
  asm("clrsr " S(SR_IEBLE)); \
} while(0)

// Enable interrupts
#define ENABLE_INTERRUPTS() \
do { \
  asm("setsr " S(SR_IEBLE)); \
} while(0)

// Synchronised output


unsigned memAlloc(unsigned int size);
void memFree(unsigned p);

void readSSwitchReg(int coreId, int reg, unsigned &data);
void writeSSwitchReg(int coreId, int reg, unsigned data);

#endif
