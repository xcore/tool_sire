sire
....

:Stable release: Unreleased
:Status: Experimental/ongoing
:Maintainer: http://github.com/jameshanlon
:Description: A language and runtime system for dynamic process creation on the XMOS XS1 architecture

sire is a small block-structured, imperative language with features to
demonstate a mechanism for distributed and dynamic creation of processes in and
over a parallel system. It targets the XMOS XS1 architecture, which is
general-purpose and has low-level support for concurrency and parallelism.

Key features
============

- Complete compiler
- Translation of sire program code to XC/assembly source.
- Construction of special multi-core binary replicating only the runtime kernel.

To do
=====

- See TODO.rst

Known issues
============

- See TODO.rst

Dependencies
============

- Python 3.2 or 3.1 with the argparse module avilable as 'python' on the command line.
- PLY (Python Lex-Yacc) 3.3+, http://www.dabeaz.com/ply/.
- XMOS tools (4.4.2+): xcc, xas, xsim, xobjdump and xrun.

Installation
============

Ensure the above dependencies are satisfied and add SIRE_INSTALL_PATH to your
environment and PATH::

  export SIRE_INSTALL_PATH=/home/jamie/sire
  PATH=$SIRE_INSTALL_PATH:$PATH

Getting started
===============

Compile and run 'hello world'::

  $ echo 'proc main() is printstrln("hello world")' | sire
  $ xsim a.xe
  hello world

Issues
======

Issues may be submitted via the Issues tab in this github repository. Response to any
issues submitted as at the discretion of the maintainer for this line.
