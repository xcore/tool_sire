// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "system/xs1/definitions.h"
#include "system/definitions.h"
#include "globals.h"
#include "system.h"
#include "util.h"
#include "host.h"
#include "memory.h"

extern void runProcess        (int, unsigned int[], int);

void       initGuestConnection(unsigned, unsigned);
{int, int} receiveClosure     (unsigned, t_argument[], unsigned[], int[]);
{int, int} receiveHeader      (unsigned);
void       receiveArguments   (unsigned, int, t_argument[], unsigned[], int[]);
int        receiveProcedures  (unsigned, int);
void       informCompleted    (unsigned, unsigned);
void       sendResults        (unsigned, int, t_argument[], unsigned[], int[]);

// Setup and initialise execution of a new thread
void runThread(unsigned senderId) {
  
  int procIndex;
  int numArgs;
  t_argument argTypes[MAX_PROC_PARAMETERS];
  unsigned argValues[MAX_PROC_PARAMETERS];
  int argLengths[MAX_PROC_PARAMETERS];
  unsigned threadId = GET_THREAD_ID();
  
  // Initialis1e this (new) thread
  if(threadId != 0) _initthread();

  // Initialise connection with sender
  initGuestConnection(spawnChan[threadId], senderId);
  
  // Receive closure data
  {procIndex, numArgs} = receiveClosure(spawnChan[threadId], 
      argTypes, argValues, argLengths);

  // Run the process
  runProcess(procIndex, argValues, numArgs);

  // Complete the creation by sending back any results
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
  unsigned pc;
  
  // Connect to the sender and receive their id 
  senderId = IN(mSpawnChan);
  SETD(mSpawnChan, senderId);

  // Close the connection
  CHKCT_END(mSpawnChan);
  OUTCT_END(mSpawnChan);

  // Give the next thread some space and launch it
  asm("ldap r11, runThread ; mov %0, r11" : "=r"(pc) :: "r11");
  newAsyncThread(pc, senderId, 0, 0, 0);
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

// Receive the arguments to the new procedure
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
      argValues[i] = memAlloc(argLengths[i]*BYTES_PER_WORD);
      
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
      argLengths[i] = 1;
      argValues[i] = INS(c);
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

