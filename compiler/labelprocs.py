# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce
import definitions as defs
import ast
from walker import NodeWalker
from evalexpr import EvalExpr
from printer import Printer

class LabelProcs(NodeWalker):
  """
  Label each statement with its offset relative to the location of the scope.
  """
  def __init__(self, sym, device):
    self.sym = sym
    self.device = device

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    node.location = ast.ElemNumber(0) 
    if node.name == 'main':
      self.stmt(node.stmt, ast.ExprSingle(node.location))
    else:
      self.stmt(node.stmt, ast.ExprSingle(node.location))
  
  # Statements ==========================================

  # Contain processes with new offsets

  def stmt_rep(self, node, l):
    node.location = l
    
    # Calculate total # processes (m) and the next power of two of this (n)
    node.m = reduce(lambda x, y: x*y.count_value, node.indicies, 1)
 
    # Calculate the compression factor
    node.f = 1
    while node.m/node.f > self.device.num_cores():
      node.f = node.f + 1
    
    # Determine f and then set l = g(d_1, d_2, ..., d_k, f)
    dims = [x.count_value for x in node.indicies]
    k = None
    for (i, x) in enumerate(node.indicies):
      c = reduce(lambda x, y: x*y, dims[i+1:], 1)
      e = (ast.ElemGroup(
            ast.ExprBinop('*', ast.ElemId(x.name),
              ast.ExprSingle(ast.ElemNumber(c)))) 
              if c>1 else ast.ElemId(x.name))
      k = ast.ExprSingle(e) if k==None else ast.ExprBinop('+', k, ast.ExprSingle(e))
    
    # Apply f
    k = (ast.ExprSingle(ast.ElemGroup(ast.ExprBinop('/', 
          ast.ElemGroup(k), ast.ExprSingle(ast.ElemNumber(node.f)))))
            if node.f>1 else k)
    
    # Add to base (if non-zero) and take modulo
    if isinstance(l, ast.ElemNumber) and l.value==0:
      pass
    else:
      k = ast.ExprBinop('+', l, k)
      #k = ast.ExprBinop('rem', ast.ElemGroup(ast.ExprBinop('+', l, k)), 
      #    ast.ExprSingle(elem_numcores))

    assert not k==None
    self.stmt(node.stmt, k)
    
  def stmt_on(self, node, l):
    node.location = l
    k = ast.ExprBinop('+', ast.ElemGroup(l), node.expr)
    # Try and evaluate this new expression
    v = EvalExpr().expr(k)
    k = ast.ExprSingle(ast.ElemNumber(v)) if v != None else k
    self.stmt(node.stmt, k)

  # Contain local processes

  def stmt_seq(self, node, l):
    node.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_par(self, node, l):
    node.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_if(self, node, l):
    node.location = l
    self.stmt(node.thenstmt, l)
    self.stmt(node.elsestmt, l)

  def stmt_while(self, node, l):
    node.location = l
    self.stmt(node.stmt, l)

  def stmt_for(self, node, l):
    node.location = l
    self.stmt(node.stmt, l)

  # Statements
  
  def stmt_skip(self, node, l):
    node.location = l

  def stmt_pcall(self, node, l):
    node.location = l

  def stmt_ass(self, node, l):
    node.location = l

  def stmt_in(self, node, l):
    node.location = l

  def stmt_out(self, node, l):
    node.location = l

  def stmt_alias(self, node, l):
    node.location = l

  def stmt_connect(self, node, l):
    node.location = l

  def stmt_assert(self, node, l):
    node.location = l
  
  def stmt_return(self, node, l):
    node.location = l
  
