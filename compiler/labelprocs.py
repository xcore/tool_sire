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
from indices import indices_expr

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
    node.m = reduce(lambda x, y: x*y.count_value, node.indices, 1)
 
    # Determine f and then set l = g(d_1, d_2, ..., d_k, f)
    k = indices_expr(node.indices)
    
    # Add to base (if non-zero) and take modulo
    if not (isinstance(l, ast.ElemNumber) and l.value==0):
      k = ast.ExprBinop('+', l, k)

    self.stmt(node.stmt, k)
    
  def stmt_on(self, node, l):
    node.location = l
    # Try and evaluate this 'target' expression
    v = EvalExpr().expr(node.expr)
    k = ast.ExprSingle(ast.ElemNumber(v)) if v != None else l
    self.stmt(node.stmt, k)

  # Statements containing statements

  def stmt_seq(self, node, l):
    node.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_par(self, node, l):
    node.location = l
    [self.stmt(x, l) for x in node.stmt]

  def stmt_server(self, node, l):
    node.location = l
    self.stmt(node.server, l)
    self.stmt(node.client, l)
  
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

  def stmt_in_tag(self, node, l):
    node.location = l

  def stmt_out_tag(self, node, l):
    node.location = l

  def stmt_alias(self, node, l):
    node.location = l

  def stmt_connect(self, node, l):
    node.location = l

  def stmt_assert(self, node, l):
    node.location = l
  
  def stmt_return(self, node, l):
    node.location = l
  
