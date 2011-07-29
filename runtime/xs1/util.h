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
#define S_(x) #x
#define S(x) S_(x)

// Set channel destination
static inline
void SETD(unsigned c, unsigned dest) {
  asm("setd res[%0], %1" :: "r"(c), "r"(dest));
}

// OUTCT CT_END
static inline
void OUTCT_END(unsigned c) {
  asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
}

// CHKCT CT_END
static inline
void CHKCT_END(unsigned c) {
  asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
}

// Asynchronous out
static inline
void OUT(unsigned c, unsigned v) {
  asm("out res[%0], %1" :: "r"(c), "r"(v));
}

// Asynchronous in
static inline
unsigned IN(unsigned c) {
  unsigned v;
  asm("in %0, res[%1]" : "=r"(v) : "r"(c));
  return v;
}

// Synchronised out
static inline
void OUTS(unsigned c, unsigned v) {
  asm("outct res[%0], " S(XS1_CT_END) ";"
      "chkct res[%0], " S(XS1_CT_END) ";"
      "out   res[%0], %1;" 
      "outct res[%0], " S(XS1_CT_END) ";"
      "chkct res[%0], " S(XS1_CT_END) ";"
      :: "r"(c), "r"(v));
}

// Synchronised in
static inline
unsigned INS(unsigned c) {
  unsigned v;
  asm("chkct  res[%1], " S(XS1_CT_END) ";" 
      "outct  res[%1], " S(XS1_CT_END) ";" 
      "in %0, res[%1];"
      : "=r"(v) : "r"(c));
  asm("chkct  res[%0], " S(XS1_CT_END) ";"
      "outct  res[%0], " S(XS1_CT_END) ";"
      :: "r"(c));
  return v;
}

// Get a chanend
static inline
unsigned GETR_CHANEND() {
  unsigned c;
  asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
  return c;
}

// Get a synchroniser
static inline
unsigned GETR_SYNC() {
  unsigned c;
  asm("getr %0, " S(XS1_RES_TYPE_SYNC) : "=r"(c));
  return c;
}

// Get an asynchronous thread
static inline
unsigned GETR_ASYNC_THREAD() {
  unsigned t;
  asm("getr %0, " S(XS1_RES_TYPE_THREAD) : "=r"(t));
  return t;
}

// Get a synchronous thread
static inline
unsigned GETR_SYNC_THREAD(unsigned sync) {
  unsigned t;
  asm("getst %0, res[%1]" : "=r"(t) : "r"(sync));
  return t;
}

// Get a lock
static inline
unsigned GETR_LOCK() {
  unsigned c;
  asm("getr %0, " S(XS1_RES_TYPE_LOCK) : "=r"(c));
  return c;
}

// Acquire lock
static inline 
void ACQUIRE_LOCK(unsigned l) {
  asm("in r11, res[%0]" :: "r"(l) : "r11");
}

// Release a lock
static inline 
void RELEASE_LOCK(unsigned l) {
  asm("out res[%0], r11" :: "r"(l) : "r11");
}

// Free a resource
static inline
void FREER(unsigned r) {
  asm("freer res[%0]" :: "r"(r));
}

// Get a thread id from a resource identifier
static inline
unsigned THREAD_ID(unsigned resId) {
  return (resId >> 8) & 0xFF;
}

// Create the channel identifier (for channel 0) for a given destination
// The node bits are written in MSB first, so need to be reversed
static inline
unsigned GEN_CHAN_RI_0(unsigned dest) {
  unsigned n = dest / NUM_CORES_PER_NODE;
  asm("bitrev %0, %1" : "=r"(n) : "r"(n));
  return n | (dest % NUM_CORES_PER_NODE) << 16 | 0x2;
}


// Create a channel resource identifier with a particular count
static inline
unsigned GEN_CHAN_RI(unsigned id, int counter) {
  return GEN_CHAN_RI_0(id) | counter << 8;  
}

// Generate a configuration resource identifier
static inline
unsigned GEN_CONFIG_RI(unsigned nodeId) {
  return nodeId << 24 | XS1_CT_SSCTRL << 8 | 12;
}

// Get the current thread id
static inline
unsigned GET_THREAD_ID() {
   int id;
   asm("get r11, id ; mov %0, r11" : "=r"(id) :: "r11");
   return id;
}

// Given a resource id, return the node identifer
static inline
unsigned GET_NODE_ID(unsigned resId) {
  unsigned int n;
  asm("bitrev %0, %1" : "=r"(n) : "r"(resId));
  return n & 0xFF;
}

// Given a resource id, return the core identifier
static inline
unsigned GET_CORE_ID(unsigned resId) {
  return (resId >> 16) & 0xFF;
}

// Given a resource id, return the global core label.
static inline
unsigned GET_GLOBAL_CORE_ID(unsigned resId) {
  return (GET_NODE_ID(resId) * NUM_CORES_PER_NODE) + GET_CORE_ID(resId);
}

static inline
void DISABLE_INTERRUPTS()
{ asm("clrsr " S(SR_IEBLE));
}

static inline
void ENABLE_INTERRUPTS()
{ asm("setsr " S(SR_IEBLE));
}

// Raise a runtime exception
static inline
void EXCEPTION(int e) {
  asm("ldc r11, 0 ; ecallf r11" ::: "r11");
}

void readSSwitchReg(int coreId, int reg, unsigned &data);
void writeSSwitchReg(int coreId, int reg, unsigned data);

#endif
