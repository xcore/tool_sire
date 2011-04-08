====
Todo
====

---
New
---

- Add println() builtin

- Allow constant values in array length specifiers

- 'val' array parameters

- For loop: for <index>:=<init> to <bound> (step <increment>)? do

- Par loop: par <index>:=<init> for <count> do

- 'val' and 'var' specifiers on all formal parameters

- In place array aliases (slicing)

- Allow slice of a single array element to 'val' or 'var'.

- Prohibit globals?

------
Driver
------

- Make sure errors are dealt with properly at each stage of the main function

- Add a CompileStage class to record time and stats etc

--------------
Lexing/parsing
--------------

- Add more error cases to improve syntax error reporting.

- Add more error synchronisation points in the parser to reduce erronous parsing
  after a syntax error.

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

