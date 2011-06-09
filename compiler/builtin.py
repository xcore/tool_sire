# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

# This module defines processes and functions which are built-in to the
# language. Those marked as mobile will be added to the jump table and will be
# executable remotely.

from ast import Def, Param
from typedefs import * 

SVAL_PARAM = Param('v', T_VAL_SINGLE, None) 
AVAL_PARAM = Param('v', T_REF_ARRAY, None) 

class Builtin(object):
  """
  A class to represent a builtin and its mobility.
  """
  def __init__(self, definition, mobile):
    self.definition = definition
    self.mobile = mobile

# Create a process declaration (prototype).
def proc_decl(name, params, mobile=False):
  return Builtin(Def(name, T_PROC, params, None, None), mobile)

# Create a function declaration (prototype).
def func_decl(name, params, mobile=False):
  return Builtin(Def(name, T_FUNC, params, None, None), mobile)

# Printing builtins
printchar   = proc_decl('printchar',   [SVAL_PARAM])
printcharln = proc_decl('printcharln', [SVAL_PARAM])
printval    = proc_decl('printval',    [SVAL_PARAM])
printvalln  = proc_decl('printvalln',  [SVAL_PARAM])
printhex    = proc_decl('printhex',    [SVAL_PARAM])
printhexln  = proc_decl('printhexln',  [SVAL_PARAM])
printstr    = proc_decl('printstr',    [AVAL_PARAM])
printstrln  = proc_decl('printstrln',  [AVAL_PARAM])
println     = proc_decl('println',     [])

# Fixed point builtins
mulf8_24 = func_decl('mulf8_24', [SVAL_PARAM, SVAL_PARAM], mobile=True)
divf8_24 = func_decl('divf8_24', [SVAL_PARAM, SVAL_PARAM], mobile=True)

procid = func_decl('procid', [], mobile=True)

builtins = {
  'printchar'   : printchar,
  'printcharln' : printcharln,
  'printval'    : printval,
  'printvalln'  : printvalln,
  'printhex'    : printhex,
  'printhexln'  : printhexln,
  'printstr'    : printstr,
  'printstrln'  : printstrln,
  'println'     : println,
  'mulf8_24'    : mulf8_24,
  'divf8_24'    : divf8_24,
  'procid'      : procid,
  }

# Runtime functions available to programs. Ordering matches jump and size tables.
runtime_functions = [ 
  '_migrate',
  '_setupthread',
  ]
