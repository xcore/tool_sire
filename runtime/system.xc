#include <xs1.h>
#include "../include/platform.h"
#include "../include/definitions.h"
#include "globals.h"
#include "util.h"
#include "system.h"

void resetChannels();

// Initialse the system: executed once by thread 0, for all threads
#pragma unsafe arrays 
void initSystem() {
    
    unsigned int led, val;

    resetChannels();

    // Get the migration channel and set the event vector
    // ASSERT: channel resource counter must be 0 
    asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(mSpawnChan));
    asm("eeu res[%0]" :: "r"(mSpawnChan));

    // Get channels for each thread
    for(int i=0; i<MAX_THREADS; i++) 
        asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(spawnChan[i]));

    // Get the remaining channels for program use
    for(int i=0; i<NUM_PROG_CHANS; i++)
        asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(progChan[i]));

    // Set the function pointer (fp) to after the data section
    asm("ldap r11, " LBL_END_BSS
        "\n\tmov %0, r11" : "=r"(fp) :: "r11");
    if(fp % 4) fp += 2;

    // Get a lock for the fp variable
    asm("getr %0, " S(XS1_RES_TYPE_LOCK) : "=r"(fpLock));

    // Setup led port
    led = LED_PORT; val = 6;
    asm("setc res[%0], 8" :: "r"(led));
    asm("setclk res[%0], %1" :: "r"(led), "r"(val));
}

// Allocate all remaining channel ends then free them to ensure they are all
// available
void resetChannels() {
    
    unsigned c = 1, c0;
    asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c0));
   
    // Get all remaining channels
    while(c)
        asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c));
    
    // Free all channels
    c = c0 & 0xFFFF00FF;
    for(int i=0; i<MAX_CHANNELS; i++) {
        asm("freer res[%0]" :: "r"(c));
        c += 0x100;
    }
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
void syncCores() {

    unsigned coreId = getCore(mSpawnChan);
    unsigned cri = genCRI(0); // Configuration resource identifier
    unsigned c, v;

    // Get and set a chanend
    c = progChan[0];
    asm("setd res[%0], %1" :: "r"(c), "r"(cri));

    // If core 0 set scratch reg to 1 and wait untill it reaches NUM_CORES
    if(coreId == 0) {
        cfgWrite(c, 1);
        while(cfgRead(c) != NUM_CORES);
    }
    // Otherwise wait until the value reaches coreId and write coreId+1
    else {
        while(cfgRead(c) != coreId);
        cfgWrite(c, coreId+1);
    }
}

// System-wide barrier synchronisation to ensure all cores in consistent state
// before starting program execution. Can assume the first channel returned will
// be number NUM_THREADS+1 as this is always core 0. Also assumes the number of 
// cores in the network is a power of 2
#pragma unsafe arrays
/*void syncCores() {

    unsigned c[DIMENSIONS];
    unsigned destResId, coreId = getCore(mSpawnChan);

    // Get a channel for each dimension and connect it
    for(int i=0; i<DIMENSIONS; i++) {
        destResId = chanResId(HNBR(coreId, i), i+NUM_THREADS+1);
        asm("getr %0, " S(XS1_RES_TYPE_CHANEND) : "=r"(c[i]));
        asm("setd res[%0], %1" :: "r"(c[i]), "r"(destResId));
    }

    // Peform the barrier
    for(int i=0; i<DIMENSIONS; i++) {
        if(coreId > HNBR(coreId, i)) {
            asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c[i]));
            asm("outct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c[i]));
            asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c[i]));
            asm("outct res[%0], " S(XS1_CT_END) :: "r"(c[i]));
        } else {
            asm("outct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c[i]));
            asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c[i]));
            asm("outct res[%0], " S(XS1_CT_END) :: "r"(c[i]));
            asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c[i]));
        }
    }

    // Free the channels
    for(int i=0; i<DIMENSIONS; i++)
        asm("freer res[%0]" :: "r"(c[i]));
}*/

// Connect a channel
void connect(unsigned to, int c1, int c2) {
    unsigned destResId = chanResId(to, PROG_CHAN_OFF+c2);
    asm("setd res[%0], %1" :: "r"(progChan[c1]), 
        "r"(destResId));
}

// Idle (thread 0 only) for the next event to occur
void idle() {

    // Disable interrupts and events, switch to event mode
    asm("clrsr " S(SR_IEBLE) " | " S(SR_EEBLE));
    asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(mSpawnChan));
    
    // Set event vector to idle handler
    asm("ldap r11, " LBL_IDLE_HOST_HANDLER "\n\t"
        "setv res[%0], r11" :: "r"(mSpawnChan) : "r11");

    // Wait for an event on mSpawnChan
    asm("waiteu");
}

// Yeild execution of a thread (only 1-7)
void yeild() {
    asm("freet");
}

