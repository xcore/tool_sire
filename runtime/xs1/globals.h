// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef GLOBALS_H
#define GLOBALS_H

#include "system/xs1/definitions.h"

// External globals
extern unsigned mSpawnChan;
extern unsigned spawnChan[MAX_THREADS];
extern unsigned progChan[NUM_PROG_CHANS];  
extern unsigned _numThreads;
extern unsigned _numThreadsLock;
extern unsigned _sp;
extern unsigned _sizetab[SIZE_TABLE_SIZE];
extern unsigned _frametab[FRAME_TABLE_SIZE];

// External functions
extern void excepHandler(void);
extern void _main(void);

#endif
