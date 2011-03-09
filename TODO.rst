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

To sort
-------

Current problems

- The process creation protocol requires an integer length parameter to
  immediately follow an array reference. This could be neatened by requiring the
  length parameter to be referenced as part of the array parameter. For example:
  \excode{proc p(a(len): int[]; len: int)} would declare an array reference
  \ttt{a} of length \ttt{len}.

- Ordering of global constant, port and variable declarations is fixed.

Possible improvements

- Allow variable types as formal parameters; i.e.\ referenced variables,
instead of just constant value arguments.

- Allow the expression of more complex programs by allowing state to be
associated with a function, rather than the current local/global scoping. This
could be in the form of object orientated, modular structuring or nested process
definitions.

- A proper type system to allow the use, for example, of byte or short
types, tuples and user-defined data types.

- Multi-dimensional arrays.

- Channel protocol types.

implementation Current problems


- Function restrictions are not enforced. This includes referenced
variable arguments or process calls.

- Thread disjointness checking. This is not a problem currently as single
variables cannot be referenced, but with the introduction of variable argument
types, this would become more necessary. More generally though, stricter
\emph{interference control} would reduce programming errors.

- Function uses must occur after their definition.


Possible improvements

- Parallel recursion is not properly dealt with. Either, a method of
stack allocation that allow multiple threads unrestricted access to the stack or
a semantic restriction in the language prohibiting more than one unrestricted
recursion is required.

- Integration of a thread virtualisation scheme. This would allow much more
flexible use of parallel composition, rather than being limited by the number of
hardware threads available. In conjunction with process creation, threads become
idle whilst blocking on the execution of a remote process, it is not necessary
for this thread pipeline slot to be unavailable during that time. 

- Alternative implementation of channels as proper variables to allow
process connectivity to be defined as part of their formal parameters.

Process creation

Current problems

- Processes can only have up to 4 formal parameters.

- Array arguments must be followed by a length parameter. In XC, additional
implicit array length parameters are added for each array argument for static
bounds checking. Something similar could be implemented.

- There is no check performed that a host core does not already own a copy of
a procedures. This would be a simple improvement to make.

- There is no sanity check performed on the destination identifier. If it
outside the range of valid core identifiers the system must halt gracefully.

- If the number of threads is insufficient for a program, the system must
halt gracefully.

- The memory used to store incoming procedures and arguments is never
reclaimed. 

- The size of the \emph{jump} and \emph{size} tables are fixed and hence so
are the number of procedures allowed in a program.

Possible improvements

- It would be possible to \emph{pipeline} the transmission and execution of
incoming closures.  A procedure could start being executed as soon as enough of
it had been received, i.e.\ up to the point of a conditional statement. In the
case of a recursively nested \ttt{on}, the next closure could immediately start
to be sent. This approach would require separators within the instruction
sequence that would allow safe execution up to them at which point it could be
paused, such as conditional statements.

