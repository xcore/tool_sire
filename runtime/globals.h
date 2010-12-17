#ifndef GLOBALS_H
#define GLOBALS_H

#include "../include/definitions.h"

// External globals
extern unsigned fp;
extern unsigned sp;
extern unsigned fpLock;
extern unsigned mSpawnChan;
extern unsigned spawnChan[MAX_THREADS];
extern unsigned progChan[NUM_PROG_CHANS];  
extern unsigned sizeTable[SIZE_TAB_SIZE];

// External functions
extern void excepHandler(void);
extern void _main(void);

#endif
