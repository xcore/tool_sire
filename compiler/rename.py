# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import sys
import collections
from ast import NodeVisitor
import ast

class Rename(NodeVisitor):
  """ 
  Rename an identifier 'old' with 'new' and if a symbol is supplied, replace
  that as well.
  """
  def __init__(self, old, new, symbol=None):
    self.old = old
    self.new = new
    self.symbol = symbol

  def rename(self, elem):
    if hasattr(elem, 'name') and elem.name == self.old:
      elem.name = self.new
      if self.symbol != None:
        elem.symbol = self.symbol
    return elem

  # Statements containing elements ======================

  def visit_stmt_ass(self, node):
    node.left = self.rename(node.left)

  def visit_stmt_in(self, node):
    node.left = self.rename(node.left)

  def visit_stmt_out(self, node):
    node.left = self.rename(node.left)

  def visit_stmt_alias(self, node):
    node.left = self.rename(node.left)
    node.slice = self.rename(node.slice)

  def visit_stmt_connect(self, node):
    node.left = self.rename(node.left)

  def visit_stmt_for(self, node):
    node.index = self.rename(node.index)

  def visit_stmt_rep(self, node):
    node.indices = [self.rename(x) for x in node.indices]

  # Expressions containing elements =====================

  def visit_expr_single(self, node):
    node.elem = self.rename(node.elem)

  def visit_expr_unary(self, node):
    node.elem = self.rename(node.elem)

  def visit_expr_binop(self, node):
    node.elem = self.rename(node.elem)
 
