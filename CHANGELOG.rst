==========
Change log
==========

---------
Version 0
---------

Language
========

- For statements now also specify a step (increment).

General compiler-related
========================

- Add NUM_CORES keyword in language.

- Constant pool extracted from xcc assembly output and replicated amongst slave
  images.

- When spawning synchronous threads, the whole stack is copied from and by the
  master.

- Array procedure parameter syntax to enforce array bounds for on statements,
  e.g.:: 
    proc foo(a[n], val n)

Process creation
================

- The host checks for a copy of a procedure contained in an incoming closure
  before receiving.

- Master thread (0) on each core is prioritised. It will be used last for
  hosting instead of first leaving it more available to serve requests and other
  jobs to get on.

- Referenced variables now work with 'on'.

- Allowing upto a maximum of 8 arguments, host 'runProcedure' load args 5
  onwards on to the stack before executing a new procedure.

- Dynamic heap allocation (XS1 malloc implementation) used allocate space for
  incoming procedures and referenced arguments.

