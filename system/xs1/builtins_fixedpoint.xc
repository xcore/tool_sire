#define _FBITS 24
#define ldivu(a,b,c,d,e) asm("ldivu %0,%1,%2,%3,%4" : "=r"(a), "=r"(b) : "r"(c), "r"(d), "r"(e))

// 8.24 fixed point multiply.
int mulf8_24(int a, int b) {
  int h;
  unsigned l;
  {h, l} = macs(a, b, 0, 1<<((32-_FBITS)*2-1));
  return (h << (32-_FBITS)) | (l >> _FBITS);
}

// 8.24 fixed point divide.
int divf8_24(int x, int y) {
  int sgn = 1;
  unsigned int d, d2, r;
  if (x < 0) {
    sgn = -1;
    x = -x;
  }
  if (y < 0) {
    sgn = -sgn;
    y = -y;
  }
  ldivu(d, r, 0, x, y);
  ldivu(d2, r, r, 0, y);
  r = d << _FBITS | (d2 + (1<<(31-_FBITS))) >> (32-_FBITS);
  return r * sgn;
}
