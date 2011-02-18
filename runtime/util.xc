#include <xs1.h>
#include "util.h"
#include "definitions.h"

// Create a channel resource identifier with a particular count
//static inline
unsigned chanResId(unsigned id, int counter) {
    return destResId(id) | counter << 8;    
}

// Generate a configuration resource identifier
//static inline
unsigned genCRI(unsigned nodeId) {
    return nodeId << 24 | XS1_CT_SSCTRL << 8 | 12;
}

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

// Get the id of this thread
unsigned getThreadId() {
    unsigned threadId;
    asm("get r11, id\n\t"
        "mov %0, r11" : "=r"(threadId) :: "r11");
    return threadId;
}

// Given a resource id, return the node identifer
unsigned getNode(unsigned resId) {
    unsigned int n;
    asm("bitrev %0, %1" : "=r"(n) : "r"(resId));
    return n & 0xFF;
}

// Given a resource id, return the core label. I.e. not separate node and core
// values
unsigned getCore(unsigned resId) {
    unsigned int n, c;
    asm("bitrev %0, %1" : "=r"(n) : "r"(resId));
    n &= 0xFF;
    c = (resId >> 16) & 0xFF;
    return (n * CORES_PER_NODE) + c;
}

// Create the channel identifier (for channel 0) for a given destination
// The node bits are written in MSB first, so need to be reversed
unsigned destResId(unsigned dest) {
    unsigned n = dest/CORES_PER_NODE;
    asm("bitrev %0, %1" : "=r"(n) : "r"(n));
    return n | (dest % CORES_PER_NODE) << 16 | 0x2;
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


