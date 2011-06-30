# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from definitions import SYS_NUM_CORES_CONST
import ast

# This function is used by transformation of parallel replicators
# (transformrep) and connection insertion (insertconns) to obtain an expression
# for the location of a target processor.

def form_location(sym, base, offset, compression):
  """
  Given the base id (ElemId), offset (Expr) and compression ratio (integer),
  produce an expression for a location::

    location = (base + (off/comp)) rem NUM_CORES
  """
  assert isinstance(base, ast.ElemId)
  assert isinstance(offset, ast.Expr)

  # Offset
  loc = offset

  # Apply compression
  if compression > 1:
    loc = ast.ExprBinop('/', ast.ElemGroup(loc),
        ast.ExprSingle(ast.ElemNumber(compression)))
  
  elem_numcores = ast.ElemId(SYS_NUM_CORES_CONST)
  elem_numcores.symbol = sym.lookup(SYS_NUM_CORES_CONST) 

  # Apply 'rem NUM_CORES' to base + (off/comp)
  loc = ast.ExprBinop('rem',
      ast.ElemGroup(ast.ExprBinop('+', base,
        ast.ExprSingle(ast.ElemGroup(loc)))),
        ast.ExprSingle(elem_numcores))

  return loc

