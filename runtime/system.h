#ifndef SYSTEM_H
#define SYSTEM_H

extern void initThread();
extern void connect(unsigned, int, int);

void initSystem();
void yeild();
void idle();
void wait();

#endif
