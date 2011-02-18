#ifndef UTIL_H
#define UTIL_H

#include "definitions.h"

// String wrapper
#define S_(x) #x
#define S(x) S_(x)

static inline
void SETD(unsigned c, unsigned dest) {
   asm("setd res[%0], %1" :: "r"(c), "r"(dest));
}

static inline
void OUTCT_END(unsigned c) {
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
}

static inline
void CHKCT_END(unsigned c) {
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
}

static inline
unsigned IN(unsigned c) {
    unsigned v;
    asm("in %0, res[%1]" : "=r"(v) : "r"(c));
    return v;
}

static inline
void OUT(unsigned c, unsigned v) {
    asm("out res[%0], %1" :: "r"(c), "r"(v));
}

static inline
void OUTS(unsigned c, unsigned v) {
   asm("outct res[%0], " S(XS1_CT_END) ";"
       "chkct res[%0], " S(XS1_CT_END) ";"
       "out   res[%0], %1;" 
       "outct res[%0], " S(XS1_CT_END) ";"
       "chkct res[%0], " S(XS1_CT_END) ";"
       :: "r"(c), "r"(v));
}

static inline
unsigned INS(unsigned c) {
    unsigned v;
    asm("chkct res[%1], " S(XS1_CT_END) ";" 
        "outct res[%1], " S(XS1_CT_END) ";" 
        "in    %0, res[%1];"
        : "=r"(v) : "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) ";"
        "outct res[%0], " S(XS1_CT_END) ";"
        :: "r"(c));
    return v;
}

static inline
unsigned GETR_CHANEND() {
   unsigned c;
   asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
   return c;
}

static inline
unsigned GETR_SYNC() {
   unsigned c;
   asm("getr %0, " S(XS1_RES_TYPE_SYNC) : "=r"(c));
   return c;
}

static inline
unsigned GET_ASYNC_THREAD() {
   unsigned t;
   asm("getr %0, " S(XS1_RES_TYPE_THREAD) : "=r"(t));
   return t;
}

static inline
unsigned GET_SYNC_THREAD(unsigned sync) {
   unsigned t;
   asm("getst %0, res[%1]" : "=r"(t) : "r"(sync));
   return t;
}

static inline
unsigned GETR_LOCK() {
   unsigned c;
   asm("getr %0, " S(XS1_RES_TYPE_LOCK) : "=r"(c));
   return c;
}

static inline 
void ACQUIRE_LOCK(unsigned l) {
    asm("in r11, res[%0]" :: "r"(l) : "r11");
}

static inline 
void RELEASE_LOCK(unsigned l) {
    asm("out res[%0], r11" :: "r"(l) : "r11");
}

unsigned chanResId(unsigned, int);
unsigned genCRI(unsigned);
void     raiseException();
void     error();
unsigned getThreadId();
unsigned getNode(unsigned);
unsigned getCore(unsigned);
unsigned destResId(unsigned);

void     cfgWrite(unsigned, unsigned);
unsigned cfgRead(unsigned);

#endif
