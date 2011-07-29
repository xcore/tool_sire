// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef SYSTEM_H
#define SYSTEM_H

#include "system/xs1/definitions.h"

// Builtins
int _procId();

// Initialisation
void resetChanends();
void initChanends();
void initPorts();
void initMemory();

// Synchronisation
void masterSync();
void slaveSync();

// Resource access
void newAsyncThread(unsigned pc, unsigned arg1, unsigned arg2, 
    unsigned arg3, unsigned arg4);
int      getAvailThreads();
unsigned claimAsyncThread();
unsigned claimSyncThread(unsigned);
void     releaseThread();
unsigned claimStackSlot(int);
void     releaseStackSlot(int);

#endif

