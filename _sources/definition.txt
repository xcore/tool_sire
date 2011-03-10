========================
sire language definition
========================

------------
Introduction
------------

    -- **sire** *verb*. To create or bear.

The sire language is a simple imperative, block structured language with syntax
similar to Pascal and features inspired from CSP [Hoare78]_ and Occam
[Occam82]_. It is indented to provide a platform on which to implement and
test the mechanism for *dynamic process creation*. It includes simple
sequential constructs and features for message passing concurrency, but omits
features such as user defined data types for simplicity. This document gives an
informal description of the syntax and semantics.

---------------------------
Variables, values and types
---------------------------

Variables hold a value state which is changed by statements operating on this
state. Variable instances are declared with the ``var`` keyword::
    
    val a, b;

declares variables ``a`` and ``b`` of type ``val``, a signed integer value.
Variable declarations of different types are separated by a semicolon, for
example::
    
    var a; 
    var b[10];

declares ``a`` of type integer and ``b`` of type integer array. The assignment
statement is used to change the value of a variable::
    
    a := 7 

changes the value of ``a`` to 7. Any expression can appear on the right hand
side of the assignment statement.  Signed integers are the only basic variable
type in sire.

Numbers
=======

Integer valued numbers can be represented in binary, decimal and hex decimal
forms by prefixing with ``0b``, nothing and ``0x`` respectively.  The
reserved symbols ``true`` and ``false`` represent the values 1 and 0
respectively.

Operators
=========

All arithmetic in sire is performed on signed integers. The table below gives
the arithmetic operators available with their type, associativity and
precedence. Precedence 0 relates to the highest precedence. 

.. The operators bitwise and, or, xor, and plus and multiply are fully
 associative and do not need bracketing. All other operators may only occur only
 once in a single, or bracketed sub expression.

======== ====== ============= ========== =====================
Symbol   Type   Associativity Precedence Meaning
======== ====== ============= ========== =====================
``-``    unary  right         1          Negation
``~``    unary  right         1          Bitwise not
``*``    binary left          2          Multiplication
``/``    binary left          2          Division
``+``    binary left          3          Addition
``-``    binary left          3          Subtraction
``rem``  binary left          4          Modulo
``or``   binary left          4          Bitwise or
``and``  binary left          4          Bitwise and
``xor``  binary left          4          Bitwise xor
``<<``   binary left          4          Bitwise left shift
``>>``   binary left          4          Bitwise right shift
``lor``  binary left          5          Logical or
``land`` binary left          5          Logical and
``=``    binary left          6          Equal
``~=``   binary left          6          Not equal
``<``    binary left          6          Less than
``<=``   binary left          6          Less than or equal
``>``    binary left          6          Greater than
``>=``   binary left          6          Greater than or equal
======== ====== ============= ========== =====================

Arrays
======

An array is created by suffixing a type with square brackets enclosing an
integer expression specifying the length::

    var a[10];

declares a length 10 array of signed integers. The elements are accessed with
the array subscript notation, for example, ``a[0]`` accesses the lowest element
of ``a``, legal accesses may be made up to ``a[9]``. Currently, only one
dimensional arrays are supported. Array references are also used for array
slicing and formal parameters. For example::

    var b[];
    
declares ``b`` as an uninitialised array reference.

Array slicing is provided by the *alias* statement. This is a special type of
assignment that assigns the value of a variable of type array reference to a
valid position of the source array. For example, the statement::
    
    b aliases a[6..]

causes ``b`` to reference the last half of ``a``. Aliasing simply duplicates an
offset array reference, no copying is involved.

Constant values
===============

Constant values represent static integer values. The declaration::

    val c := 4; 
    
sets the value of ``c`` to 4, ``c`` cannot then be changed by any assignment
statement during execution.

Ports
=====

Ports are a special constant-valued variable that may be used as a source or
destination in an input or output operation. The declaration::

    port p : 0x10600 
    
