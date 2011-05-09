#include "builtins.h"

#define _FBITS 24

/*
 * 8.24 fixed point multiply.
 */
int _mulf8_24(int x, int y) {
    sint64 temp = (sint64) x * (sint64) y;
    int r = temp + ((temp & 1<<(32-_FBITS-1))<<1);
    return r >> _FBITS;
}

/*
 * 8.24 fixed point divide.
 */
int _divf8_24(int x, int y) {
    return (sint64) (x << (32-_FBITS)) / (sint64) y;
}

