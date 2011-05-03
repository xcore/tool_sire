#ifndef MPI_DEFINITIONS_H
#define MPI_DEFINITIONS_H

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
#define _MUL_8_24(x, y)          mul8_24(x, y)
#define _DIV_8_24(x, y)          div8_24(x, y)

#endif

