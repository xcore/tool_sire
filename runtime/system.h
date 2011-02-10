#ifndef SYSTEM_H
#define SYSTEM_H

extern void _setupthread();
extern void _connect(unsigned, int, int);

static inline 
void ACQUIRE_LOCK(unsigned l) {
    asm("in r11, res[%0]" :: "r"(l) : "r11");
}

static inline 
void RELEASE_LOCK(unsigned l) {
    asm("out res[%0], r11" :: "r"(l) : "r11");
}

void initSystem();
void resetChannels();
void masterSync();
void slaveSync();
void idle();
void slaveYeild();

#endif
