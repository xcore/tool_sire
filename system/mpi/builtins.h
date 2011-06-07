#ifndef BUILTINS_H
#define BUILTINS_H

// Printing
#define _PRINTCHAR(x)   printf("%c", x)
#define _PRINTCHARLN(x) printf("%c\n", x) 
#define _PRINTVAL(x)    printf("%d", x) 
#define _PRINTVALLN(x)  printf("%d\n", x) 
#define _PRINTHEX(x)    printf("%x", x) 
#define _PRINTHEXLN(x)  printf("%x\n", x) 
#define _PRINTSTR(x)    printf("%s", x) 
#define _PRINTSTRLN(x)  printf("%s\n", x) 
#define _PRINTLN()      printf("\n") 

// Fixed point
int mulf8_24(int, int);
int divf8_24(int, int);

// System
int procid();

#endif

