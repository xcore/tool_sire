#include <xs1.h>
#include "../include/definitions.h"
#include "globals.h"
#include "system.h"
#include "util.h"
#include "host.h"

extern void runProcedure      (unsigned int, int, int, unsigned int[]);

void       initGuestConnection(unsigned, unsigned);
{int, int} receiveClosure     (unsigned, unsigned[], int[]);
{int, int} receiveHeader      (unsigned);
void       receiveArguments   (unsigned, int, unsigned[], int[]);
int        receiveProcedures  (unsigned, int, unsigned);
void       informCompleted    (unsigned, unsigned);
void       sendResults        (unsigned, int, unsigned[], int[]);
void       newAsyncThread     (unsigned, unsigned, unsigned);

// Setup and initialise execution of a new thread
void runThread(unsigned senderId) {
    
    unsigned args[NUM_ARGS];
    int len[NUM_ARGS];
    int procIndex, numArgs;
    unsigned threadId = getThreadId();
    unsigned c = spawnChan[threadId];
    
    // Initialis1e this (new) thread
    if(threadId != 0) initThread();

    // Initialise connection with sender
    initGuestConnection(c, senderId);
    
    // Receive closure data
    {procIndex, numArgs} = receiveClosure(c, args, len);

    // Run the procedure
    runProcedure(c, threadId, procIndex, (args, unsigned int[]));

    // Complete the migration by sending back any results
    informCompleted(c, senderId);
    
    // Send any results back
    sendResults(c, numArgs, args, len);
}

// Initialise guest connection with this thread 0 as host
unsigned setHost() {
    
    unsigned senderId;
    
    // Connect to the sender and receive their id 
    asm("chkct  res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(mSpawnChan));
    asm("in %0, res[%1]" : "=r"(senderId): "r"(mSpawnChan));
    asm("setd   res[%0], %1" :: "r"(mSpawnChan), "r"(senderId));
    asm("outct  res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(mSpawnChan));
    
    // Close mSpawnChan connection
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(mSpawnChan));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(mSpawnChan));

    return senderId;
}

// Host an incoming procedure when thread 0 is BUSY
void spawnHost() {

    unsigned senderId, pc;
    
    // Connect to the sender and receive their id 
    asm("chkct  res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(mSpawnChan));
    asm("in %0, res[%1]" : "=r"(senderId): "r"(mSpawnChan));
    asm("setd   res[%0], %1" :: "r"(mSpawnChan), "r"(senderId));
    asm("outct  res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(mSpawnChan));

    // Close the connection
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(mSpawnChan));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(mSpawnChan));

    // Initialise migrated process on a new thread
    asm("ldap r11, " LBL_RUN_THREAD "\n\t"
        "mov %0, r11" : "=r"(pc) :: "r11");
    
    // Give the next thread some space and launch it
    sp -= THREAD_STACK_SPACE; 
    newAsyncThread(pc, sp, senderId);
}

// Initialise the conneciton with the sender
void initGuestConnection(unsigned c, unsigned senderId) {
    
    asm("setd res[%0], %1"  :: "r"(c), "r"(senderId));
    asm("outct res[%0], " S(XS1_CT_START_TRANSACTION)  :: "r"(c));
    asm("out   res[%0], %1" :: "r"(c), "r"(c));
    asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION)  :: "r"(c));
}

// Receive a closure
{int, int} receiveClosure(unsigned c, unsigned args[], int len[]) {
  
    int numArgs, numProcs, index;
    unsigned inst, jumpTable;

    // Receive the header
    {numArgs, numProcs} = receiveHeader(c);

    // Use and update the fp safely by obtaining a lock
    asm("in r11, res[%0]" :: "r"(fpLock));
    
    // Receive arguments
    receiveArguments(c, numArgs, args, len);

    // Load jump table address
    asm("ldaw r11, cp[0]\n\t"
        "mov %0, r11" : "=r"(jumpTable) :: "r11");

    // Receive the children
    index = receiveProcedures(c, numProcs, jumpTable);

    // Release the lock
    asm("out res[%0], r11" :: "r"(fpLock));
    
    return {index, numArgs};
}

// Receive the closure header
{int, int} receiveHeader(unsigned c) {
    
    int numArgs, numProcs;

    // Acknowledge begin
    asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
    asm("outct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
    
    // Receive closure header
    asm("in %0, res[%1]" : "=r"(numArgs) : "r"(c));
    asm("in %0, res[%1]" : "=r"(numProcs) : "r"(c));

    // Synchronise with acknowledge end
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));

    return {numArgs, numProcs};
}

