// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <stdlib.h>
#include "memory.h"

// Allocate a chunk of memory of size bytes.
unsigned memAlloc(unsigned int size) {
    return (unsigned) malloc(size);
}

// Free a chunk of memory given by the ptr
void memFree(unsigned ptr) {
    free((void *) ptr);
}


