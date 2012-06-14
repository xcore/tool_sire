// Copyright (c) 2011, James Hanlon, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#ifndef MEMORY_H
#define MEMORY_H

#ifdef  __XC__ 
 #define REF & 
#else 
 #define REF * 
#endif 
 
unsigned _pointerUnsigned(unsigned REF a);
unsigned _pointerInt(int REF a);

#endif