// Receive the arguments to the migrated procedure
#pragma unsafe arrays
void receiveArguments(unsigned c, int numArgs, 
        unsigned args[], int len[]) {

    unsigned length, value;

    // For each argument
    for(int i=0; i<numArgs; i++) {

        // Acknowledge begin
        asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
        asm("outct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
    
        // Receive the length
        asm("in %0, res[%1]"  : "=r"(len[i]) : "r"(c));

        // Receive a single value
        if(len[i] == 1) {
            asm("in %0, res[%1]"  : "=r"(args[i]) : "r"(c));
        }
        // Receive an array: write to stack and set args[i] to start address
        else {
            args[i] = fp;

            // Receive each element of the array and write straight to memory
            for(int j=0; j<len[i]; j++) {
                asm("in %0, res[%1]"  : "=r"(value) : "r"(c));
                asm("stw %0, %1[%2]" :: "r"(value), "r"(fp), "r"(j));
            }
           
            // Update fp, ensuring it is word aligned
            fp += len[i]*4; 
            if(fp % 4) fp += 2;
        }
            
        // Synchronise with acknowledge end
        asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
        asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
    }
}

// Receive the procedure and any children
#pragma unsafe arrays
int receiveProcedures(unsigned c, int numProcs, unsigned jumpTable) {
    
    int procIndex, procSize, index;
    unsigned inst;
    
    for(int i=0; i<numProcs; i++) {
        
        // Jump index and size
        asm("in %0, res[%1]"  : "=r"(procIndex) : "r"(c));
        asm("in %0, res[%1]"  : "=r"(procSize) : "r"(c));

        // TODO: Respond if this procedure has already been sent

        // Instructions
        for(int j=0; j<procSize/4; j++) {
            asm("in %0, res[%1]"  : "=r"(inst): "r"(c));
            asm("stw %0, %1[%2]" :: "r"(inst), "r"(fp), "r"(j));
        }
     
        // Acknowledge end
        asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
        asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
    
        // Patch jump table entry
        asm("stw %0, %1[%2]" :: "r"(fp), "r"(jumpTable), "r"(procIndex));

        // Update the procSize entry
        sizeTable[procIndex] = procSize;

        if(i == 0) index = procIndex;
        
        // Update fp, ensuring it is word aligned
        fp += procSize;
        if(fp % 4) fp += 2;
    }

    return index;
}

// Branch to and execute the migrated procedure
/*#pragma unsafe arrays
void runProcedure(unsigned c, int threadId, int procIndex,
        unsigned args[]) {
   
    unsigned procAddr, s=16;

    // Preserve r0-r3 on extended stack area
    asm("extsp 4");
    asm("stw r0, sp[1]");
    asm("stw r1, sp[2]");
    asm("stw r2, sp[3]");
    asm("stw r3, sp[4]");

    // Load arguments and run procedure
    asm("ldaw r11, cp[0]\n\t"
        "ldw %0, r11[%1]"
        : "=r"(procAddr) : "r"(procIndex));
    asm("mov r0, %0\n\tmov r1, %1\n\tmov r2, %2\n\tmov r3, %3\n\t"
        "bla %4" 
        :: "r"(args[0]), "r"(args[1]), "r"(args[2]), "r"(args[3]), "r"(procAddr) 
        : "r0", "r1", "r2", "r3");
   
    // Load r0-r3 and contract stack
    asm("ldw r0, sp[1]");
    asm("ldw r1, sp[2]");
    asm("ldw r2, sp[3]");
    asm("ldw r3, sp[4]");
    asm("ldaw r11, sp[0]\n\t"
        "add r11, r11, %0\n\t" 
        "set sp, r11\n\t"
        :: "r"(s) : "r11");
}*/

// Complete the migration of the procedure by informing the sender and
// transmitting back any results
void informCompleted(unsigned c, unsigned senderId) {
    
    // Set the channel destination (as it may have been set again by a nested on)
    asm("setd res[%0], %1"  :: "r"(c), "r"(senderId));

    // Signal the completion of execution
    asm("outct res[%0], " S(CT_COMPLETED) :: "r"(c));
    asm("chkct res[%0], " S(CT_COMPLETED) :: "r"(c));
    
    // End
    asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
    asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
}

// Send back any arrays that may have been updated by the execution of
// the migrated procedure
#pragma unsafe arrays
void sendResults(unsigned c, int numArgs, unsigned args[], int len[]) {

    unsigned value, length, addr;
    
    for(int i=0; i<numArgs; i++) {
        length = len[i];
        if(length > 1) {

            // Begin
            asm("outct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
            asm("chkct res[%0], " S(XS1_CT_START_TRANSACTION) :: "r"(c));
    
            for(int j=0; j<length; j++) {
                // Note can write this in one asm using r11 (but causes xcc fail)
                asm("ldw %0, %1[%2]" : "=r"(value) : "r"(args[i]), "r"(j));
                asm("out res[%0], %1" :: "r"(c), "r"(value));
            }
        
            // End
            asm("outct res[%0], " S(XS1_CT_END) :: "r"(c));
            asm("chkct res[%0], " S(XS1_CT_END) :: "r"(c));
        }
    }
}

// Spawn a new asynchronous thread
void newAsyncThread(unsigned pc, unsigned sp, unsigned senderId) {
    
    unsigned t, c = 0;
    int id;
   
    // Get a new asynchronous thread
    asm("getr %0, " S(XS1_RES_TYPE_THREAD) : "=r"(t));
    if(t == 0) error();

    // Get the thread's id (resource counter)
    id = (t >> 8) && 0xF;

    // Initialise cp, dp, sp, pc, lr := &yeild
    asm("ldaw r11, cp[0]"    ::: "r11");
    asm("init t[%0]:cp, r11" :: "r"(t));
    asm("ldaw r11, dp[0]"    ::: "r11");
    asm("init t[%0]:dp, r11" :: "r"(t) : "r11");
    asm("init t[%0]:sp, %1"  :: "r"(t), "r"(sp));
    asm("init t[%0]:pc, %1"  :: "r"(t), "r"(pc));
    asm("ldap r11, " LBL_YEILD ::: "r11");
    asm("init t[%0]:lr, r11" :: "r"(t) : "r11");
                             
    // Set senderId arg 
    asm("set t[%0]:r0, %1"  :: "r"(t), "r"(senderId));

    // Touch remaining GPRs
    asm("set t[%0]:r1, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r2, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r3, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r4, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r5, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r6, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r7, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r8, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r9, %1"  :: "r"(t), "r"(c));
    asm("set t[%0]:r10, %1" :: "r"(t), "r"(c));

    // Start the thread
    asm("start t[%0]" :: "r"(t));
}

