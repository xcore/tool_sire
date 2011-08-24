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
extern void exceptionHandler();
extern void _main(void);

/* These variables are declared in globals.c. */

// Global data
extern unsigned _sp;
extern unsigned _seed;

// Processor allocation
extern unsigned spawn_master;
extern unsigned thread_chans[MAX_THREADS];

// Connection setup and management

typedef struct
{ unsigned connId;
  unsigned origin;
  unsigned threadCRI;
  unsigned chanCRI;
} conn_req;

extern unsigned conn_master;
extern conn_req conn_buffer[CONN_BUFFER_SIZE];
extern conn_req conn_locals[MAX_THREADS];

#endif

