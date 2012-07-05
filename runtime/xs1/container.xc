// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <platform.h>

void foo(void) {}; 

int main(void) {
  par {
    on stdcore[0] : foo();
    on stdcore[1] : foo();
  }
  return 0;
}

