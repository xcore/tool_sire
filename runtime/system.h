#ifndef SYSTEM_H
#define SYSTEM_H

extern void _setupthread();
extern void _connect(unsigned, int, int);

void initSystem();
void resetChannels();
void masterSync();
void slaveSync();
void yeild();
void idle();
void wait();

#endif
