# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from walker import NodeWalker
from typedefs import *
from symboltab import Symbol
import ast

class InsertIds(NodeWalker):
  """
  Insert assignment of procid() builtin for replicators.
  """
  def __init__(self):
    pass

  def insert(self, stmt):
    
    # Create the assignment
    e = ast.ElemId(PROC_ID_VAR)
    e.symbol = Symbol(PROC_ID_VAR, T_VAR_SINGLE, None, T_SCOPE_PROC)
    s = ast.StmtAss(e, ast.ExprSingle(ast.ElemFcall('procid', [])))

    # Add the assignent in sequence with the existing body process
    #if isinstance(node.stmt, ast.StmtSeq):
    #  node.stmt.stmt.insert(0, s)
    #else:
    return ast.StmtSeq([s, stmt])

  # Program ============================================

  def walk_program(self, node):
    for x in node.defs:
      # Add a declaration for the variable
      if self.stmt(x.stmt):
        x.decls.append(ast.Decl(PROC_ID_VAR, T_VAR_SINGLE, None))
  
  # Statements ==========================================

  # Statements potentially containing replicators

  def stmt_rep(self, node):
    b = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      node.stmt = self.insert(node.stmt)
      b = True
    return b
    
  def stmt_seq(self, node):
    b = any([self.stmt(x) for x in node.stmt])
    for x in node.stmt:
      if isinstance(node.stmt, ast.StmtRep):
        node.stmt = self.insert(node.stmt)
        b = True
    return b

  def stmt_par(self, node):
    b = any([self.stmt(x) for x in node.stmt])
    for x in node.stmt:
      if isinstance(node.stmt, ast.StmtRep):
        node.stmt = self.insert(node.stmt)
        b = True
    return b

  def stmt_if(self, node):
    b = self.stmt(node.thenstmt) or self.stmt(node.elsestmt)
    if isinstance(node.thenstmt, ast.StmtRep):
      node.thenstmt = self.insert(node.thenstmt)
      b = True
    if isinstance(node.elsestmt, ast.StmtRep):
      node.elsestmt = self.insert(node.elsestmt)
      b = True
    return b

  def stmt_while(self, node):
    b = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      node.stmt = self.insert(node.stmt)
      b = True
    return b

  def stmt_for(self, node):
    b = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      node.stmt = self.insert(node.stmt)
      b = True
    return b

  def stmt_on(self, node):
    b = self.stmt(node.stmt)
    if isinstance(node.stmt, ast.StmtRep):
      node.stmt = self.insert(node.stmt)
      b = True
    return b

  # Statements not containing statements

  def stmt_return(self, node):
    return False
  
  def stmt_skip(self, node):
    return False

  def stmt_pcall(self, node):
    return False

  def stmt_ass(self, node):
    return False

  def stmt_in(self, node):
    return False

  def stmt_out(self, node):
    return False

  def stmt_in_tag(self, node):
    return False

  def stmt_out_tag(self, node):
    return False

  def stmt_alias(self, node):
    return False

  def stmt_connect(self, node):
    return False
  
  def stmt_assert(self, node):
    return False
  

