#define _POLYNOMIAL 0xEDB88320
#include <math.h>

#define _TIME(v) \
do {\
  asm("getr r11, " S(XS1_RES_TYPE_TIMER) ";" \
    "in %0, res[r11];" \
    "freer res[r11]" : "=r"(v) :: "r11");\
} while(0)

int crc(int x) {
  unsigned y = (unsigned) x;
  crc32(y, ~0, _POLYNOMIAL);
  return y;
}

int rand() {
  int mask;
  crc32(_seed, ~0, _POLYNOMIAL);
  return (int) ((int)_seed < 0) ? -(unsigned)_seed : _seed;
}
