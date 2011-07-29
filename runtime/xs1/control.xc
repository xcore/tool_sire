// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include <platform.h>
#include "system/xs1/definitions.h"
#include "system.h"
#include "globals.h"
#include "util.h"
#include "control.h"

// Idle (thread 0 only) for the next event to occur
void controlIdle() {

  // Disable interrupts and events, switch to event mode
  asm("clrsr " S(SR_IEBLE) " | " S(SR_EEBLE));
  asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(spawn_master));
  asm("setc res[%0], " S(XS1_SETC_IE_MODE_EVENT) :: "r"(conn_master));
  
  // Set event vector to idle handler
  asm("ldap r11, " LABEL_HOST_HANDLER "\n\t"
    "setv res[%0], r11" :: "r"(spawn_master) : "r11");
  asm("ldap r11, " LABEL_CONN_HANDLER "\n\t"
    "setv res[%0], r11" :: "r"(conn_master) : "r11");

  // Wait for an event on spawn_master
  asm("waiteu");
}

// Yeild execution of the master thread (of a slave node), and enter idle state.
void controlYeild() {
  controlIdle();
}

