# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class RemoveDecls(NodeWalker):
  """
  Remove any unused local declarations from procedures.
  """
  def __init__(self):
    pass

  def remove(self, s, decls):
    new = []
    for x in decls:
      if x.name in s:
        new.append(x)
    return new

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    s = self.stmt(node.stmt)
  
  # Statements ==========================================

  # New scopes

  def stmt_seq(self, node):
    s = set()
    [s.update(self.stmt(x)) for x in node.stmt]
    node.decls = self.remove(s, node.decls)
    return s

  def stmt_par(self, node):
    s = set()
    [s.update(self.stmt(x)) for x in node.stmt]
    node.decls = self.remove(s, node.decls)
    return s

  def stmt_server(self, node):
    s = self.stmt(node.server)
    s |= self.stmt(node.client)
    node.decls = self.remove(s, node.decls)
    return s

  # No new scope
  
  def stmt_skip(self, node):
    return set()

  def stmt_pcall(self, node):
    s = set()
    [s.update(self.expr(x)) for x in node.args]
    return s

  def stmt_ass(self, node):
    s = self.elem(node.left)
    return s | self.expr(node.expr)

  def stmt_in(self, node):
    s = self.elem(node.left)
    return s | self.expr(node.expr)

  def stmt_out(self, node):
    s = self.elem(node.left)
    return s | self.expr(node.expr)

  def stmt_alias(self, node):
    return self.expr(node.slice)

  def stmt_connect(self, node):
    s = self.elem(node.left)
    s = self.expr(node.id)
    return s | self.expr(node.expr)

  def stmt_if(self, node):
    s = self.expr(node.cond)
    s |= self.stmt(node.thenstmt)
    return s | self.stmt(node.elsestmt)

  def stmt_while(self, node):
    s = self.expr(node.cond)
    return s | self.stmt(node.stmt)

  def stmt_for(self, node):
    s = self.elem(node.index)
    return s | self.stmt(node.stmt)

  def stmt_rep(self, node):
    s = set()
    [s.update(self.elem(x)) for x in node.indices]
    return s | self.stmt(node.stmt)
    
  def stmt_on(self, node):
    s = self.expr(node.expr)
    return s | self.stmt(node.stmt)

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
    s = self.elem(node.elem)
    return s | self.expr(node.right)
  
  # Elements= ===========================================

  def elem_id(self, node):
    return set([node.name])

  def elem_sub(self, node):
    return set([node.name]) | self.expr(node.expr)

  def elem_slice(self, node):
    s = self.expr(node.base)
    return set([node.name]) | s | self.expr(node.count)

  def elem_index_range(self, node):
    s = self.expr(node.base)
    return set([node.name]) | s | self.expr(node.count)

  def elem_group(self, node):
    return self.expr(node.expr)

  def elem_pcall(self, node):
    s = set()
    [s.update(self.expr(x)) for x in node.args]
    return s

  def elem_fcall(self, node):
    s = set()
    [s.update(self.expr(x)) for x in node.args]
    return s

  def elem_number(self, node):
    return set()

  def elem_boolean(self, node):
    return set()

  def elem_string(self, node):
    return set()

  def elem_char(self, node):
    return set()