sets the value of ``p`` to ``0x10600``.

Scope
=====

There are only two levels of scoping for variables in sire: global, at the
program level, and local, at the process/function level. Variable declarations
may be made either globally or locally, but constant and port declarations may
*only* be made globally.

-----------
Structuring
-----------

Sequential and parallel composition
===================================

*Processes* and *functions* are composed of a set of block-structured
statements. Statements can either be composed *sequentially* or in *parallel*. This
is denoted by the use of the sequential separator '``;``', or the parallel
separator '``|``'. The block::

    { process1() ; process2() ; process3() } 
    
is composed sequentially, so processes 1, 2 and 3 will be executed one after
another. Execution of the block will complete when ``process3`` has completed.
In contrast, the block::

    { process1() | process2() | process3() }

is composed in parallel, so on entry to the block, two new threads are created
for processes 2 and 3 and then execution of all three processes commences in
parallel. Execution of the block will terminate only when the last process has
completed.

The ``while`` loop
==================

The ``while`` loop repetitively executes a body while a condition remains
true. This is checked each time prior to the execution of the body. When it
becomes false, the loop terminates. The following code demonstrates the use of a
while loop, which implements an algorithm to calculate the factorial of a number
``n``, n!::

    var i;
    var factorial;
    { i := 0 
    ; factorial = 1
    ; while i < n do
      { factorial := factorial * i 
      ; i := i + 1 
      }
    }

The ``for`` loop
================

The ``for`` loop repetitively executes a loop body based on a pre and post
condition on a incrementing counter. This allows a simple iteration to be more
simply expressed. The following code again implements the factorial algorithm,
but with a for loop::

    var i;
    var factorial;
    { factorial =: 1
    ; for i:=1 to n do
        factorial := factorial * i
    }

The ``if`` statement
====================

The ``if`` statement allows the conditional execution of statements. The
condition is evaluated as an arithmetic expression and if non-zero then the
``then`` part is executed, otherwise the ``else`` part is. The ``else`` part is
required to solve the dangling else problem. The following code implements a
recursive factorial algorithm, demonstrating the use of an if statement::

    func factorial(val n) is
      if n = 0 then return 1 else return n * factorial(n-1)

The ``skip`` statement
======================

The ``skip`` statement does nothing, but is used to fill an empty if statement's
``else``.

Processes and functions
=======================

.. % formal parameters, array references
.. % return statement
.. % Recursion?

*Processes* and *functions*, both types of *procedure*, are a
collection of one or more statements that perform some task. Functions are a
special procedure type that do not cause any *side effects* and only
return a value. A function causes a side effect if it also modifies some
external state. This might include, for instance, changing the
value of a global variable, or modifying the contents of a referenced array. To
prevent this from happening, functions cannot write to global variables or
referenced parameters, invoke processes or use input or output operators. In
contrast, processes do not return a value but have no such restrictions on side
effects. 

A process is defined using the ``proc`` keyword, followed by the process name,
formal parameters, local variable declarations and then the body.  For example,
the following process definition implements the bubble sort algorithm::

    proc sort(a[len]; len: int) is
     var i;
     var j;
     var tmp;
     for i:=0 to len-1 do 
       for j:=0 to len-1 do
         if a[j] > a[j+1]
           then { tmp := a[j] ; a[j] := a[j+1] ; a[j+1] := tmp }
           else skip

A process is invoked by naming the process and specifying any input parameters::

    sort(a, 10)

A function is defined in the same way as a process except with the ``func``
keyword, it must also complete with a ``return`` statement. The following
function recursively calculates the ``n`` th Fibonacci number::

    func fib(n: int) is
      if n > 1 then return fib(n-1) + fib(n-2)
      else if n = 0 then return 0 else return 1

Functions can be called in the same way as processes or as part of an
expression, as it is in the above example.  The formal parameters of a function
or process may only be of integer or integer array reference types. 

Scoping
-------

