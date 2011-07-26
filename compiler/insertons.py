# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce

from walker import NodeWalker
import ast

class InsertOns(NodeWalker):
  """
  Prefix processes with on in parallel composition to distribute them over a
  system.
  """
  def __init__(self):
    pass

  # Program ============================================

  def walk_program(self, node):
    [self.stmt(x.stmt, 0) for x in node.defs]
  
  # Statements ==========================================

  # Statements containing statements

  def stmt_seq(self, node, d):
    [self.stmt(x, d) for x in node.stmt]
    return d + 1

  def stmt_par(self, node, d):
    d = self.stmt(node.stmt[0], d)
    for (i, x) in enumerate(node.stmt[1:]):
      node.stmt[i+1] = ast.StmtOn(ast.ExprSingle(ast.ElemNumber(d)), x)
      d = self.stmt(x, d)
    return d

  def stmt_rep(self, node, d):
    offset = reduce(lambda x, y: x*y.count_value, node.indicies, 1)
    self.stmt(node.stmt, d)
    return offset
    
  def stmt_on(self, node, d):
    self.stmt(node.stmt, d)
    return d + 1

  def stmt_if(self, node, d):
    self.stmt(node.thenstmt, d)
    self.stmt(node.elsestmt, d)
    return d + 1

  def stmt_while(self, node, d):
    self.stmt(node.stmt, d)
    return d + 1

  def stmt_for(self, node, d):
    self.stmt(node.stmt, d)
    return d + 1

  # Statements not containing statements

  def stmt_ass(self, node, d):
    return d + 1

  def stmt_in(self, node, d):
    return d + 1

  def stmt_out(self, node, d):
    return d + 1

  def stmt_alias(self, node, d):
    return d + 1

  def stmt_connect(self, node, d):
    return d + 1

  def stmt_return(self, node, d):
    return d + 1
  
  def stmt_skip(self, node, d):
    return d + 1

  def stmt_pcall(self, node, d):
    return d + 1

