# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce
from math import floor
from symboltab import Symbol
from typedefs import *
import ast

def indices_value(indices, values):
  """
  Given a set of indices and values for them, compute the combined value.
  """
  assert len(indices) == len(values)
  mult = reduce(lambda x, y: x*y.count_value, indices, 1)
  r = 0
  for (x, y) in zip(indices, values):
    mult = floor(mult / x.count_value)
    r += y * mult
  return r

def indices_expr(indices):
  """
  Given a set of indices, return an expression computing their combined value.
  """
  dims = [x.count_value for x in indices]
  r = None
  for (i, x) in enumerate(indices):
    c = reduce(lambda x, y: x*y, dims[i+1:], 1)
    c_expr = ast.ExprSingle(ast.ElemNumber(c))
    eid = ast.ElemId(x.name)
    eid.symbol = Symbol(x.name, T_VAL_SINGLE, None, scope=T_SCOPE_PROC)
    e = ast.ExprBinop('*', eid, c_expr) if c>1 else ast.ExprSingle(eid)
    r = e if r==None else ast.ExprBinop('+', ast.ElemGroup(r), e)
  return r

