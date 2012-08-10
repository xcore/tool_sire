/* 
 * Global data (local to the runtime on a core). These must be delcared in
 * this way so that we can guarantee they will be linked at the same addresses
 * in the master and slave binaries (at the beginnning of the dp region).
 */

#include "system/xs1/definitions.h"

  .globl _spValue,     "ui"
  .globl _seed,        "ui"

  .globl spawn_master, "ui"
  .globl thread_chans, "a(:ui)"

  .globl conn_master,  "ui"
  .globl conn_buffer,  "a(:s(){m(connId){si},m(origin){si},m(chanCRI){ui}})"
  .globl conn_locals,  "a(:s(){m(connId){si},m(origin){si},m(chanCRI){ui}})"
  .globl conn_server,  "a(:s(){m(connId){si},m(chanCRI){ui}})"

  .globl chan_mem_access, "ui"
 
.section .dp.data, "awd", @progbits
  .align BYTES_PER_WORD

/*
 * Global data
 */

_spValue:
  .space BYTES_PER_WORD
  .set _spValue.globound, BYTES_PER_WORD

_seed:
  .word 0xFFFFFFFF
  .set _seed.globound, BYTES_PER_WORD

/*
 * Processor allocaion
 */

spawn_master:
  .space BYTES_PER_WORD
  .globl spawn_master.globound
  .set spawn_master.globound, BYTES_PER_WORD

thread_chans:
  .space MAX_THREADS*BYTES_PER_WORD
  .globl thread_chans.globound
  .set thread_chans.globound, MAX_THREADS*BYTES_PER_WORD

/*
 * Connection setup and management 
 */

conn_master:
  .space BYTES_PER_WORD
  .globl conn_master.globound
  .set conn_master.globound, BYTES_PER_WORD

conn_buffer:
  .space 3*CONN_BUFFER_SIZE*BYTES_PER_WORD
  .globl conn_buffer.globound
  .set conn_buffer.globound, 3*CONN_BUFFER_SIZE*BYTES_PER_WORD

conn_locals:
  .space 3*MAX_THREADS*BYTES_PER_WORD
  .globl conn_locals.globound
  .set conn_locals.globound, 3*MAX_THREADS*BYTES_PER_WORD

conn_server:
  .space 2*MAX_THREADS*BYTES_PER_WORD
  .globl conn_server.globound
  .set conn_server.globound, 2*MAX_THREADS*BYTES_PER_WORD

/*
 * Remote memory access
 */

chan_mem_access:
  .space BYTES_PER_WORD
  .globl chan_mem_access.globound
  .set chan_mem_access.globound, BYTES_PER_WORD

