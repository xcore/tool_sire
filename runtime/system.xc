#include <xs1.h>
#include "numcores.h"
#include "definitions.h"
#include "globals.h"
#include "util.h"
#include "system.h"

// Allocate all remaining channel ends then free them to ensure they are all
// available
void resetChannels() {
    
    unsigned c = 1, c0;
    c0 = GETR_CHANEND();

    // Get all remaining channels
    while(c)
        c = GETR_CHANEND();
   
    // Free all channels
    c = c0 & 0xFFFF00FF;
    for(int i=0; i<MAX_CHANNELS; i++) {
        asm("freer res[%0]" :: "r"(c));
        c += 0x100;
    }
}

// Initialse the system: executed once by thread 0, for all threads
#pragma unsafe arrays 
void initSystem() {
    
    unsigned int led;

    // Get the migration channel and set the event vector
    // ASSERT: channel resource counter must be 0 
    mSpawnChan = GETR_CHANEND();
    asm("eeu res[%0]" :: "r"(mSpawnChan));

    // Get channels for each thread
    for(int i=0; i<MAX_THREADS; i++) 
        spawnChan[i] = GETR_CHANEND();

    // Get the remaining channels for program use
    for(int i=0; i<NUM_PROG_CHANS; i++)
        progChan[i] = GETR_CHANEND();

    // Set the function pointer (fp) to after the data section
    asm("ldap r11, " LABEL_END_BSS
        "\n\tmov %0, r11" : "=r"(_fp) :: "r11");
    if(_fp % 4) _fp += 2;

    // Get a lock for the fp variable
    _fpLock = GETR_LOCK();
    _spLock = GETR_LOCK();

    // Setup led port
    led = LED_PORT;
    asm("setc res[%0], 8" :: "r"(led));
    asm("setclk res[%0], %1" :: "r"(led), "r"(6));
}

// Write a switch configuration register
void cfgWrite(unsigned c, unsigned value) {

    unsigned v;

    // WRITEC token
    asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_WRITEC));

    // NodeId, CoreId, ChanId
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

    // Switch address (register 3)
    asm("outt  res[%0], %1" :: "r"(c), "r"(0));
    asm("outt  res[%0], %1" :: "r"(c), "r"(3));

    // Data to write
    asm("out res[%0], %1" :: "r"(c), "r"(value));

    // End of message
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

    // Receive acknowledgement
    asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
}

// Read a switch configuration register
unsigned cfgRead(unsigned c) {

    unsigned value, v;

    // READC
    asm("outct res[%0], %1" :: "r"(c), "r"(XS1_CT_READC));

    // NodeId, CoreId, ChanId
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 24));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 16));
    asm("outt  res[%0], %1" :: "r"(c), "r"(c >> 8));

    // Switch address (register 3)
    asm("outt  res[%0], %1" :: "r"(c), "r"(0));
    asm("outt  res[%0], %1" :: "r"(c), "r"(3));

    // End of message
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

    // Receive ACK and data
    asm("chkct res[%0], " S(XS1_CT_ACK) :: "r"(c));
    asm("in %0, res[%1]" : "=r"(value) : "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));

    return value;
}

// Ensure all cores are in a consistent state before completing initialisation
// Assume that master is always core 0
void masterSync() {

    if (NUM_CORES > 1) {

        unsigned coreId = getCore(mSpawnChan);
        // Configuration resource identifier
        unsigned cri = genCRI(0); 
        unsigned c, v;
        unsigned t;

        // Get and set a chanend
        c = progChan[0];
        asm("setd res[%0], %1" :: "r"(c), "r"(cri));

        // If core 0 set scratch reg to 1 and wait untill it reaches NUM_CORES
        cfgWrite(c, 1);
        while(cfgRead(c) != NUM_CORES)
            continue;
    }
}

// Ensure all cores are in a consistent state before completing initialisation
void slaveSync() {

    unsigned coreId = getCore(mSpawnChan);
    // Configuration resource identifier
    unsigned cri = genCRI(0); 
    unsigned c, v;

    // Get and set a chanend
    c = progChan[0];
    asm("setd res[%0], %1" :: "r"(c), "r"(cri));

    // Otherwise wait until the value reaches coreId and write coreId+1
    while(cfgRead(c) != coreId)
        continue;
    cfgWrite(c, coreId+1);
}

// Connect a channel
void _connect(unsigned to, int c1, int c2) {
    unsigned destResId = chanResId(to, PROG_CHAN_OFF+c2);
    //asm("setd res[%0], %1" :: "r"(progChan[c1]), "r"(destResId));
    SETD(progChan[c1], destResId);
}

// Idle (thread 0 only) for the next event to occur
void idle() {

    // Disable interrupts and events, switch to event mode
    asm("clrsr " S(SR_IEBLE) " | " S(SR_EEBLE));
    asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(mSpawnChan));
    
    // Set event vector to idle handler
    asm("ldap r11, " LABEL_IDLE_HOST_HANDLER "\n\t"
        "setv res[%0], r11" :: "r"(mSpawnChan) : "r11");

    // Wait for an event on mSpawnChan
    asm("waiteu");
}

// Yeild execution of a thread (only 1-7), set as the value of the link register
// of an asynchronous thread (created by the host).
void slaveYeild() {
    asm("freet");
}


