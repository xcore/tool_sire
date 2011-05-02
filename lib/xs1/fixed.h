#ifndef FIXED_H
#define FIXED_H

#include "mathf8_24.h"

/*
 * Convert a int (val) to fixed point.
 */
static inline f8_24 fix(f8_24 v) {
    return f8_242int(v); 
}

/*
 * Division.
 */
static inline f8_24 div(f8_24 x, f8_24 y) {
    return divf8_24(x, y);
}

/*
 * Multiplication.
 */
static inline f8_24 mul(f8_24 x, f8_24 y) {
    return mulf8_24(x, y);
}

#endif
