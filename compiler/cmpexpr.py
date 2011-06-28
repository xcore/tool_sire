# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker
import ast

class CmpExpr(NodeWalker):
  """
  Compare two expressions for equality.
  """
  def __init__(self):
    pass

  # Expressions =========================================

  def expr_single(self, node, expr):
    return (isinstance(expr, type(node))
        and self.elem(node.elem, expr.elem))

  def expr_unary(self, node, expr):
    return (isinstance(expr, type(node))
        and (node.op == expr.op
        and self.elem(node.elem, expr.elem)))

  def expr_binop(self, node, expr):
    return (isinstance(expr, type(node))
        and node.op == expr.op
        and self.elem(node.elem, expr.elem) 
        and self.expr(node.right, expr.right))
  
  # Elements= ===========================================

  def elem_group(self, node, expr):
    return (isinstance(expr, type(node))
        and self.expr(node.expr, expr.expr))

  def elem_id(self, node, expr):
    return (isinstance(expr, type(node))
        and node.name == expr.name)
    
  def elem_sub(self, node, expr):
    return (isinstance(expr, type(node))
        and node.name == expr.name 
        and self.expr(node.expr, expr.expr))

  def elem_slice(self, node, expr):
    return (isinstance(expr, type(node))
        and node.name == expr.name 
        and self.expr(node.base, expr.base)
        and self.expr(node.count, expr.count))

  def elem_index_range(self, node, expr):
    return (isinstance(expr, type(node))
        and node.name == expr.name 
        and self.expr(node.base, expr.base)
        and self.expr(node.count, expr.count))

  def elem_fcall(self, node, expr):
    return (isinstance(expr, type(node))
        and node.name == expr.name 
        and len(node.args) == len(expr.args) 
        and all([self.expr(x, y) for x, y in zip(node.args, expr.args)]))

  def elem_number(self, node, expr):
    return (isinstance(expr, type(node))
        and node.value == expr.value)

  def elem_boolean(self, node, expr):
    return (isinstance(expr, type(node))
        and node.value == expr.value)

  def elem_string(self, node, expr):
    return (isinstance(expr, type(node))
        and node.value == expr.value)

  def elem_char(self, node, expr):
    return (isinstance(expr, type(node)) 
        and node.value == expr.value)

