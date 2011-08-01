// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <stdlib.h>
#include "memory.h"

// Allocate a chunk of memory of size bytes.
unsigned mallocWrapper(unsigned int size) {
  int *p = malloc(size);
  if (p == NULL) {
    return 0;
  }
  else {
    return (unsigned) p;
  }
}

// Free a chunk of memory given by the ptr
void freeWrapper(unsigned p) {
  free((void *) p);
}

