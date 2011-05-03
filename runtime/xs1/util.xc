// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "util.h"

// Raise an exception in the event of an error
//static inline
void raiseException() {
    asm("ldc r11, 0\n\tecallf r11" ::: "r11");
}

// Exception error
//static inline
void error() {
    asm("waiteu");
}

// Write a switch configuration register
void cfgWrite(unsigned c, unsigned value) {

    unsigned v;

    // WRITEC token
    asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_WRITEC));

    // NodeId, CoreId, ChanId
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

    // Switch address (register 3)
    asm("outt  res[%0], %1" :: "r"(c), "r"(0));
    asm("outt  res[%0], %1" :: "r"(c), "r"(3));

    // Data to write
    asm("out res[%0], %1" :: "r"(c), "r"(value));

    // End of message
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

    // Receive acknowledgement
    asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
}

// Read a switch configuration register
unsigned cfgRead(unsigned c) {

    unsigned value, v;

    // READC
    asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_READC));

    // NodeId, CoreId, ChanId
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

    // Switch address (register 3)
    asm("outt  res[%0], %1" :: "r"(c), "r"(0));
    asm("outt  res[%0], %1" :: "r"(c), "r"(3));

    // End of message
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

    // Receive ACK and data
    asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
    asm("in %0, res[%1]" : "=r"(value) : "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));

    return value;
}


