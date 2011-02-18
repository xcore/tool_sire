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
