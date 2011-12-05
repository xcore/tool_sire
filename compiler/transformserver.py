# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker

class TransformServer(NodeWalker):
  """
  An AST walker to flatten nested parallel compositions.
  """
  def __init__(self):
    pass

  def transform(self, stmt):
    # Flatten server of client parallel compositions into the server
    # composition
    if isinstance(stmt, ast.StmtServer):
      l = []
      if isinstance(stmt.server, ast.StmtPar):
        l.extend(stmt.server.stmt)
      else:
        l.append(stmt.server)
      if isinstance(stmt.client, ast.StmtPar):
        l.extend(stmt.client.stmt)
      else:
        l.append(stmt.client)
      return ast.StmtPar([], l)
    return stmt

  # Program ============================================

  def walk_program(self, node):
    [self.stmt(x.stmt) for x in node.defs]
  
  # Statements containing statements ===================

  def stmt_par(self, node):
    # Flatten a server into parallel composition
    stmts = []
    for x in node.stmt:
      self.stmt(x)
      s = self.transform(x)
      if isinstance(s, ast.StmtPar):
        stmts.extend(s.stmt)
      else:
        stmts.append(x)
    node.stmt = stmts

  def stmt_seq(self, node):
    for (i, x) in enumerate(node.stmt):
      self.stmt(x)
      node.stmt[i] = self.transform(x)

  def stmt_server(self, node):
    self.stmt(node.server)
    self.stmt(node.client)
    node.server = self.transform(node.server)
    node.client = self.transform(node.client)
  
  def stmt_if(self, node):
    self.stmt(node.thenstmt)
    self.stmt(node.elsestmt)
    node.thenstmt = self.transform(node.thenstmt)
    node.elsestmt = self.transform(node.elsestmt)

  def stmt_while(self, node):
    self.stmt(node.stmt)
    node.stmt = self.transform(node.stmt)

  def stmt_for(self, node):
    self.stmt(node.stmt)
    node.stmt = self.transform(node.stmt)

  def stmt_rep(self, node):
    self.stmt(node.stmt)
    node.stmt = self.transform(node.stmt)

  def stmt_on(self, node):
    self.stmt(node.stmt)
    node.stmt = self.transform(node.stmt)
 
  # Statements not containing statements

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

