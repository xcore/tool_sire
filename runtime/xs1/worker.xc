// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include "worker.h"

// Yeild execution of a slave thread (only 1-7)
void workerYeild() {
  asm volatile("freet");
}

