====
sire
====

:Stable release: Unreleased
:Status: Experimental/ongoing
:Maintainer: http://github.com/jameshanlon
:Description: A language and runtime system for dynamic process creation on the XMOS XS1 architecture

sire is a small block-structured, imperative language with features to
demonstate a mechanism for distributed and dynamic creation of processes in and
over a parallel system. It targets the XMOS XS1 architecture, which is
general-purpose and has low-level support for concurrency and parallelism.

For more information, check out the on-line documentation at
http://xcore.github.com/tool_sire

------------
Key features
------------

- Complete compiler
- Translation of sire program code to XC/assembly source.
- Construction of special multi-core binary replicating only the runtime kernel.

-----
To do
-----

- See TODO.rst.

------------
Known issues
------------

- Plenty, see TODO.rst.

---------------------
Required repositories
---------------------

- xdoc git@github.com:xcore/xdoc.git
  
------------
Dependencies
------------

- Python 3.2 or 3.1 with the argparse module avilable as 'python3' on the command line.
- PLY (Python Lex-Yacc) 3.3+, http://www.dabeaz.com/ply/.
- XMOS tools (4.4.2+): xcc, xas, xsim, xobjdump and xrun.

------
Issues
------

Issues may be submitted via the Issues tab in this github repository. Response to any
issues submitted as at the discretion of the maintainer for this line.
