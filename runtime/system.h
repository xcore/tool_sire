#ifndef SYSTEM_H
#define SYSTEM_H

extern void _setupthread();
extern void _connect(unsigned, int, int);

void initSystem();
void resetChannels();
void masterSync();
void slaveSync();
void masterIdle();
void slaveYeild();
unsigned int getAvailThreads();
void incrementAvailThreads();
void decrementAvailThreads();
void claimStackSpace();
void releaseStackSpace();

#endif
