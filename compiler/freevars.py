# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class FreeVars(NodeWalker):
  """
  Calculate the set of free variables within a statement. This can be:
   - All definitions and uses.
   - All definitions.
   - All uses and definitions of array types only.
  """
  def __init__(self):
    pass

  def allvars(self, node):
    self.collect = 'all'
    return self.stmt(node)

  def defs(self, node):
    self.collect = 'defs'
    return self.stmt(node)

  # Statements ==========================================

  def stmt_seq(self, node):
    c = set()
    [c.update(self.stmt(x)) for x in node.stmt]
    return c

  def stmt_par(self, node):
    c = set()
    [c.update(self.stmt(x)) for x in node.stmt]
    return c

  def stmt_skip(self, node):
    return set()

  def stmt_ass(self, node):
    c = self.elem(node.left)
    c |= self.expr(node.expr)
    return c

  def stmt_in(self, node):
    c = self.elem(node.left)
    c |= self.expr(node.expr)
    return c

  def stmt_out(self, node):
    c = self.elem(node.left)
    c |= self.expr(node.expr)
    return c

  def stmt_alias(self, node):
    c = self.elem(node.left)
    c |= self.elem(node.slice)
    return c

  def stmt_pcall(self, node):
    c = set()
    [c.update(self.expr(x)) for x in node.args]
    return c

  def stmt_if(self, node):
    c = self.expr(node.cond)
    c |= self.stmt(node.thenstmt)
    c |= self.stmt(node.elsestmt)
    return c

  def stmt_while(self, node):
    c = self.expr(node.cond)
    c |= self.stmt(node.stmt)
    return c

  def stmt_for(self, node):
    c = self.elem(node.index)
    c |= self.stmt(node.stmt)
    return c

  def stmt_rep(self, node):
    c = set()
    [c.update(self.elem(x)) for x in node.indicies]
    c |= self.stmt(node.stmt)
    return c

  def stmt_connect(self, node):
    c = self.elem(node.left)
    if node.expr:
      c |= self.expr(node.expr)
    return c

  def stmt_on(self, node):
    c = self.expr(node.expr)
    c |= self.stmt(node.stmt)
    return c

  def stmt_assert(self, node):
    return self.expr(node.expr)
  
  def stmt_return(self, node):
    return self.expr(node.expr)
  
  # Expressions =========================================

  def expr_single(self, node):
    return self.elem(node.elem)

  def expr_unary(self, node):
    return self.elem(node.elem)

  def expr_binop(self, node):
    c = self.elem(node.elem)
    c |= self.expr(node.right)
    return c
  
  # Elements= ===========================================

  # Identifier
  def elem_id(self, node):
    return set([node])

  # Array subscript
  def elem_sub(self, node):
    c = self.expr(node.expr)
    return c | set([node])

  # Array slice
  def elem_slice(self, node):
    c = self.expr(node.base)
    c |= self.expr(node.count)
    return c | set([node])

  # Index
  def elem_index_range(self, node):
    c = self.expr(node.base)
    c |= self.expr(node.count)
    return c | set([node])

  def elem_group(self, node):
    return self.expr(node.expr)

  def elem_fcall(self, node):
    c = set()
    [c.update(self.expr(x)) for x in node.args]
    return c

  def elem_number(self, node):
    return set()

  def elem_boolean(self, node):
    return set()

  def elem_string(self, node):
    return set()

  def elem_char(self, node):
    return set()


