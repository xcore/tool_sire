// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef SYSTEM_H
#define SYSTEM_H

extern void _initThread();
int _procid();

// Initialisation
void resetChanends();
void initChanends();
void initCounters();
void initPorts();
void initMemory();

// Synchronisation
void masterSync();
void slaveSync();

// Yeild and idling
void slaveMasterIdle();
void slaveMasterYeild();
void slaveYeild();

// Resource usage
void newAsyncThread(unsigned pc, unsigned arg1, 
    unsigned arg2, unsigned arg3, unsigned arg4);
unsigned int getAvailThreads();
unsigned claimAsyncThread();
unsigned claimSyncThread(unsigned);
void releaseThread();
unsigned claimStackSlot(int);
void releaseStackSlot(int);

#endif
