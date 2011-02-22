#ifndef SYSTEM_H
#define SYSTEM_H

extern void _initThread();
extern void _connect(unsigned, int, int);

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

// Resource usage
unsigned int getAvailThreads();
void incrementAvailThreads();
void decrementAvailThreads();
void claimStackSpace();
void releaseStackSpace();

#endif
