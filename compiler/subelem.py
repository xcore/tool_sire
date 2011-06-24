# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from ast import NodeVisitor

class SubElem(NodeVisitor):
  """
  Am AST walker to replace a particular element. Replace all instances of
  'old' element with 'new' element in the list of arguments. Elements are
  replaced by name.
  """
  def __init__(self, old, new):
    """
    Elements old (name) and new (element).
    """
    self.old = old
    self.new = new
    #print('Replacing: {}, with {}'.format(old, new))

  def visit_expr_single(self, node):
    if isinstance(node.elem, type(self.old)):
      if node.elem.name == self.old.name:
        node.elem = self.new

  def visit_expr_unary(self, node):
    if isinstance(node.elem, type(self.old)):
      if node.elem.name == self.old.name:
        node.elem = self.new

  def visit_expr_binop(self, node):
    if isinstance(node.elem, type(self.old)):
      if node.elem.name == self.old.name:
        node.elem = self.new


