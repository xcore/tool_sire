#include <platform.h>
#include "../include/definitions.h"
#include "../include/platform.h"
#include "globals.h"
#include "system.h"

#define RUNS 1

extern void _master();
void runMain(unsigned main); 

// Master initialisation (thread0, core0, node0)
/* NOTE: This is the 'normal' master procedure
void initMaster() {

    // Branch to main procedure
    asm("ldap r11, " MAIN_PROC "\n\t"
        "bla r11" ::: "r11");

    idle();
}*/

void initMaster() {

    timer tmr;
    unsigned main, begin, end, elapsed, result;
    
    asm("ldap r11, " LBL_MAIN "\n\t"
        "mov %0, r11" : "=r"(main) :: "r11");
   
    tmr :> begin;
    runMain(main);
    tmr :> end;
       
    // Calculate the elapsed time in 10ms units
    elapsed = (end-begin); /// 100;

    // Move the elapsed time to r11 and pause
    asm("mov r11, %0" :: "r"(elapsed));
    asm("waiteu");

    idle();
}

// Mapping function
int main(void) {
    par(int i=0; i<NUM_CORES; i++) {
        on stdcore[i] : _master();
    }
}
