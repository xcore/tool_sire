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
    eid = ast.ElemId(x.name)
    eid.symbol = Symbol(x.name, T_VAL_SINGLE, None, scope=T_SCOPE_PROC)
    e = (ast.ElemGroup(ast.ExprBinop('*', eid, 
        ast.ExprSingle(ast.ElemNumber(c))))
            if c>1 else eid)
    r = (ast.ElemGroup(ast.ExprSingle(e)) if r==None 
        else ast.ExprBinop('+', r, ast.ExprSingle(e)))
  return r

