#include <xs1.h>
#include "definitions.h"
#include "language.h"
#include "globals.h"
#include "system.h"
#include "util.h"
#include "host.h"
#include "memory.h"

extern void runProcedure      (unsigned int, int, int, unsigned int[]);

void       initGuestConnection(unsigned, unsigned);
{int, int} receiveClosure     (unsigned, t_argument[], unsigned[], int[]);
{int, int} receiveHeader      (unsigned);
void       receiveArguments   (unsigned, int, t_argument[], unsigned[], int[]);
int        receiveProcedures  (unsigned, int);
void       informCompleted    (unsigned, unsigned);
void       sendResults        (unsigned, int, t_argument[], unsigned[], int[]);
void       newAsyncThread     (unsigned);

// Setup and initialise execution of a new thread
void runThread(unsigned senderId) {
    
    t_argument argTypes[NUM_ARGS];
    unsigned argValues[NUM_ARGS];
    int argLengths[NUM_ARGS];
    int procIndex, numArgs;
    unsigned threadId = getThreadId();
    
    // Initialis1e this (new) thread
    if(threadId != 0) _initThread();

    // Initialise connection with sender
    initGuestConnection(spawnChan[threadId], senderId);
    
    // Receive closure data
    {procIndex, numArgs} = receiveClosure(spawnChan[threadId], argTypes, argValues, argLengths);

    // Run the procedure
    runProcedure(spawnChan[threadId], threadId, procIndex, (argValues, unsigned int[]));

    // Complete the migration by sending back any results
    informCompleted(spawnChan[threadId], senderId);
    
    // Send any results back
    sendResults(spawnChan[threadId], numArgs, argTypes, argValues, argLengths);
}

// Initialise guest connection with this thread 0 as host.
unsigned setHost() {
    
    unsigned senderId;
    
    // Connect to the sender and receive their id 
    senderId = IN(mSpawnChan);
    SETD(mSpawnChan, senderId);
    
    // Close mSpawnChan connection
    OUTCT_END(mSpawnChan);
    CHKCT_END(mSpawnChan);

    return senderId;
}

// Host an incoming procedure when thread 0 is BUSY. During this time, events
// and interrupts are disabled and more requests may arrive. get_requests deals
// with this.
void spawnHost() {

    unsigned senderId;
    
    // Connect to the sender and receive their id 
    senderId = IN(mSpawnChan);
    SETD(mSpawnChan, senderId);

    // Close the connection
    CHKCT_END(mSpawnChan);
    OUTCT_END(mSpawnChan);

    // Give the next thread some space and launch it
    newAsyncThread(senderId);
}

// Initialise the conneciton with the sender
// Communication performed on a slave spawn channel
void initGuestConnection(unsigned c, unsigned senderId) {
    
    // Send the new CRI
    SETD(c, senderId);
    OUT(c, c);

    // Sync and close the conncection
    OUTCT_END(c);
    CHKCT_END(c);
}

// Receive a closure
{int, int} receiveClosure(unsigned c, 
        t_argument argTypes[], unsigned argValues[], int argLengths[]) {
  
    int numArgs, numProcs, index;
    unsigned inst, jumpTable;

    // Receive the header
    {numArgs, numProcs} = receiveHeader(c);

    // Receive arguments
    receiveArguments(c, numArgs, argTypes, argValues, argLengths);

    // Receive the children
    index = receiveProcedures(c, numProcs);

    return {index, numArgs};
}

// Receive the closure header
{int, int} receiveHeader(unsigned c) {
    
    int numArgs = INS(c);
    int numProcs = INS(c);

    return {numArgs, numProcs};
}

// Receive the arguments to the migrated procedure
#pragma unsafe arrays
void receiveArguments(unsigned c, int numArgs, 
        t_argument argTypes[], unsigned argValues[], int argLengths[]) {

    // For each argument
    for(int i=0; i<numArgs; i++) {

        // Receive the argument type
        argTypes[i] = INS(c);

        switch(argTypes[i]) {
        
        case t_arg_ALIAS:
            // Allocate space for the array
            argLengths[i] = INS(c);
            argValues[i] = memAlloc(argLengths[i]);
            
            // Receive each element of the array and write straight to memory
            for(int j=0; j<argLengths[i]; j++) {
                unsigned value = INS(c);
                asm("stw %0, %1[%2]" :: "r"(value), "r"(argValues[i]), "r"(j));
            }
            break;
        
        case t_arg_VAR:
            // Allocate space for the var and store it
            argValues[i] = memAlloc(BYTES_PER_WORD);
            argLengths[i] = 1;
            {unsigned value = INS(c);
            asm("stw %0, %1[%2]" :: "r"(value), "r"(argValues[i]), "r"(0));}
            break;
        
        case t_arg_VAL:
            // Assign the val value directly
            argValues[i] = INS(c);
            argLengths[i] = 1;
            break;
        
        default:
            break;
        }
    }
}

