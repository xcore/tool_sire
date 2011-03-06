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

- Reclaim procedure and argument data stored in _fp after an 'on' has
  completed.

- Fail nicely with invalid core ids, e.g. core[0] or core[-1]

- Raise proper exception when no avilable threads.

- Free heap-allocated memory for arguments (and procedures?) when remote
  execution completes.

