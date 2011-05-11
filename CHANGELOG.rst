==========
Change log
==========

-----------
Version 0.1
-----------

- Builtins: set of built-in procedures available in the language. Implemented in
  target language in system/<system>/builtin.* and included in translation and
  build process. Also addition of:
    - println()
    - Fixed point 2.24 divide and muliply routines.

- Unit test restructure: separation of target platforms and expected output into
  a .output file.

Minor changes:
- Allow constant values in array length specifiers
- 'val' array parameters
- 'val' and 'var' specifiers on all formal parameters
- New for loop syntax: for <index>:=<init> to <bound> (step <increment>)? do
- In place array aliases (slicing)

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

