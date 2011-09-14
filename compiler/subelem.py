# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from ast import NodeVisitor

class SubElem(NodeVisitor):
  """
  Am AST walker to replace a particular element. Replace all instances of
  'old' element with 'new' element in the list of arguments. Elements are
  replaced by name.
  """
  def __init__(self, old, new):
    self.old = old
    self.new = new
    #print('Replacing: {}, with {}'.format(old, new))

  def substitute(self, elem):
    if (isinstance(elem, type(self.old)) 
        and elem.name == self.old.name):
      return self.new
    else:
      return elem

  # Statements containing elements ======================

  def visit_stmt_ass(self, node):
    node.left = self.substitute(node.left)

  def visit_stmt_in(self, node):
    node.left = self.substitute(node.left)

  def visit_stmt_out(self, node):
    node.left = self.substitute(node.left)

  def visit_stmt_alias(self, node):
    node.left = self.substitute(node.left)

  def visit_stmt_connect(self, node):
    node.left = self.substitute(node.left)

  # Expressions containing elements =====================

  def visit_expr_single(self, node):
    node.elem = self.substitute(node.elem)

  def visit_expr_unary(self, node):
    node.elem = self.substitute(node.elem)

  def visit_expr_binop(self, node):
    node.elem = self.substitute(node.elem)

