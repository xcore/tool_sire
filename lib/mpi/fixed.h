#ifndef FIXED_H
#define FIXED_H

#define MATHF8_24_BITS 24
#define MATHF8_24_IBITS (32-MATHF8_24_BITS)

#define f8_242int(a) (a >> MATHF8_24_BITS)
#define int2f8_24(a) (a << MATHF8_24_BITS)

typedef int f8_24;

/*
 * Convert a int (val) to fixed point.
 */
static inline f8_24 fix(f8_24 v) {
    return f8_242int(v); 
}

f8_24 div(f8_24 x, f8_24 y);

f8_24 mul(f8_24 x, f8_24 y);

#endif
