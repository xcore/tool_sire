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
#include "source.h"

void initHostConnection(unsigned, unsigned);
void sendClosure       (unsigned, unsigned[]);
void sendHeader        (unsigned, int, int);
int  sendArguments     (unsigned, int, unsigned[]);
void sendProcedures    (unsigned, int, int, unsigned[]);
void waitForCompletion (unsigned);
void receiveResults    (unsigned, int, unsigned[]);

/*
 * Create a new remote process.
 */
#pragma unsafe arrays
void _createProcess(unsigned dest, unsigned closure[]) 
{
  unsigned threadId;
  unsigned c;
  unsigned destResID; 
  THREAD_ID(threadId);
  c = thread_chans[threadId];
  CHAN_RI_0(dest, destResID);

  // Initialise the connection with the host
  initHostConnection(c, destResID);
  
  // Transfer closure data
  sendClosure(c, closure);
  
  // Wait for ececution to complete
  waitForCompletion(c);

  // Receive any results
  receiveResults(c, closure[CLOSURE_NUM_ARGS], closure);
}

/*
 * Initialise the connection with the host thread.
 */
void initHostConnection(unsigned c, unsigned destResID) {

  // Connected to: Master spawn channel=======================
  // Initiate conneciton by sending chanResId
  SETD(c, destResID);
  OUT(c, c);

  // Close the current channel connection 
  OUTCT_END(c);
  CHKCT_END(c);
  
  // Connected to: Slave spawn channel========================
  // Open new connection with spawned thread and get their CRI
  IN(c, destResID);
  SETD(c, destResID);
  
  // Sync and close the connection
  CHKCT_END(c);
  OUTCT_END(c);
}

/* 
 * Send a closure.
 * NOTE: xcc adds in array bounds checking which assumes array length is an
 * implicit argument.
 */
#pragma unsafe arrays
void sendClosure(unsigned c, unsigned closure[]) {
   
  unsigned numArgs  = closure[CLOSURE_NUM_ARGS];
  unsigned numProcs = closure[CLOSURE_NUM_PROCS];
  int procOffset;

  // Send the header
  sendHeader(c, numArgs, numProcs);

  // Send arguments
  procOffset = sendArguments(c, numArgs, closure);

  // Send the children
  sendProcedures(c, numProcs, procOffset, closure);
}

/*
 * Send the header.
 */
void sendHeader(unsigned c, int numArgs, int numProcs) {
  OUTS(c, numArgs);
  OUTS(c, numProcs);
}

/*
 * Send the source procedures arguments.
 */
#pragma unsafe arrays
int sendArguments(unsigned c, int numArgs, unsigned closure[]) {

  int index = CLOSURE_ARGS;

  for(int i=0; i<numArgs; i++) {
  
    // Send the arument type
    OUTS(c, closure[index]);
  
    switch(closure[index]) {
    default: break;
    
    case t_arg_ALIAS:
      OUTS(c, closure[index+1]);
      for(int j=0; j<(int) closure[index+1]; j++) {
        unsigned value;
        asm("ldw %0, %1[%2]" : "=r"(value) : "r"(closure[index+2]), "r"(j));
        OUTS(c, value);
      }
      index += 3;
      break;
    
    case t_arg_VAR:
      {unsigned value;
      asm("ldw %0, %1[%2]" : "=r"(value) : "r"(closure[index+1]), "r"(0));
      OUTS(c, value);}
      index += 2;
      break;
    
    case t_arg_CHANEND:
      OUTS(c, closure[index+1]);
      index += 2;
      break;
    
    case t_arg_VAL:
      OUTS(c, closure[index+1]);
      index += 2;
      break;
    }
  }

  return index;
}

/*
 * Send the source procedure and any children it has.
 */
#pragma unsafe arrays
void sendProcedures(unsigned c, int numProcs, int procOff, unsigned closure[]) {
  
  unsigned cp;

  // Load the address of the constant pointer
  asm("ldaw r11, cp[0] ; mov %0, r11" : "=r"(cp) :: "r11");

  for(int i=0; i<numProcs; i++) {

    unsigned flag;

    // Load the procAddress and procSize from the index
    unsigned procIndex = closure[procOff+i];
  
    // Send the jump index
    OUTS(c, procIndex);
    INS(c, flag);
    
    // If the host doesn't have the procedure, send it.
    if(flag) {
      unsigned procAddr; 
      int procSize  = (int) SIZE_TABLE[procIndex];
      OUTS(c, procSize);
    
      // Instructions
      asm("ldw %0, %1[%2]" : "=r"(procAddr) : "r"(cp), "r"(procIndex));
      
      for(int j=0; j<procSize/4; j++) {
        unsigned inst;
        asm("ldw %0, %1[%2]" : "=r"(inst) : "r"(procAddr), "r"(j));
        OUTS(c, inst);
      }
    }
  }
}

/*
 * Wait for the completion of the new procedure.
 */
void waitForCompletion(unsigned c) {
  
  // (wait to) Acknowledge completion
  asm("chkct res[%0], " S(CT_COMPLETED) :: "r"(c));  
  asm("outct res[%0], " S(CT_COMPLETED) :: "r"(c));  
      
  // Acknowledge end
  CHKCT_END(c);
  OUTCT_END(c);
}

/* 
 * Receive any array arguments that may have been updated by the new
 * procedure.
 */
#pragma unsafe arrays
void receiveResults(unsigned c, int numArgs, unsigned closure[]) {

  int index = CLOSURE_ARGS;

  for(int i=0; i<numArgs; i++) {
    
    switch(closure[index]) {
    default: break;
    
    case t_arg_ALIAS:
      for(int j=0; j<(int) closure[index+1]; j++) {
        unsigned value;
        INS(c, value);
        asm("stw %0, %1[%2]" :: "r"(value), "r"(closure[index+2]), "r"(j));
      }
      index += 3;
      break;
    
    case t_arg_VAR:
      {unsigned value;
      INS(c, value);
      asm("stw %0, %1[%2]" :: "r"(value), "r"(closure[index+1]), "r"(0));}
      index += 2;
      break;
    
    case t_arg_CHANEND:
      index += 2;
      break;

    case t_arg_VAL:
      index += 2;
      break;
    }
  }
}

