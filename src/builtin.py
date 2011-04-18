# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from ast import Def, Formals, Param
from type import Type

printchar = Def(
        'printchar', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printcharln = Def(
        'printcharln', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printval = Def(
        'printval', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printvalln = Def(
        'printvalln',
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printhex = Def(
        'printhex', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printhexln = Def(
        'printhexln',
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'), None)]),
        None, None)

printstr = Def(
        'printstr', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'), None)]),
        None, None)

printstrln = Def(
        'printstrln', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'), None)]),
        None, None)

println = Def(
        'println', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'), None)]),
        None, None)

#exit = Def(
#        'exit', 
#        Type('proc', 'procedure'), 
#        Formals([Param('v', Type('val', 'single'), None)]),
#        None, None)

functions = (
  printchar,
  printcharln,
  printval,
  printvalln,
  printhex,
  printhexln,
  printstr,
  printstrln,
  println,
  )

# Must relate to the above list
names = (
  'printchar',
  'printcharln',
  'printval',
  'printvalln',
  'printhex',
  'printhexln',
  'printstr',
  'printstrln',
  'println',
  )

# Runtime functions available to programs. Ordering matches jump and size tables.
runtime_functions = [ 
  '_migrate',
  '_setupthread',
  ]
