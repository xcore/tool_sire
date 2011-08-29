#define _POLYNOMIAL 0xEDB88320

int crc(int x) {
  unsigned y = (unsigned) x;
  crc32(y, ~0, _POLYNOMIAL);
  return y;
}

int rand() {
  crc32(_seed, ~0, _POLYNOMIAL);
  return _seed;
}
