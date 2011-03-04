Todo
====

General compiler-related
------------------------

- Add more error cases to improve syntax error reporting.

- Add more error synchronisation points in the parser to reduce erronous parsing
  after a syntax error.

- Write tests for each rule of semantic analysis, check that it behaves well on
  all cases that cause errors and warnings.

- Make sure errors are dealt with properly at each stage of the main function

- Ideally, symbol lookup should be O(1) by creating new tables for
  each new scope

- Write language feature test cases in a unittest framework.

- Make sure all runtime variables can't clash with sire variables - rename all
  with underscores.

- Add a CompileStage class to record time and stats etc

- Semantic analysis should check formal array qualifiers are valid.

- No system call funcitons can be used by processes moved to another core as the
  slave binaries do not have this linked in.

- Check var arguments only accept a valid identifier (not an expression).

- Read devices directory to determine valid number of cores.

on implementation
-----------------

- ON: Reclaim procedure and argument data stored in _fp after an 'on' has
  completed.

- ON: Fail nicely with invalid core ids, e.g. core[0] or core[-1]


Done
====

General compiler-related
------------------------

- Add NUM_CORES keyword

- Constant pool (ideally) needs to be replicated amongst slaves.

- Adjust syntax to enforce array bounds for on statements, e.g. 
    proc foo(a[n], val n)

on implementation
-----------------

- ON: Check for a copy of a procedure before receiving.

- ON: Use master thread for hosting last instead of first

- ON: raise proper exception when no avilable threads

- ON: Implement referenced variables (or restrict their use with on).

- ON: load args 5 onwards on to the stack.


Skipped
=======

- Find out why asm expressions produce syntax errors, e.g. 
    .set .foo (_cp/4)+3

