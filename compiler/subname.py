# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import sys
import collections
from ast import NodeVisitor
import ast

class SubName(NodeVisitor):
  """ 
  Substitute a named value with an expression.
  """
  def __init__(self, name, expr):
    self.name = name
    self.expr = expr

  def replace(self, elem):
    if isinstance(elem, ast.ElemId) and elem.name == self.name:
      return ast.ElemGroup(expr)
    else: 
      return elem

  # Statements containing elements ======================

  def visit_stmt_ass(self, node):
    node.left = self.replace(node.left)

  def visit_stmt_in(self, node):
    node.left = self.replace(node.left)

  def visit_stmt_out(self, node):
    node.left = self.replace(node.left)

  def visit_stmt_alias(self, node):
    node.left = self.replace(node.left)

  def visit_stmt_connect(self, node):
    node.left = self.replace(node.left)

  # Expressions containing elements =====================

  def visit_expr_single(self, node):
    node.elem = self.replace(node.elem)

  def visit_expr_unary(self, node):
    node.elem = self.replace(node.elem)

  def visit_expr_binop(self, node):
    node.elem = self.replace(node.elem)
 
