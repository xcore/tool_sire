// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "system/xs1/definitions.h"
#include "globals.h"

/* These are variables used across the rutime system (on a single core). */

// Global data
unsigned _numthreads;
unsigned _numthreads_lock;
unsigned _sp;

// Processor allocation
unsigned spawn_master;
unsigned spawn_chans[MAX_THREADS];

// Connection setup and management
unsigned conn_master;
unsigned conn_buffer[CONN_BUFFER_SIZE];
unsigned conn_ids[MAX_THREADS];
unsigned conn_slaves[MAX_THREADS];

