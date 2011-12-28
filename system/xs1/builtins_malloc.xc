// Malloc/free

int _malloc(unsigned &p, int size) {
  p = memAlloc(size);
  return (p == 0) ? 0 : 1;
}

int _free(unsigned p) {
  memFree(p);
  return 0;
}
