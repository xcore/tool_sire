# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker

class TemplateWalker(NodeWalker):
  """
  A template recursive descent AST NodeWalker.
  """
  def __init__(self):
    pass

  # Program ============================================

  def walk_program(self, node):
    [self.decl(x) for x in node.decls]
    [self.defn(x) for x in node.defs]
  
  # Variable declarations ===============================

  def decl(self, node):
    self.expr(node.expr)

  # Procedure definitions ===============================

  def defn(self, node):
    [self.param(x) for x in node.params]
    [self.decl(x) for x in node.decls]
    self.stmt(node.stmt)
  
  # Formals =============================================
  
  def param(self, node):
    self.expr(node.expr)

  # Statements ==========================================

  def stmt_seq(self, node):
    [self.stmt(x) for x in node.stmt]

  def stmt_par(self, node):
    [self.stmt(x) for x in node.stmt]

  def stmt_server(self, node):
    [self.decl(x) for x in node.decls]
    self.stmt(node.server)
    self.stmt(node.client)

  def stmt_skip(self, node):
    pass

  def stmt_pcall(self, node):
    [self.expr(x) for x in node.args]

  def stmt_ass(self, node):
    self.elem(node.left)
    self.expr(node.expr)

  def stmt_in(self, node):
    self.elem(node.left)
    self.expr(node.expr)

  def stmt_out(self, node):
    self.elem(node.left)
    self.expr(node.expr)

  def stmt_in_tag(self, node):
    self.elem(node.left)
    self.expr(node.expr)

  def stmt_out_tag(self, node):
    self.elem(node.left)
    self.expr(node.expr)

  def stmt_alias(self, node):
    self.expr(node.slice)

  def stmt_connect(self, node):
    self.elem(node.left)
    self.expr(node.id)
    self.elem(node.core)

  def stmt_if(self, node):
    self.expr(node.cond)
    self.stmt(node.thenstmt)
    self.stmt(node.elsestmt)

  def stmt_while(self, node):
    self.expr(node.cond)
    self.stmt(node.stmt)

  def stmt_for(self, node):
    self.elem(node.index)
    self.stmt(node.stmt)

  def stmt_rep(self, node):
    [self.elem(x) for x in node.indices]
    self.stmt(node.stmt)
    
  def stmt_on(self, node):
    self.expr(node.expr)
    self.stmt(node.stmt)

  def stmt_assert(self, node):
    self.expr(node.expr)

  def stmt_return(self, node):
    self.expr(node.expr)

  # Expressions =========================================

  def expr_single(self, node):
    self.elem(node.elem)

  def expr_unary(self, node):
    self.elem(node.elem)

  def expr_binop(self, node):
    self.elem(node.elem)
    self.expr(node.right)
  
  # Elements= ===========================================

  def elem_group(self, node):
    self.expr(node.expr)

  def elem_id(self, node):
    pass

  def elem_sub(self, node):
    self.expr(node.expr)

  def elem_slice(self, node):
    self.expr(node.base)
    self.expr(node.count)

  def elem_index_range(self, node):
    self.expr(node.base)
    self.expr(node.count)

  def elem_pcall(self, node):
    [self.expr(x) for x in node.args]

  def elem_fcall(self, node):
    [self.expr(x) for x in node.args]

  def elem_number(self, node):
    pass

  def elem_boolean(self, node):
    pass

  def elem_string(self, node):
    pass

  def elem_char(self, node):
    pass
  

