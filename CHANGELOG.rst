Change log
==========

General compiler-related
------------------------

- Add NUM_CORES keyword in language.

- Constant pool extracted from xcc assembly output and replicated amongst slave
  images.

- When spawning synchronous threads, the whole stack is copied from and by the
  master.

- Adjust syntax to enforce array bounds for on statements, e.g.:: 
    proc foo(a[n], val n)

on implementation
-----------------

- Check for a copy of a procedure before receiving.

- Use master thread for hosting last instead of first leaving it more available
  to serve requests and other jobs to get on.

- Implement referenced variables (or restrict their use with on).

- load args 5 onwards on to the stack, allowing maximum of 8 arguments.

- Use malloc to allocate memory on the heap for procedures and incoming
  arguments.


