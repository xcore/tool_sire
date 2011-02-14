#include <xs1.h>
#include "definitions.h"
#include "globals.h"
#include "system.h"
#include "util.h"
#include "guest.h"

void initHostConnection(unsigned, unsigned);
void sendClosure       (unsigned, unsigned[], unsigned[], int[]);
void sendHeader        (unsigned, int, int);
void sendArguments     (unsigned, int, unsigned[], unsigned[], int[]);
void sendProcedures    (unsigned, int, int, unsigned[]);
void waitForCompletion (unsigned, int);
void receiveResults    (unsigned, int, unsigned[], int[]);

unsigned permDest(unsigned d) {
    if(d >= 16 && d <= 31)
        return d + 16;
    if(d >= 32 && d <= 47)
        return d - 16;
    return d;
}

// Migrate a procedure to a destination
void _migrate(unsigned dest, unsigned closure[]) {
    
    unsigned args[NUM_ARGS];
    int len[NUM_ARGS];
    unsigned threadId = getThreadId();
    unsigned c = spawnChan[threadId];
    unsigned destId = destResId(dest);

    // Initialise the connection with the host
    initHostConnection(c, destId);
    
    // Transfer closure data
    sendClosure(c, closure, args, len);
    
    // Wait for ececution to complete
    waitForCompletion(c, threadId);

    // Receive any results
    receiveResults(c, closure[CLOSURE_NUM_ARGS], args, len);
}

// Initialise the connection with the host thread
void initHostConnection(unsigned c, unsigned destId) {

    // Set the channel destination
    SETD(c, destId);

    // Initiate conneciton by sending chanResId
    //OUTCT_END(c);
    OUT(c, c);
    CHKCT_END(c);

    // Close the current channel connection 
    CHKCT_END(c);
    OUTCT_END(c);
    
    // Open new connection with spawned thread
    CHKCT_END(c);
    destId = IN(c);
    SETD(c, destId);
    OUTCT_END(c);
}

// Send a closure
// NOTE: xcc adds in array bounds checking which assumes array length is an
// implicit argument
void sendClosure(unsigned c, unsigned closure[], 
    unsigned args[], int len[]) {
   
    unsigned numArgs  = closure[CLOSURE_NUM_ARGS];
    unsigned numProcs = closure[CLOSURE_NUM_PROCS];

    // Send the header
    sendHeader(c, numArgs, numProcs);

    // Send arguments
    sendArguments(c, numArgs, closure, args, len);

    // Send the children
    sendProcedures(c, numProcs, CLOSURE_ARGS+2*numArgs, closure);
}

// Send the header
void sendHeader(unsigned c, int numArgs, int numProcs) {
    
    OUTS(c, numArgs);
    OUTS(c, numProcs);
}

// Send the guest procedures arguments
#pragma unsafe arrays
void sendArguments(unsigned c, int numArgs, unsigned closure[],
    unsigned args[], int len[]) {

    unsigned addr, value;
    int cIndex;

    for(int i=0; i<numArgs; i++) {
        
        cIndex = CLOSURE_ARGS+i*2;
        len[i] = closure[cIndex];
        args[i] = closure[cIndex+1];

        // Send the argument length
        OUTS(c, len[i]);
        
        // Send a single value
        if(len[i] == 1) {
            OUTS(c, closure[cIndex+1]);
        }
        // Send an array
        else {
            for(int j=0; j<len[i]; j++) {
                asm("ldw %0, %1[%2]" : "=r"(value) : "r"(args[i]), "r"(j));
                OUTS(c, value);
            }
        }
    }
}

// Send the guest procedure and any children it has
// NOTE: the asm below causes bug in xcc optimisation
/*asm("ldaw r11, cp[0]\n\t"
    "ldw %0, r11[%1]"
    :  "=r"(procAddr) : "r"(procIndex) : "r11");*/
#pragma unsafe arrays
void sendProcedures(unsigned c, int numProcs, int procOff, unsigned closure[]) {
    
    unsigned procIndex, procAddr, procSize, inst;
    unsigned jumpTable, cp;
    
    // Get address of cp
    asm("ldaw r11, cp[0]\n\t"
        "mov %0, r11" : "=r"(cp) :: "r11");

    for(int i=0; i<numProcs; i++) {

        // Load the procAddress and procSize from the index
        procIndex = closure[procOff+i];
        procSize  = _sizetab[procIndex];
    
        // Jump index and size
        OUTS(c, procIndex);
        OUTS(c, procSize);
        OUTS(c, _frametab[procIndex]);
    
        // TODO: check here whether the host already has this procedure

        // Instructions
        asm("ldw %0, %1[%2]" : "=r"(procAddr) : "r"(cp), "r"(procIndex));
        
        for(int j=0; j<procSize/4; j++) {
            asm("ldw %0, %1[%2]" : "=r"(inst) : "r"(procAddr), "r"(j));
            //asm("out res[%0], %1" :: "r"(c), "r"(inst));
            OUTS(c, inst);
        }
    }
}

// Wait for the completion of the migrated procedure
void waitForCompletion(unsigned c, int threadId) {
    
    // Only thread 0 can interrupt here
    // Enable interrupts and wait for either the COMPLETED control token or for
    // another BEGIN token
    /*if(threadId == 0) {
        asm("setc res[%0], " XS1_SETC_IE_MODE_INTERRUPT :: "r"(mSpawnChan));
        asm("setsr " SR_IEBLE);
        
        // * Will interrupt into kernel here which will acknowledge COMPLETED and
        // hand back to here *
    }*/
    
    // (wait to) Acknowledge completion
    asm("chkct res[%0], " S(CT_COMPLETED) :: "r"(c));    
    asm("outct res[%0], " S(CT_COMPLETED) :: "r"(c));    
            
    // Acknowledge end
    CHKCT_END(c);
    OUTCT_END(c);
}

// Receive any array arguments that may have been updated by the migrated
// procedure 
#pragma unsafe arrays
void receiveResults(unsigned c, int numArgs, unsigned args[], int len[]) {

    unsigned value, length;

    for(int i=0; i<numArgs; i++) {
        length = len[i];
        if(length > 1) {

            for(int j=0; j<length; j++) {
                // Note can write this in one asm using r11 (but causes xcc fail)
                //asm("in %0, res[%1]" : "=r"(value) : "r"(c));
                value = INS(c);
                asm("stw %0, %1[%2]" :: "r"(value), "r"(args[i]), "r"(j));
            }
        }
    }
}

