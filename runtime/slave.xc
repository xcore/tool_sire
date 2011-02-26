#include <platform.h>
#include "numcores.h"

extern void _slave(); 

// Mapping function to trigger construction of a NUM_CORES binary. Image on
// core 1 will be replaced by the master image.
int main(void) {
#if NUM_CORES > 1
    par(int i=0; i<NUM_CORES; i++) {
        on stdcore[i] : _slave();
    }
#endif
}
