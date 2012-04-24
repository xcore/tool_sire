# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

# This module defines processes and functions which are built-in to the
# language. Those marked as mobile will be added to the jump table and will be
# executable remotely.

from ast import ProcDef, Param
from typedefs import * 

SVAL_PARAM = Param('v', T_VAL_SINGLE, None) 
SREF_PARAM = Param('v', T_REF_SINGLE, None) 
AVAL_PARAM = Param('v', T_REF_ARRAY, None) 
CHANEND_PARAM = Param('v', T_CHANEND_SINGLE, None) 

class Builtin(object):
  """
  A class to represent a builtin and its mobility.
  """
  def __init__(self, definition, mobile):
    self.definition = definition
    self.mobile = mobile

# Create a process declaration (prototype).
def proc_decl(name, params, mobile=False):
  return Builtin(ProcDef(name, T_PROC, params, None, None), mobile)

# Create a function declaration (prototype).
def func_decl(name, params, mobile=False):
  return Builtin(ProcDef(name, T_FUNC, params, None, None), mobile)

# Builtin definitions

# Printing
printchar   = proc_decl('printchar',   [SVAL_PARAM])
printcharln = proc_decl('printcharln', [SVAL_PARAM])
printval    = proc_decl('printval',    [SVAL_PARAM])
printvalln  = proc_decl('printvalln',  [SVAL_PARAM])
printhex    = proc_decl('printhex',    [SVAL_PARAM])
printhexln  = proc_decl('printhexln',  [SVAL_PARAM])
printstr    = proc_decl('printstr',    [AVAL_PARAM])
printstrln  = proc_decl('printstrln',  [AVAL_PARAM])
println     = proc_decl('println',     [])

# File IO
fopen       = proc_decl('fopen',   [AVAL_PARAM, SVAL_PARAM])
fwrite      = proc_decl('fwrite',  [SVAL_PARAM, SVAL_PARAM])
fread       = proc_decl('fread',   [SVAL_PARAM, SREF_PARAM])
fclose      = proc_decl('fclose',  [SVAL_PARAM])

# Communication
inp        = proc_decl('inp',      [CHANEND_PARAM, SREF_PARAM])
out        = proc_decl('out',      [CHANEND_PARAM, SVAL_PARAM])
inct       = proc_decl('inct',     [CHANEND_PARAM, SREF_PARAM])
outct      = proc_decl('outct',    [CHANEND_PARAM, SVAL_PARAM])
chkctend   = proc_decl('chkctend', [CHANEND_PARAM])
outctend   = proc_decl('outctend', [CHANEND_PARAM])

# Remote memory access
rread      = proc_decl('rread',    [SVAL_PARAM, SVAL_PARAM, SREF_PARAM])
rwrite     = proc_decl('rwrite',   [SVAL_PARAM, SVAL_PARAM, SVAL_PARAM])

# Fixed point
mulf8_24   = func_decl('mulf8_24', [SVAL_PARAM, SVAL_PARAM], mobile=True)
divf8_24   = func_decl('divf8_24', [SVAL_PARAM, SVAL_PARAM], mobile=True)

# System
procid     = func_decl('procid',   []) # Required for implementation of on and connect
time       = func_decl('time',     [])
crc        = func_decl('crc',      [SVAL_PARAM], mobile=True)
rand       = func_decl('rand',     [], mobile=True)
memalloc   = func_decl('memalloc', [AVAL_PARAM, SVAL_PARAM])
memfree    = func_decl('memfree',  [AVAL_PARAM])

#livermore loops
livermore1 = proc_decl('livermore1', [CHANEND_PARAM, SVAL_PARAM, SVAL_PARAM]) 
livermore2 = proc_decl('livermore2', [CHANEND_PARAM, SVAL_PARAM, SVAL_PARAM]) 
livermore3 = proc_decl('livermore3', [CHANEND_PARAM, SVAL_PARAM, SVAL_PARAM]) 
livermore4 = proc_decl('livermore4', [CHANEND_PARAM, SVAL_PARAM, SVAL_PARAM])
livermore5 = proc_decl('livermore5', [CHANEND_PARAM, SVAL_PARAM, SVAL_PARAM])

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
  'fopen'       : fopen,
  'fwrite'      : fwrite,
  'fread'       : fread,
  'fclose'      : fclose,
  'inp'         : inp,
  'out'         : out,
  'inct'        : inct,
  'outct'       : outct,
  'chkctend'    : chkctend,
  'outctend'    : outctend,
  'rread'       : rread,
  'rwrite'      : rwrite,
  'mulf8_24'    : mulf8_24,
  'divf8_24'    : divf8_24,
  'procid'      : procid,
  'time'        : time,
  'crc'         : crc,
  'rand'        : rand,
  'memalloc'    : memalloc,
  'memfree'     : memfree,
  'livermore1'  : livermore1,
  'livermore2'  : livermore2,
  'livermore3'  : livermore3,
  'livermore4'  : livermore4,
  'livermore5'  : livermore5,
  }

# Runtime functions available to programs. Ordering matches jump and size tables.
runtime_functions = [ 
  '_createProcess',
  '_procId',
  '_connectMaster',
  '_connectSlave',
  '_connectServer',
  '_connectClient',
  '_memAlloc',
  '_memFree',
  ]

