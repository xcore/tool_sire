// File IO
void _readnextint(int fd, int &v) {
  int off;
  off = _read(fd, (v, char[]), sizeof(int));
  ASSERT(off != -1);
}

void _writenextint(int fd, int &v) {
  int off;
  off = _write(fd, (v, char[]), sizeof(int));
  ASSERT(off != -1);
}

#define _OPEN(f, m)   _open(f, m, S_IREAD | S_IWRITE)
#define _READ(fd, v)  _readnextint(fd, v) 
#define _WRITE(fd, v) _writenextint(fd, v)
#define _CLOSE(fd)    _close(fd)
