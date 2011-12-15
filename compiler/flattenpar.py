# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker

class FlattenPar(NodeWalker):
  """
  An AST walker to flatten nested parallel compositions.
  """
  def __init__(self):
    pass

  # Program ============================================

  def walk_program(self, node):
    [self.stmt(x.stmt) for x in node.defs]
  
  # Statements ==========================================

  def stmt_par(self, node):
    # NOTE: Can't just flatten nested parallel compostions because of nested 
    # variable scoping.
    stmts = []
    for x in node.stmt:
      self.stmt(x)
      if isinstance(x, ast.StmtPar):
        decls.extend(x.decls)
        stmts.extend(x.stmt)
      else:
        stmts.append(x)
    node.decls = decls
    node.stmt = stmts

  def stmt_seq(self, node):
    [self.stmt(x) for x in node.stmt]

  def stmt_server(self, node):
    self.stmt(node.server)
    self.stmt(node.client)
  
  def stmt_if(self, node):
    self.stmt(node.thenstmt)
    self.stmt(node.elsestmt)

  def stmt_while(self, node):
    self.stmt(node.stmt)

  def stmt_for(self, node):
    self.stmt(node.stmt)

  def stmt_rep(self, node):
    self.stmt(node.stmt)

  def stmt_on(self, node):
    self.stmt(node.stmt)
  
  def stmt_pcall(self, node):
    pass

  def stmt_ass(self, node):
    pass

  def stmt_in(self, node):
    pass

  def stmt_out(self, node):
    pass

  def stmt_alias(self, node):
    pass

  def stmt_connect(self, node):
    pass

  def stmt_assert(self, node):
    pass

  def stmt_return(self, node):
    pass

  def stmt_skip(self, node):
    pass

