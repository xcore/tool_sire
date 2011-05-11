#include "builtins.h"

#define _IBITS 8
#define _DBITS 24

typedef int f8_24;
typedef signed long long int64;

// 8.24 fixed point multiply.
int _mulf8_24(f8_24 x, f8_24 y) {
    int64 r = (int64) x * (int64) y;
    r = r + ((r & 1<<(_DBITS-1))<<1);
    return (int) (r >> _DBITS);
}

// 8.24 fixed point divide.
int _divf8_24(f8_24 x, f8_24 y) {
    return (int) (((int64) x << _DBITS) / (int64) y);
}

