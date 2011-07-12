// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef GLOBALS_H
#define GLOBALS_H

#include "system/xs1/definitions.h"

// Seperate master and slave versions
extern unsigned _sizetab[SIZE_TABLE_SIZE];

// External functions
extern void excepHandler(void);
extern void _main(void);

/* These variables are declared in globals.c. */

// Global data
extern unsigned _numthreads;
extern unsigned _numthreads_lock;
extern unsigned _sp;

// Processor allocation
extern unsigned spawn_master;
extern unsigned spawn_chans[MAX_THREADS];

// Connection setup and management
extern unsigned conn_master;
extern unsigned conn_buffer[CONN_BUFFER_SIZE];
extern unsigned conn_ids[MAX_THREADS];
extern unsigned conn_slaves[MAX_THREADS];

#endif

