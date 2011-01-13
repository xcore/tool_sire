#ifndef UTIL_H
#define UTIL_H

unsigned chanResId(unsigned, int);
unsigned genCRI(unsigned);
void     raiseException();
void     error();
unsigned getThreadId();
unsigned getNode(unsigned);
unsigned getCore(unsigned);
unsigned destResId(unsigned);

#endif
