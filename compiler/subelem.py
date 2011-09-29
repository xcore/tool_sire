# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from ast import NodeVisitor

class SubElem(NodeVisitor):
  """
  Am AST walker to replace a particular element. Replace all instances of
  'old' element with 'new' element or expression in the list of arguments.
  Elements are replaced by name.
  """
  def __init__(self, old, new):
    self.old = old
    self.new = new
    #print('Replacing: {}, with {}'.format(old, new))

  def substitute(self, elem):
    
    # If we've found a match
    if (isinstance(elem, type(self.old)) and elem.name == self.old.name):
          
      # If new is an ExprSingle replace the element from it
      if isinstance(self.new, ast.ExprSingle):
        return self.new.elem

      # If the replacement is any other expression then group it
      elif isinstance(self.new, ast.Expr):
        return ast.ElemGroup(self.new)

      # Otherwise it is an element and we replace directly
      else:
        assert isinstance(self.new, ast.Elem)
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

