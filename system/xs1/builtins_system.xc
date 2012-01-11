#define _POLYNOMIAL 0xEDB88320
#include <math.h>

int time() {
  timer t;
  unsigned v;
  t :> v;
  ASSERT(v < 0x7fffffff);
  return (int) v;
}

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
