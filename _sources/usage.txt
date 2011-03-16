=====
Usage
=====

------------
Installation
------------

Setting up the dependencies
===========================

Python 3 (including the argparse module)
----------------------------------------

Download and install the latest release of Python 3
(http://www.python.org/download/). This should then be available on the PATH as
'python3'. To do this *append* /python3/install/path/bin to PATH, for example::

    export PATH=/python3/install/path/bin:$PATH

The ``argparse`` module is included as part of the standard library from
version 3.2+. For older versions, this will need to be installed manually.

PLY (Python Lex-Yacc)
---------------------

Download and install the latest version of PLY (http://www.dabeaz.com/ply/). You
can copy the ``lexer.py`` and ``parser.py`` files into
``tool_sire/compiler/ply`` or install PLY using ``distutils``::

    cd ply-3.4
    python3 setup.py install

XMOS development tools
----------------------

Download and install the latest version of the XMOS development tools
(https://www.xmos.com/products/development-tools). To make them accessible from
the command line you then need to run::

    source SetEnv

from ``XMOS/DevelopmentTools/11.2.0/`` or copy the contents into your
``.bashrc`` and change ``installpath`` to the installation path. 

Documentation
-------------

To build the documentation you will need the xcore/xdoc repository in the same
directory as the sire repository::
 
    git clone https://github.com/xcore/xdoc.git

You can then build the HTML and PDF targets by running ``make`` in the root
directory.

Setting up sire
===============

Once the dependencies are satisfied, the sire compiler can be setup by adding
SIRE_INSTALL_PATH to your environment and PATH by adding the following to your
.bashrc file, for example::

  export SIRE_INSTALL_PATH=/path/to/sire
  PATH=$SIRE_INSTALL_PATH:$PATH

---------------
Getting started
---------------

Compile and simulate 'hello world'::

  $ echo 'proc main() is printstrln("hello world")' | sire
  $ xsim a.xe
  hello world

Display help to view available command line options::

    $ sire -h
    usage: sire [-h] [-o <file>] [-n <n>] [-v] [-e] [-r] [-s] [-a] [-p] [-t] [-c]
                [-d]
                [<input-file>]

    sire compiler

    positional arguments:
      <input-file>          input filename

    optional arguments:
      -h, --help            show this help message and exit
      -o <file>             output filename
      -n <n>, --numcores <n>
                            number of cores
      -v, --verbose         display status messages
      -e, --display-calls   display external commands invoked
      -r, --parse           parse the input file and quit
      -s, --sem             perform semantic analysis and quit
      -a, --display-ast     display the AST and quit
      -p, --pprint-ast      pretty-print the AST and quit
      -t, --translate       translate but do not compile
      -c, --compile         compile but do not assemble and link
      -d, --devices         display available devices


Useful options
==============

Display the Abstract Syntax Tree (AST)::

    $ echo 'proc main() is printstrln("hello world")' | sire -a
    Program()
      Decls()
      Defs()
        Def(_main, Type(proc, procedure))
          Formals()
          Decls()
          StmtPcall(printstrln)
            ExprList()
              ExprSingle()
                ElemString("hello world")

Display a pretty-printed AST, and compile it::

    $ echo 'proc main() is printstrln("hello world")' | sire -p

    proc main() is
      printstrln("hello world")

    $ echo 'proc main() is printstrln("hello world")' | sire -p | sire
    
Perform XC-translation only::

    $ echo 'proc main() is printstrln("hello world")' | sire -t
    $ cat a.xc
    #include <xs1.h>
    #include <print.h>
    #include <syscall.h>
    #include "globals.h"
    #include "util.h"
    #include "guest.h"
    #include "device.h"
    #include "language.h"

    #pragma unsafe arrays
    void _main()
    {
      {
        printstrln("hello world");
      }
    }

Compile with verbose messages::

    $ echo 'proc main() is printstrln("hello world")' | sire -v
    Parsing file 'stdin'
    Performing semantic analysis
    Performing child analysis
    Translating AST
    [Building an executable for 1 cores]
    Creating device header device.h
    Compiling program.xc -> program.S
    Modifying assembly output
      Extracting constants
      Inserting function labels
      Inserting frame sizes
      Rewriting calls
    Assembling program.S -> program.o
    Assembling constpool.S -> constpool.o
    Building master jump table
    Assembling masterjumptab.S -> masterjumptab.o
    Building master size table
    Building master frame table
    Assembling mastertables.S -> mastertables.o
    Compiling runtime:
      guest.xc -> guest.xc.o
      host.S -> host.S.o
      host.xc -> host.xc.o
      master.S -> master.S.o
      master.xc -> master.xc.o
      slave.S -> slave.S.o
      slave.xc -> slave.xc.o
      slavetables.S -> slavetables.S.o
      system.S -> system.S.o
      system.xc -> system.xc.o
      util.xc -> util.xc.o
      memory.c -> memory.c.o
    Linking master -> master.xe
    Linking slave -> slave.xe
    Replacing master image in node 0, core 0
    Cleaning up
    Produced file: a.xe