A process or function becomes visible only at the beginning of its definition.
Hence, a procedure cannot be used before it is defined.

Recursion
---------

Recursion is permitted, but only for self-recursive procedures. Due to simple
scoping for procedure names which would require the need for forward references,
mutual-recursion is not supported.

Program structure
=================

.. What about visibility of function definitions?

A sire program consists of a set of *processes* and *functions* and
possibly some global state. The structure of a sire program is as follows.
Any value, variable or port global declarations are made at the beginning,
before any process or function definitions. Processes and functions may then be
defined in any order. A program must contain a process called ``main`` as
execution will start at this point. For example, a complete example sorting
program may be defined as::

    val LEN := 10;
    var a[LEN];

    proc sort(a[len], val len) is
      var i;
      var j;
      var tmp;
      for i:=0 to len-1 do 
        for j:=0 to len-1 do
          if a[j] > a[j+1]
          then { tmp := a[j] ; a[j] := a[j+1] ; a[j+1] := tmp }
          else skip

    proc main() is
      sort(a, LEN)

..
    -------------
    Communication
    -------------

    Concurrently executing processes are able to communicate by means of
    \emph{channels}. A channel is a bidirectional communication medium, established
    through \emph{connected} channel ends. Channel ends are available in a global
    address space, and accessed by a special system channel end array called
    \ttt{chan}. Before a channel can be used it must first be connected to another
    channel end, this is achieved with the connect statement. For example, execution
    of the statement: \excode{connect} chan[0] to} core[10] : chan[0]} on
    core 0 connects the local channel end \ttt{chan[0]} to the channel end
    \ttt{chan[0]} on core 10. This is sufficient to make a unidirectional
    connection, allowing messages to be received from core 0 by core 10, but when it
    is \emph{fully} connected and messages can be exchanged in both directions. To
    allow this, a connection must also be made at the other end:
    \excode{connect} chan[0] to} core[0] : chan[0]}

    Once a channel is connected, values can be sent and received using the
    \emph{input} and \emph{output} operators: '\ttt{?}' and '\ttt{!}'. The following
    code implements a buffer, illustrating the use of these operations:

     proc} buffer() is}
        var} x: int};
        while} true do} \{ chan[IN] ? x ; chan[OUT] ! x \}

    The buffer simply copies values from the \ttt{IN} channel to the
    \ttt{OUT} channel. The output operator can also be used with ports.
..

----------------
Process creation
----------------

Process creation is the key feature of the sire language and is provided with
the ``on`` statement. Semantically, ``on`` is exactly the same as a regular
process call, except that the computation is performed remotely. It is
*synchronous* in that it blocks the sending processes thread of execution
until the new process has terminated; this behavior fits naturally with
composing it in parallel with other tasks.

The transmission of a process to a remote processor for execution requires a
*closure* of the process to be created. A closure is a data structure that
contains the process' instructions, and a representation of the functions
*lexical environment*, that is the set of available variables and their
values. \sire processes may have formal parameters of type integer value or
array reference, so these must be included as part of the closure. Referenced
arrays are copied and replicated at the destination. On completion, any
referenced arrays are sent back to reflect any changes that were made in the
original copy. The statement::

    var a[10];
    on core[3] : sort(a, 10)

spawns the ``sort`` process on core 3. The ``core`` array is a system variable
and is used to address the set of processing cores comprising the system.
Because the ``on`` statement is synchronous, it is natural to to compose this in
parallel with other statements.  For example, the block::

    var a[10];
    var b[10];
    { on core[10] do sort(a, 10) | sort(b, 10) }

allows the thread to execute another sorting process whilst the spawned one is
performed remotely.

----------
References
----------

.. [Hoare78] C. A. R. Hoare. Communicating sequential processes. *Commun. ACM*,
     21(8):666-677, 1978.

.. [Occam82] David May. Occam. *SIGPLAN Not.*, 18(4):69-79, 1983.