// Receive the procedure and any children
#pragma unsafe arrays
int receiveProcedures(unsigned c, int numProcs) {
    
    int index;
    unsigned jumpTable;

    // Load jump table address
    asm("ldaw r11, cp[0] ; mov %0, r11" : "=r"(jumpTable) :: "r11");

    for(int i=0; i<numProcs; i++) {
        
        // Jump index, size and frame size
        int procIndex = INS(c);
        if(i == 0) index = procIndex;

        // If we don't have the procedure, receive it
        if (_sizetab[procIndex] == 0) {
            
            int procSize;
            int frameSize;
            unsigned ptr;
            
            OUTS(c, 1);
            procSize = INS(c);
            frameSize = INS(c);
            ptr = memAlloc(procSize);

            // Instructions
            for(int j=0; j<procSize/4; j++) {
                unsigned inst = INS(c);
                asm("stw %0, %1[%2]" :: "r"(inst), "r"(ptr), "r"(j));
            }
         
            // Patch jump table entry
            asm("stw %0, %1[%2]" :: "r"(ptr), "r"(jumpTable), "r"(procIndex));

            // Update the procSize and frameSize entry
            _sizetab[procIndex] = procSize;
            _frametab[procIndex] = frameSize;
        }
        else {
            OUTS(c, 0);
        }
    }

    return index;
}

// Complete the migration of the procedure by informing the sender and
// transmitting back any results
void informCompleted(unsigned c, unsigned senderId) {
    
    // Set the channel destination (as it may have been set again by a nested on)
    SETD(c, senderId);

    // Signal the completion of execution
    asm("outct res[%0], " S(CT_COMPLETED) :: "r"(c));
    asm("chkct res[%0], " S(CT_COMPLETED) :: "r"(c));
    
    // End
    OUTCT_END(c);
    CHKCT_END(c);
}

// Send back any arrays that may have been updated by the execution of
// the migrated procedure
#pragma unsafe arrays
void sendResults(unsigned c, int numArgs, 
    t_argument argTypes[], unsigned argValues[], int argLengths[]) {

    unsigned value, length, addr;
    
    for(int i=0; i<numArgs; i++) {
        
        switch(argTypes[i]) {
        
        case t_arg_ALIAS:
            for(int j=0; j<argLengths[i]; j++) {
                asm("ldw %0, %1[%2]" : "=r"(value) : "r"(argValues[i]), "r"(j));
                OUTS(c, value);
            }
            break;
        
        case t_arg_VAR:
            asm("ldw %0, %1[%2]" : "=r"(value) : "r"(argValues[i]), "r"(0));
            OUTS(c, value);
            break;
        
        case t_arg_VAL:
            break;
        
        default:
            break;
        }
    }
}

// Spawn a new asynchronous thread
void newAsyncThread(unsigned senderId) {
    
    // Claim a thread
    unsigned t = claimAsyncThread();
    
    // Claim a stack slot
    unsigned sp = claimStackSlot((t>>8) && 0xF);
    
    // Initialise cp, dp, sp, pc, lr
    asm("ldaw r11, cp[0] "
        "; init t[%0]:cp, r11" ::"r"(t) : "r11");
    asm("ldaw r11, dp[0] "
        "; init t[%0]:dp, r11" :: "r"(t) : "r11");
    asm("init t[%0]:sp, %1" :: "r"(t), "r"(sp));
    asm("ldap r11, runThread" 
        " ; init t[%0]:pc, r11" :: "r"(t) : "r11");
    asm("ldap r11, slaveYeild"  
        " ; init t[%0]:lr, r11" :: "r"(t) : "r11");
                             
    // Set senderId arg 
    asm("set t[%0]:r0, %1"  :: "r"(t), "r"(senderId));

    // Touch remaining GPRs
    asm("set t[%0]:r1, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r2, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r3, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r4, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r5, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r6, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r7, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r8, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r9, %1"  :: "r"(t), "r"(0));
    asm("set t[%0]:r10, %1" :: "r"(t), "r"(0));

    // Start the thread
    asm("start t[%0]" :: "r"(t));
}

// Yeild execution of a slave thread (only 1-7)
void slaveYeild() {
    releaseStackSlot(GET_THREAD_ID());
    releaseThread();
    asm("freet");
}

