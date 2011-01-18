#ifndef DEFINITIONS_H
#define DEFINITIONS_H

// Labels
#define LABEL_EXCEP_HANDLER      "excepHandler"
#define LABEL_IDLE_HOST_HANDLER  "idleHostHandler"
#define LABEL_BUSY_HOST_HANDLER  "busyHostHandler"
#define LABEL_RUN_THREAD         "runThread"
#define LABEL_WAIT_HANDLER       "waitHandler"
#define LABEL_MAIN               "_main"
#define LABEL_YEILD              "yeild"
#define LABEL_END_BSS            "_edp.bss"
#define LABEL_START              "_start"
#define LABEL_MIGRATE            "migrate"
#define LABEL_INIT_THREAD        "initThread"
#define LABEL_CONNECT            "connect"
#define LABEL_CHAN_ARRAY         "progChan"
#define LABEL_JUMP_TABLE         "jumpTable"
#define LABEL_SIZE_TABLE         "sizeTable"

// System variables
#define SYS_CHAN_ARRAY           "chan"
#define SYS_CORE_ARRAY           "core"

// Jump table
#define JUMPI_MIGRATE            0
#define JUMPI_INIT_THREAD        1
#define JUMPI_CONNECT            2

// Hardware specs
#define RAM_BASE                 0x10000
#define RAM_SIZE                 0x10000
#define BYTES_PER_WORD           4
#define MAX_THREADS              8
#define MAX_CHANNELS             32
#define CORES_PER_NODE           4
                                
// Runtime specs                
#define NUM_ARGS                 4
#define MAX_PROCS                10
#define JUMP_TABLE_SIZE          20
#define SIZE_TABLE_SIZE          20
#define KERNEL_SPACE             0x200
#define THREAD_STACK_SPACE       0x400
#define JUMP_INDEX_OFFSET        3
#define PROG_CHAN_OFF            (MAX_THREADS+1)
#define NUM_PROG_CHANS           (MAX_CHANNELS-PROG_CHAN_OFF)
                                
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

// For cmp/codegen.c
#define RES_TYPE_SYNC            0x3

// String wrapper
#define S_(x) #x
#define S(x) S_(x)

#endif
