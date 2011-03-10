==========
Using sire
==========

----------------------
Setup and installation
----------------------

Ensure the above dependencies are satisfied and add SIRE_INSTALL_PATH to your
environment and PATH by adding the following to your .bashrc file, for example::

  export SIRE_INSTALL_PATH=/path/to/sire
  PATH=$SIRE_INSTALL_PATH:$PATH

---------------
Getting started
---------------

Compile and run 'hello world'::

  $ echo 'proc main() is printstrln("hello world")' | sire
  $ xsim a.xe
  hello world

