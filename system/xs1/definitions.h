// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef XS1_DEFINITIONS_H
#define XS1_DEFINITIONS_H

// Labels
#define LABEL_EXCEP_HANDLER      "excepHandler"
#define LABEL_IDLE_HOST_HANDLER  "idleHostHandler"
#define LABEL_BUSY_HOST_HANDLER  "busyHostHandler"
#define LABEL_RUN_THREAD         "runThread"
#define LABEL_WAIT_HANDLER       "waitHandler"
#define LABEL_SLAVE_YEILD        "slaveYeild"
#define LABEL_CHAN_ARRAY         "progChan"
#define LABEL_MAIN               "_main"
#define LABEL_BEGIN_BSS          "_fdp.bss"
#define LABEL_END_BSS            "_edp.bss"
#define LABEL_START              "_start"
#define LABEL_JUMP_TABLE         "_jumptab"
#define LABEL_SIZE_TABLE         "_sizetab"
#define LABEL_FRAME_TABLE        "_frametab"

// Labels for jump table builtins
#define LABEL_CREATE_PROCESS     "_createprocess"
#define LABEL_INIT_THREAD        "_initthread"
#define LABEL_PROC_ID            "_procid"
#define LABEL_CONNECT_MASTER     "_connectmaster"
#define LABEL_CONNECT_SLAVE      "_connectslave"

// Jump table indicies
#define JUMPI_CREATE_REMOTE      0
#define JUMPI_INIT_THREAD        1
#define JUMPI_PROC_ID            2
#define JUMPI_CONNECT_MASTER     3
#define JUMPI_CONNECT_SLAVE      4

// Index offset of program jump indicies
#define JUMP_INDEX_OFFSET        5 

// Hardware specs
#define RAM_BASE                 0x10000
#define RAM_SIZE                 0x10000
#define BYTES_PER_WORD           4
#define MAX_THREADS              8
#define MAX_CHANNELS             32
                                
// Runtime specs                
#define MAX_PROCS                20
#define JUMP_TABLE_SIZE          25
#define SIZE_TABLE_SIZE          25 
#define KERNEL_SPACE             0x200
#define THREAD_STACK_SPACE       0x400
#define PROG_CHAN_OFF            (MAX_THREADS+1)
#define CONN_BUFFER_SIZE         10
                                
// Closure elements             
#define CLOSURE_NUM_ARGS         0
#define CLOSURE_NUM_PROCS        1
#define CLOSURE_ARGS             2
                                
// Ports                        
#define LED_PORT                 67072
                                
// Status register bit masks    
#define SR_EEBLE                 0x1
#define SR_IEBLE                 0x2
#define SR_WAITING               0x40

// Control tokens
#define CT_COMPLETED             0x5

#define SWITCH_SCRATCH_REG       3

#define NUM_PARAM_REGS           4

#endif
