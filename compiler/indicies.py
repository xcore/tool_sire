# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce
from math import floor
from symbol import Symbol
from typedefs import *
import ast

def indicies_value(indicies, values):
  """
  Given a set of indicies and values for them, compute the combined value.
  """
  assert len(indicies) == len(values)
  mult = reduce(lambda x, y: x*y.count_value, indicies, 1)
  r = 0
  for (x, y) in zip(indicies, values):
    mult = floor(mult / x.count_value)
    r += y * mult
  return r

def indicies_expr(indicies):
  """
  Given a set of indicies, return an expression computing their combined value.
  """
  dims = [x.count_value for x in indicies]
  r = None
  for (i, x) in enumerate(indicies):
    c = reduce(lambda x, y: x*y, dims[i+1:], 1)
    c_expr = ast.ExprSingle(ast.ElemNumber(c))
    eid = ast.ElemId(x.name)
    eid.symbol = Symbol(x.name, T_VAL_SINGLE, None, scope=T_SCOPE_PROC)
    e = ast.ExprBinop('*', eid, c_expr) if c>1 else ast.ExprSingle(eid)
    r = e if r==None else ast.ExprBinop('+', ast.ElemGroup(r), e)
  return r

