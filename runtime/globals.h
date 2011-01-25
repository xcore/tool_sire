#ifndef GLOBALS_H
#define GLOBALS_H

#include "../include/definitions.h"

// External globals
extern unsigned _fp;
extern unsigned _sp;
extern unsigned fpLock;
extern unsigned mSpawnChan;
extern unsigned spawnChan[MAX_THREADS];
extern unsigned progChan[NUM_PROG_CHANS];  
extern unsigned sizeTable[SIZE_TABLE_SIZE];

// External functions
extern void excepHandler(void);
extern void _main(void);

#endif
