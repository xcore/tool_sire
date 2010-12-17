#ifndef UTIL_H
#define UTIL_H

unsigned getThreadId();
unsigned chanResId(unsigned, int);
unsigned genCRI(unsigned);
unsigned getNode(unsigned);
unsigned getCore(unsigned);
unsigned destResId(unsigned);
void     raiseException();
void     error();

#endif
