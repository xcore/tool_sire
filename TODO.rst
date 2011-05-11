====
Todo
====

---
New
---

- Par loop: par <index>:=<init> for <count> do
- Parallel composition of process calls only.
- No globals

------
Driver
------

- Make sure errors are dealt with properly at each stage of the main function

- Add a CompileStage class to record time and stats etc

--------------
Lexing/parsing
--------------

- Make sure error synchronisation points work well and only cause one error to
  be reported.

-----------------
Semantic analysis
-----------------

- Write tests for each rule of semantic analysis, check that it behaves well on
  all cases that cause errors and warnings.

- Ideally, symbol lookup should be O(1) by creating new tables for
  each new scope

- Semantic analysis should check formal array qualifiers are valid.

- Implement thread disjointness checking. 

- Function restrictions are not enforced. This includes referenced variable
  arguments or process calls.

- Function uses must occur after their definition.

- Check var arguments only accept a valid identifier (not an expression).

- No system call funcitons can be used by processes moved to another core as the
  slave binaries do not have this linked in.

- Semantic analysis needs to check types properly by walking the AST.

---------------
Code generation
---------------

- Make sure all runtime variables can't clash with sire variables - rename all
  with underscores.

- Read devices directory to determine valid number of cores.

----------------
Process creation
----------------

- Reclaim procedure and argument data stored in _fp after an 'on' has
  completed.

- Fail nicely with invalid core ids, e.g. core[0] or core[-1]

- Raise proper exception when no avilable threads.

- Free heap-allocated memory for arguments (and procedures?) when remote
  execution completes.

-------------
Miscellaneous
-------------

- Setting _DoSyscall symbol to 0 (on slave cores) breaks the event handler with
  the 11.2.0 tools and not 10.4.2 - find out why this is.

--------------------------------
Possible improvements/extensions
--------------------------------

- Complete code generation: add a complete back-end to produce assembly output
  natively or target LLVM.

