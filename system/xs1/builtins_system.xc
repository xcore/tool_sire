#define _POLYNOMIAL 0xEDB88320

int _rand() {
  crc32(_seed, ~0, _POLYNOMIAL);
  return _seed;
}
