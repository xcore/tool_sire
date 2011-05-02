#ifndef PRINT_H
#define PRINT_H

#include <stdlib.h>

static inline void printchar(char c) {
    printf("%c", c);
}

static inline void printcharln(char c) {
    printf("%c\n", c);
}

static inline void printval(int v) {
    printf("%d\n", v);
}

static inline void printvalln(int v) {
    printf("%d\n", v);
}

static inline void printhex(int v) {
    printf("%x", v);
}

static inline void printhexln(int v) {
    printf("%x\n", v);
}

static inline void printstr(char s[]) {
    printf("%s\n", v);
}

static inline void printstrln(char s[]) {
    printf("%s\n", v);
}

static inline void println() {
    printf("\n");
}

#endif
