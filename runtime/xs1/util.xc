// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "memory.h"
#include "util.h"

unsigned memAlloc(unsigned int size) {
  unsigned p = mallocWrapper(size);
  if (p == 0) {
    EXCEPTION(et_INSUFFICIENT_MEMORY);
  } else {
    return p;
  }
}

void memFree(unsigned p) {
  freeWrapper(p);
}

void readSSwitchReg(int coreId, int reg, unsigned &data) {

  // Get and set a chanend
  unsigned switchCRI = GEN_CONFIG_RI(coreId); 
  unsigned c = GETR_CHANEND();
  asm("setd res[%0], %1" :: "r"(c), "r"(switchCRI));

  // READC
  asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_READC));

  // NodeId, CoreId, ChanId
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

  // Switch address (register)
  asm("outt  res[%0], %1" :: "r"(c), "r"(reg >> 8));
  asm("outt  res[%0], %1" :: "r"(c), "r"(reg));

  // End of message
  asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

  // Receive ACK and data
  asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
  asm("in %0, res[%1]" : "=r"(data) : "r"(c));
  asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));

  // Free the channel end
  asm("freer res[%0]" :: "r"(c));
}

void writeSSwitchReg(int coreId, int reg, unsigned data) {

  // Get and set a chanend
  unsigned switchCRI = GEN_CONFIG_RI(coreId); 
  unsigned c = GETR_CHANEND();
  asm("setd res[%0], %1" :: "r"(c), "r"(switchCRI));

  // WRITEC token
  asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_WRITEC));

  // NodeId, CoreId, ChanId
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
  asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

  // Switch address (register)
  asm("outt  res[%0], %1" :: "r"(c), "r"(reg >> 8));
  asm("outt  res[%0], %1" :: "r"(c), "r"(reg));

  // Data to write
  asm("out res[%0], %1" :: "r"(c), "r"(data));

  // End of message
  asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

  // Receive acknowledgement
  asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
  asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));

  // Free the channel end
  asm("freer res[%0]" :: "r"(c));
}

