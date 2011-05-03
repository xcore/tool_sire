// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <platform.h>
#include "device.h"

extern void _slave(); 

// Mapping function to trigger construction of a NUM_CORES binary. Image on
// core 1 will be replaced by the master image.
int main(void) 
{ par(int i=0; i<NUM_CORES; i++)
  { on stdcore[i] : _slave();
  }
}
